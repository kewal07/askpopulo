import pymysql
import random
import time
import datetime
from django.core.mail import EmailMessage
import askpopulo.settings
import sys
import csv

def aldpSurvey():
	try:
		db_dict = askpopulo.settings.DATABASES.get('default')
		db_host = db_dict.get('HOST')
		db_user = db_dict.get('USER')
		db_pass = db_dict.get('PASSWORD')
		db_name = db_dict.get('NAME')
		conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_name)
		
		opFile = open('aldp.csv','wt')
		aldpwriter = csv.writer(opFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		surveyQuestionsCur = conn.cursor()
		questionChoiceCur = conn.cursor()
		uniquekeysCur = conn.cursor()

		surveyQuestionsCur.execute("select polls_question.id, polls_question.question_text from polls_question inner join polls_survey_question on polls_question.id = polls_survey_question.question_id where polls_survey_question.survey_id = 81")
		
		uniquekeysCur.execute("select distinct unique_key from polls_voteapi where question_id = 4767")		
		quesList = []
		uk = []

		for row in surveyQuestionsCur:
			qList = list(row)
			quesList.append(qList)
		
		for row in uniquekeysCur:
			temp = list(row)
			uk.append(temp[0])
		temprow = [""]
		for r in uk:
			temprow.append(r)
		aldpwriter.writerow(temprow)
		temprow = []

		for qId, qText in quesList:
			questionChoiceCur = conn.cursor()
			questionChoiceCur.execute("select id, choice_text from polls_choice where question_id="+str(qId))
			tempRow = [qText]
			if questionChoiceCur.rowcount > 0:
				aldpwriter.writerow(tempRow)
				tempRow = []
				for choice in questionChoiceCur:
					tempRow.append(choice[1])
					for uqk in uk:
						answerColumnCur = conn.cursor()
						answerColumnCur.execute("select votecolumn_id from polls_voteapi where unique_key ="+str(uqk)+"and question_id = "+str(qId)+" and choice_id="+str(choice[0]))
						columnLabelCur = conn.cursor()
						colId = []
						for row in answerColumnCur:
							colId = list(row)

						if colId:
							columnLabelCur.execute("select columnlabel from polls_matrixratingcolumnlabels where id ="+str(colId[0]))
							for row in columnLabelCur:
								colLabel = list(row)
							tempRow.append(colLabel[0])
						else:
							tempRow.append('NA')
					aldpwriter.writerow(tempRow)
					tempRow = []
			else:
				for uqk in uk:
					answerTextCur = conn.cursor()
					answerTextCur.execute("select answer_text from polls_voteapi where unique_key ="+str(uqk)+" and question_id ="+str(qId))
					for ans in answerTextCur:
						ansVal = list(ans)
					tempRow.append(ansVal[0])
				aldpwriter.writerow(tempRow)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		err = ' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj)
		print(err)

def sendFeed():
	try:
		db_dict = askpopulo.settings.DATABASES.get('default')
		db_host = db_dict.get('HOST')
		db_user = db_dict.get('USER')
		db_pass = db_dict.get('PASSWORD')
		db_name = db_dict.get('NAME')
		conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_name)
	
		questionCur = conn.cursor()
		questionCur.execute("SELECT id,question_text,que_slug FROM polls_question where privatePoll = 0 ORDER BY id DESC LIMIT 0 , 3")
	
		userCur = conn.cursor()

		userIdCur = conn.cursor()
		userIdCur.execute("select auth_user.id, email from auth_user inner join login_extendeduser on auth_user.id = login_extendeduser.user_id where mailSubscriptionFlag = 0")

		catCur = conn.cursor()
		catCur.execute("SELECT category_title from categories_category order by rand() LIMIT 2")

		topQText = []
		topSlug  = []
		topQId   = []
		catList  = []
		subsQId  = []
		subsQText= []
		subsQSlug= []

		mail_log_file = open('/home/ubuntu/askpopulo/mail_send_log.log','a')

		for row in catCur:
			cList = list(row)
			catList.append(cList[0])

		for row in questionCur:
			topQ = list(row)
			topQId.append(topQ[0])
			topQText.append(topQ[1])
			topSlug.append(topQ[2])

		for_loop_counter = 1

		for idNumEmail in userIdCur:
			idNum = idNumEmail[0]
			to_email = idNumEmail[1]
			#print(to_email)
			query = "SELECT auth_user.id, auth_user.email, polls_subscriber.question_id, question_text, que_slug FROM auth_user INNER JOIN polls_subscriber ON   auth_user.id = polls_subscriber.user_id INNER JOIN polls_question ON polls_subscriber.question_id = polls_question.id WHERE auth_user.id = %s AND polls_question.privatePoll = 0 order by RAND() LIMIT 3" %idNum
			count = userCur.execute(query)
			if count!= 0:
				for row in userCur:
					data = list(row)
					subsQId.append(data[2])
					subsQText.append(data[3])
					subsQSlug.append(data[4])
			#print(to_email)
			msg = EmailMessage(subject="Your Personal News Feed delivered with love by Ask By Poll!", from_email="askbypoll@gmail.com",to=[to_email])
			msg.template_name = "activityletter"           # A Mandrill template name
			#msg.template_content = {                        # Content blocks to fill in
			#   'TRACKING_BLOCK1': "<a href='.../*|Link1|*'>Poll1</a>",
		   	#'Link1':"<a href='www.askbypoll.com/polls/'+str(topPolls[0].id)+'/'+topPolls[0].que_slug> *|TOP1|* </a>"
			#}
			#site="www.askbypoll.com"
			if count == 0:
				msg.global_merge_vars = {                       # Merge tags in your template
		    		'Top1': topQText[0], 'Top2': topQText[1], 'Top3':topQText[2],
		    		'Link1':str(topQId[0])+'/'+topSlug[0], 'Link2':str(topQId[1])+'/'+topSlug[1], 'Link3':str(topQId[2])+'/'+topSlug[2],
		    		#'Cat1': catList[0], 'Cat2': catList[1],
		    		'Cat1': 'Technology', 'Cat2': 'Education',
		    		'YourP1': 'Create Poll', 'YourP2': 'Vote on a Poll', 'YourP3':'Subscribe',
		    		'YLink1':'', 'YLink2':'', 'YLink3':''
				}		
			elif count == 1:
				msg.global_merge_vars = {                       # Merge tags in your template
		    		'Top1': topQText[0], 'Top2': topQText[1], 'Top3':topQText[2],
		    		'Link1':str(topQId[0])+'/'+topSlug[0], 'Link2':str(topQId[1])+'/'+topSlug[1], 'Link3':str(topQId[2])+'/'+topSlug[2],
		    		#'Cat1': catList[0], 'Cat2': catList[1],
		    		'Cat1': 'Technology', 'Cat2': 'Education',
		    		'YourP1': subsQText[0], 'YourP2': 'Ask More', 'YourP3':'Vote on a Poll',
		    		'YLink1':'polls'+'/'+str(subsQId[0])+'/'+subsQSlug[0], 'YLink2':'', 'YLink3':''
				}
			elif count == 2:
				msg.global_merge_vars = {                       # Merge tags in your template
		    		'Top1': topQText[0], 'Top2': topQText[1], 'Top3':topQText[2],
		    		'Link1':str(topQId[0])+'/'+topSlug[0], 'Link2':str(topQId[1])+'/'+topSlug[1], 'Link3':str(topQId[2])+'/'+topSlug[2],
		    		#'Cat1': catList[0], 'Cat2': catList[1],
		    		'Cat1': 'Technology', 'Cat2': 'Education',
		    		'YourP1': subsQText[0], 'YourP2': subsQText[1], 'YourP3':'Ask More',
		    		'YLink1':'polls'+'/'+str(subsQId[0])+'/'+subsQSlug[0], 'YLink2':'polls'+'/'+str(subsQId[1])+'/'+subsQSlug[1], 'YLink3':''
				}
			else:
				msg.global_merge_vars = {                       # Merge tags in your template
		    		'Top1': topQText[0], 'Top2': topQText[1], 'Top3':topQText[2],
		    		'Link1':str(topQId[0])+'/'+topSlug[0], 'Link2':str(topQId[1])+'/'+topSlug[1], 'Link3':str(topQId[2])+'/'+topSlug[2],
		    		#'Cat1': catList[0], 'Cat2': catList[1],
		    		'Cat1': 'Technology', 'Cat2': 'Education',
		    		'YourP1': subsQText[0], 'YourP2': subsQText[1], 'YourP3':subsQText[2],
		    		'YLink1':'polls'+'/'+str(subsQId[0])+'/'+subsQSlug[0], 'YLink2':'polls'+'/'+str(subsQId[1])+'/'+subsQSlug[1], 'YLink3':'polls'+'/'+str(subsQId[2])+'/'+subsQSlug[2]
				}
			doNotSendList = ['reading.goddess@yahoo.com','mrsalyssadandy@gmail.com','ourmisconception@gmail.com','sdtortorici@gmail.com','valeriepetsoasis@aol.com','gladys.adams.ga@gmail.com','denysespecktor@gmail.com','kjsmilesatme@gmail.com']
			if (not to_email in doNotSendList) and to_email and to_email.strip():
				mail_log_file.write("\n*********************** Send to and content **********************\n")
				mail_log_file.write(str(for_loop_counter) + "\n")
				mail_log_file.write(str(datetime.datetime.now()) + "\n")
				mail_log_file.write(to_email + "\n")
				mail_log_file.write(str(msg.global_merge_vars) + "\n")
				mail_log_file.write("\n*********************** Send to and content end ******************\n")
				for_loop_counter += 1
				msg.send()
				time.sleep(10)

			if for_loop_counter % 150 == 0:
				time.sleep(2200)
				pass

			subsQId  = []
			subsQText= []
			subsQSlug= []
			#msg.merge_vars = {                              # Per-recipient merge tags
			#    'accounting@example.com': {'NAME': "Pat"},
			#    'customer@example.com':   {'NAME': "Kim"}
			#}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		err = ' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj)
		mail_log_file.write(str(exc_type)+str(exc_obj)+str(exc_tb)+str(e)+str(err))
	mail_log_file.close()
	questionCur.close()
	userCur.close()
	userIdCur.close()
	catCur.close()
	conn.close()

aldpSurvey()
