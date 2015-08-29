import os

os.environ['DJANGO_SETTINGS_MODULE'] = "askpopulo.settings"

import pymysql
import time
import datetime
from django.core.mail import EmailMessage
import sys
import stream
import traceback
from django.core.management import execute_from_command_line

from askpopulo import settings
from login.models import ExtendedUser
from django.contrib.auth.models import User
from django.core.mail import send_mail
client = stream.connect(settings.STREAM_API_KEY, settings.STREAM_API_SECRET)

def sendExpirationNotification():
	try:
		db_dict = settings.DATABASES.get('default')
		db_host = db_dict.get('HOST')
		db_user = db_dict.get('USER')
		db_pass = db_dict.get('PASSWORD')
		db_name = db_dict.get('NAME')
		conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_name)
		
		mailSentPollIdCur = conn.cursor()
		mailSentPollIdCur.execute("SELECT pollid FROM pollexpiry_mail")
		
		expiredPollsCur = conn.cursor()
		expiredPollsCur.execute("SELECT id FROM polls_question WHERE expiry is not null and NOW() > expiry")

		betPollsCur = conn.cursor()
		betPollsCur.execute("SELECT id,winning_choice FROM polls_question WHERE isBet=1 and privatePoll=0 and expiry is not null and NOW() > expiry")

		userToSendCur = conn.cursor()
		questionSlugCur = conn.cursor()
		insertCursor = conn.cursor()
		userToBetCur = conn.cursor()
		userBetVotedCur = conn.cursor()

		mailSentList = []
		expiredPollsList = []
		betPollsList = []
		userToSendList = []
		to_email = ""
		que_slug = ""
		que_text = ""
		que_voter = ""
		que_desc = ""

		for row in mailSentPollIdCur:
			temp = list(row)
			mailSentList.append(temp[0])

		for row in expiredPollsCur:
			temp = list(row)
			expiredPollsList.append(temp[0])

		for row in betPollsCur:
			temp = list(row)
			betPollsList.append(temp)
		
		expiredPollsList = list(set(expiredPollsList) - set([x[0] for x in betPollsList]))
		mailNotSentExpiredPolls = list(set(expiredPollsList) - set(mailSentList))
		# print(betPollsList)
		# print(mailSentList)
		# print(expiredPollsList)
		count = 0
		for bets in betPollsList:
			poll = bets[0]
			winning_choice = bets[1]
			choice_count = {}
			returnBets = False
			if winning_choice == -2:
				returnBets = True
			query = "select que_slug, question_text, description from polls_question where id = %s" %poll
			questionSlugCur.execute(query)
			for row in questionSlugCur:
				que_slug = row[0]
				que_text = row[1]
				que_desc = row[2]
			if winning_choice:
				#send mail to betters
				findMax = False
				if winning_choice == -1:
					findMax = True
				user_credit_choice = "select user_id, betCredit, choice_id, id from polls_vote where choice_id in (select id from polls_choice where question_id=%s)"%poll
				userToBetCur.execute(user_credit_choice)
				user_credit_choice = "select user_id from polls_vote where betCredit=0 and choice_id in (select id from polls_choice where question_id=%s)"%poll
				userBetVotedCur.execute(user_credit_choice)
				user_id_choice_credit = {}
				user_id_list_vote = []
				user_id_list_bet = []
				total_pot = 0
				for row in userToBetCur:
					temp = list(row)
					choice_id = temp[2]
					credit = temp[1]
					if findMax and not returnBets:
						choice_count[choice_id] = choice_count.get(choice_id,0) + 1
					if credit > 0:
						user_id_list_bet.append(temp[0])
						user_id_choice_credit[temp[0]] = {
							"credit":credit,
							"choice":choice_id,
							"vote_id":temp[3]
						}
				max_choice = -1
				votes_list = []
				max_votes = -1
				if findMax and not returnBets:
					for choice,vote_count in choice_count.items():
						if vote_count in votes_list:
							returnBets = True
							break
						elif vote_count > max_votes:
							max_votes = vote_count
							max_choice = choice
						votes_list.append(vote_count)
					winning_choice = max_choice
				# print("voted people",user_id_list_vote)
				query = "select email,first_name,auth_user.id,login_extendeduser.mailSubscriptionFlag, login_extendeduser.id from auth_user inner join login_extendeduser on auth_user.id = login_extendeduser.user_id where auth_user.id in ( %s )"%(','.join(str(x) for x in user_id_list_bet))
				userToSendCur.execute(query)
				winners_pot = 0
				total_pot = 0
				for row in userToSendCur:
					# send bet mail
					temp = list(row)
					to_email = temp[0]
					que_voter = temp[1]
					que_voter_id = temp[2]
					mailSubscriptionFlag = temp[3]
					extendeduser_id = temp[4]
					user_dict = user_id_choice_credit.get(que_voter_id)
					user_dict['email'] = to_email
					user_dict['name'] = que_voter
					user_dict['mailSubscriptionFlag'] = mailSubscriptionFlag
					user_dict["extendeduser_id"] = extendeduser_id;
					if user_dict.get("choice") == winning_choice or returnBets:
						user_dict['action'] = "won"
						winners_pot +=  user_dict["credit"]
					else:
						user_dict['action'] = "lost"
					total_pot += user_dict["credit"]
				loosers_pot = total_pot - winners_pot
				# print("total",total_pot)
				# print("win",winners_pot)
				# print("lost",loosers_pot)
				# print(user_id_choice_credit)
				for que_voter_id,user_dict in user_id_choice_credit.items():
					to_email = user_dict['email']
					que_voter = user_dict['name']
					# print("calc mail",user_dict)
					earned_credit = 0
					if user_dict['action'] == 'won' and not returnBets:
						earned_credit = user_dict['credit'] + ((loosers_pot/winners_pot) * user_dict['credit'])
					user_dict['credit'] += earned_credit
					# print("You %s %s credits"%(user_dict['action'],user_dict['credit']))
					if user_dict['mailSubscriptionFlag'] == 0:
						send_expiry_bet_admin_mail(to_email,poll,que_voter,que_text,que_slug,"bet",user_dict['action'],user_dict['credit'])
					# print("exted",que_voter_id,type(que_voter_id))
					extendeduser = ExtendedUser.objects.get(pk=user_dict['extendeduser_id'])
					# print(extendeduser.credits)
					activity = {'actor': que_voter, 'verb': 'credits', 'object': poll, 'question_text':que_text, 'question_desc':que_desc, 'question_url':'/polls/'+str(poll)+'/'+que_slug, 'actor_user_name':que_voter,'actor_user_pic':extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(que_voter_id)+"/"+extendeduser.user_slug, "points":user_dict['credit'], "action":user_dict['action']+"Bet","visible_public":True}
					# print(activity)
					feed = client.feed('notification', que_voter_id)
					feed.add_activity(activity)
					if earned_credit > 0:
						# update user credits table
						new_credits = extendeduser.credits + user_dict['credit']
						updateQuery = "UPDATE login_extendeduser SET credits=%s WHERE id=%s"%(new_credits,user_dict['extendeduser_id'])
						insertCursor.execute(updateQuery)
						updateQuery = "UPDATE polls_vote SET earnCredit=%s WHERE id=%s"%(earned_credit,user_dict['vote_id'])
						insertCursor.execute(updateQuery)
				for row in userBetVotedCur:
					temp = list(row)
					user_id_list_vote.append(temp[0])
				if user_id_list_vote:
					query = "select email,first_name,auth_user.id from auth_user inner join login_extendeduser on auth_user.id = login_extendeduser.user_id where mailSubscriptionFlag=0 and auth_user.id in (%s )"%(",".join( str(x) for x in user_id_list_vote))
					userToSendCur.execute(query)
					for row in userToSendCur:
						# send expiry mail
						temp = list(row)
						to_email = temp[0]
						que_voter = temp[1]
						# print("expiry bet",temp)
						send_expiry_bet_admin_mail(to_email,poll,que_voter,que_text,que_slug,"expiry")
				insertQuery = "INSERT INTO pollexpiry_mail(pollid) VALUES (%s)" %poll
				insertCursor.execute(insertQuery)
			else:
				#send mail to admin for adding choice
				# print("admin")
				# to_email = "support@askbypoll.com"
				send_expiry_bet_admin_mail("admin",poll,"admin",que_text,que_slug,"admin")
		for poll in mailNotSentExpiredPolls:
			query = "select que_slug, question_text from polls_question where id = %s" %poll
			questionSlugCur.execute(query)
			for row in questionSlugCur:
				que_slug = row[0]
				que_text = row[1]
			
			query = "select email, first_name from auth_user inner join login_extendeduser on auth_user.id = login_extendeduser.user_id where mailSubscriptionFlag=0 and auth_user.id in (select polls_vote.user_id from polls_question inner join polls_choice on polls_question.id = polls_choice.question_id inner join polls_vote on polls_choice.id = polls_vote.choice_id where polls_question.id = %s)" %poll
			userToSendCur.execute(query)
			for row in userToSendCur:
				temp = list(row)
				to_email = temp[0]
				que_voter = temp[1]
				send_expiry_bet_admin_mail(to_email,poll,que_voter,que_text,que_slug,"expiry")
			insertQuery = "INSERT INTO pollexpiry_mail(pollid) VALUES (%s)" %poll
			insertCursor.execute(insertQuery)

		mailSentPollIdCur.close()
		expiredPollsCur.close()
		betPollsCur.close()
		questionSlugCur.close()
		userToSendCur.close()
		userToBetCur.close()
		userBetVotedCur.close()
		conn.commit()
		conn.close()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		err = ' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj)
		print(err)
		print(traceback.format_exc())

def send_expiry_bet_admin_mail(to_email,poll,que_voter,que_text,que_slug,mail_type,action="",betAmount=0):
	msg = None
	SalutoryMessage = ""
	Result = ""
	EarnedLost = ""
	if mail_type == "expiry":
		msg = EmailMessage(subject="Poll timed out notification from AskByPoll", from_email="askbypoll@gmail.com",to=[to_email])
		msg.template_name = "expiryemailnotification" #mandrill template name
	elif mail_type == "bet":
		msg = EmailMessage(subject="Bet Poll results out notification from AskByPoll", from_email="askbypoll@gmail.com",to=[to_email])
		msg.template_name = "predictionresults" #mandrill template name
		if action == "won":
			SalutoryMessage = "Hurray"
			Result = "correct"
			EarnedLost = "earned"
		else:
			SalutoryMessage ="Oops"
			Result = "wrong"
			EarnedLost = "lost"
	elif mail_type == "admin":
		subject = "Please update result"
		message = "/polls/"+str(poll)+'/'+que_slug+" "+que_text+" needs the winning_choice"
		send_mail(subject, message, 'support@askbypoll.com',['support@askbypoll.com','kewal07@gmail.com'], fail_silently=False)
		return
	msg.global_merge_vars = {                       # Merge tags in your template
		'QuestionVoter': que_voter, 'QuestionText': que_text, 'QuestionUrl':str(poll)+'/'+que_slug, "Points": betAmount, "SalutoryMessage": SalutoryMessage, "Result": Result, "EarnedLost":EarnedLost
	}
	if to_email and to_email.strip():
		# print("send msg",to_email,poll,que_voter,que_text,que_slug,mail_type,action,betAmount)
		msg.send()

if __name__ == '__main__':
	sendExpirationNotification()
