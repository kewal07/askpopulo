import os
import pymysql
import time
import datetime
from django.core.mail import EmailMessage
import askpopulo.settings
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "askpopulo.settings"

def sendExpirationNotification():
	try:
		db_dict = askpopulo.settings.DATABASES.get('default')
		db_host = db_dict.get('HOST')
		db_user = db_dict.get('USER')
		db_pass = db_dict.get('PASSWORD')
		db_name = db_dict.get('NAME')
		conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_name)
	
		mailSentPollIdCur = conn.cursor()
		mailSentPollIdCur.execute("SELECT pollid FROM pollexpiry_mail")
		
		expiredPollsCur = conn.cursor()
		expiredPollsCur.execute("SELECT id FROM polls_question WHERE expiry is not null and NOW() > expiry")
	
		userToSendCur = conn.cursor()
		questionSlugCur = conn.cursor()
		insertCursor = conn.cursor()

		mailSentList = []
		expiredPollsList = []
		userToSendList = []
		to_email = ""
		que_slug = ""
		que_text = ""
		que_voter = ""

		for row in mailSentPollIdCur:
			temp = list(row)
			mailSentList.append(temp[0])

		for row in expiredPollsCur:
			temp = list(row)
			expiredPollsList.append(temp[0])
		
		mailNotSentExpiredPolls = list(set(expiredPollsList) - set(mailSentList))
		count = 0
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
				msg = EmailMessage(subject="Poll timed out notification from AskByPoll", from_email="askbypoll@gmail.com",to=[to_email])
				msg.template_name = "expiryemailnotification" #mandrill template name
				
				msg.global_merge_vars = {                       # Merge tags in your template
		    		'QuestionVoter': que_voter, 'QuestionText': que_text, 'QuestionUrl':str(poll)+'/'+que_slug
				}		

				#oNotSendList = ['reading.goddess@yahoo.com','mrsalyssadandy@gmail.com','ourmisconception@gmail.com','sdtortorici@gmail.com','valeriepetsoasis@aol.com','gladys.adams.ga@gmail.com','denysespecktor@gmail.com','kjsmilesatme@gmail.com']

				if to_email and to_email.strip():
					msg.send()
			insertQuery = "INSERT INTO pollexpiry_mail(pollid) VALUES (%s)" %poll
			insertCursor.execute(insertQuery)

		mailSentPollIdCur.close()
		expiredPollsCur.close()
		questionSlugCur.close()
		userToSendCur.close()
		conn.commit()
		conn.close()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		err = ' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj)
		#print(err)

if __name__ == '__main__':
	sendExpirationNotification()
