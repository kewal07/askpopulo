import os
import sys
from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from django.core.mail import send_mail
from polls.models import Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory,QuestionUpvotes
import polls.continent_country_dict
from categories.models import Category
import datetime
import simplejson as json
from django.core import serializers
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from haystack.forms import ModelSearchForm
import hmac
import hashlib
import base64
import time
from django.conf import settings
from collections import OrderedDict
from PIL import Image,ImageChops
from django.utils import timezone
from login.models import ExtendedUser,Follow,Company
from login.views import BaseViewList,BaseViewDetail
from login.forms import MySignupPartForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from stream_django.feed_manager import feed_manager
from stream_django.enrich import Enrich
from django.utils import timezone
from trivia.models import Trivia
import stream
client = stream.connect(settings.STREAM_API_KEY, settings.STREAM_API_SECRET)
from login.models import ExtendedGroup
from django.contrib.auth.models import Group

# Create your views here.

class TeamView(BaseViewList):
	template_name = 'polls/team.html'
	def get_queryset(self):
		return {}

class IndexView(BaseViewList):
	context_object_name = 'data'
	paginate_by = 50

	def render_to_response(self, context, **response_kwargs):
		response = super(IndexView, self).render_to_response(context, **response_kwargs)
		# print(self.request.COOKIES.get("location"))
		if not self.request.COOKIES.get("location"):
			# print("setting location cookie")
			response.set_cookie("location","global")
		return response

	def get_template_names(self):
		request = self.request
		template_name = 'polls/index.html'
		if request.path.endswith('category') and not request.GET.get('category'):
			template_name = 'polls/categories.html'
		return [template_name]
	
	def get_queryset(self):
		createExtendedUser(self.request.user)
		request = self.request
		user = request.user
		context = {}
		mainData = []
		latest_questions = []
		curtime = timezone.now()
		# if user.is_authenticated():
		# 	print(reverse('polls:mypolls', kwargs={'pk':user.id,'user_name':user.extendeduser.user_slug}),request.path, user.is_authenticated() and request.path == reverse('polls:mypolls', kwargs={'pk': user.id, 'user_name':user.extendeduser.user_slug}))
		global_location = ""
		country_list =[]
		if request.COOKIES.get("location","global").lower() != "global":
			global_location = request.COOKIES.get("location").lower()
			country_list = polls.continent_country_dict.continent_country_dict.get(global_location)
		# print(global_location)
		# print(country_list)

		if request.path.endswith('category') and not request.GET.get('category'):
			mainData = Category.objects.all()
			return mainData
		elif request.path.endswith('featuredpolls'):
			adminpolls = Question.objects.filter(user__is_superuser=1,privatePoll=0,home_visible=1).order_by('-pub_date')
			featuredpolls = Question.objects.filter(featuredPoll=1,privatePoll=0,home_visible=1).order_by('-pub_date')
			latest_questions.extend(featuredpolls)
			latest_questions.extend(adminpolls)
			if latest_questions:
				latest_questions = list(OrderedDict.fromkeys(latest_questions))
				if request.GET.get('tab') == 'mostvoted':
					latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
				elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
					latest_questions = latest_questions
				elif request.GET.get('tab') == 'leastvoted':
					latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
				elif request.GET.get('tab') == 'withexpiry':
					toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
					expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
					toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
					expired_polls.sort(key=lambda x: x.expiry, reverse=True)
					latest_questions = []
					if toexpire_polls:
						latest_questions.extend(toexpire_polls)
					if expired_polls:
						latest_questions.extend(expired_polls)
				# latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
			# sendFeed()
		elif user.is_authenticated() and request.path == reverse('polls:mypolls', kwargs={'pk': user.id, 'user_name':user.extendeduser.user_slug}):
			if request.GET.get('tab') == 'mycategories':
				category_questions = []
				if user.extendeduser.categories:
					user_categories_list = list(map(int,user.extendeduser.categories.split(',')))
					user_categories = Category.objects.filter(pk__in=user_categories_list)
					que_cat_list = QuestionWithCategory.objects.filter(category__in=user_categories)
					category_questions = [x.question for x in que_cat_list if x.question.privatePoll == 0 and x.question.home_visible == 1]
					latest_questions.extend(category_questions)
			elif request.GET.get('tab') == 'followed':
				followed_questions = [x.question for x in Subscriber.objects.filter(user=user)]
				latest_questions.extend(followed_questions)
			elif request.GET.get('tab') == 'voted':
				voted_questions = [x.question for x in Voted.objects.filter(user=user)]
				latest_questions.extend(voted_questions)
			elif request.GET.get('tab') == 'mypolls' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				asked_polls = Question.objects.filter(user=user)
				latest_questions.extend(asked_polls)
			if latest_questions:
				latest_questions = list(OrderedDict.fromkeys(latest_questions))
				latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
		elif request.GET.get('category'):
			category_title = request.GET.get('category')
			category = Category.objects.filter(category_title=category_title)[0]
			latest_questions = [que_cat.question for que_cat in QuestionWithCategory.objects.filter(category = category) if que_cat.question.privatePoll == 0 and que_cat.question.home_visible == 1]
			latest_questions = latest_questions[::-1]
			if request.GET.get('tab') == 'mostvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
			elif request.GET.get('tab') == 'withexpiry':
				toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
				expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
				toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
				expired_polls.sort(key=lambda x: x.expiry, reverse=True)
				latest_questions = []
				if toexpire_polls:
					latest_questions.extend(toexpire_polls)
				if expired_polls:
					latest_questions.extend(expired_polls)
		else:
			latest_questions = Question.objects.filter(privatePoll=0,home_visible=1).order_by('-pub_date')
			latest_questions = list(OrderedDict.fromkeys(latest_questions))
			if request.GET.get('tab') == 'mostvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
			elif request.GET.get('tab') == 'withexpiry':
				toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
				expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
				toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
				expired_polls.sort(key=lambda x: x.expiry, reverse=True)
				latest_questions = []
				if toexpire_polls:
					latest_questions.extend(toexpire_polls)
				if expired_polls:
					latest_questions.extend(expired_polls)
		subscribed_questions = []
		if user.is_authenticated():
			subscribed_questions = Subscriber.objects.filter(user=request.user)
		sub_que = []
		for sub in subscribed_questions:
			sub_que.append(sub.question.id)
		if country_list:
			latest_questions = [x for x in latest_questions if x.user.extendeduser and x.user.extendeduser.country in country_list ]
		for mainquestion in latest_questions:
			data = {}
			followers = [ x.user for x in Follow.objects.filter(target_id=mainquestion.user_id,deleted_at__isnull=True) ]
			following = [ x.target for x in Follow.objects.filter(user_id=mainquestion.user_id,deleted_at__isnull=True) ]
			data['connection'] = len(followers) + len(following)
			print(data['connection'])
			data ['question'] = mainquestion
			subscribers = mainquestion.subscriber_set.count()
			data['votes'] = mainquestion.voted_set.count()
			data['subscribers'] = subscribers
			data['subscribed'] = sub_que
			data['expired'] = False
			data['upvoteCount'] = mainquestion.upvoteCount
			if mainquestion.expiry and mainquestion.expiry < curtime:
				data['expired'] = True
			user_already_voted = False
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(user=user,question=mainquestion)
				if question_user_vote:
					user_already_voted = True
			# print(mainquestion,user_already_voted,user)
			data['user_already_voted'] = user_already_voted
			mainData.append(data)
		context['data'] = mainData
		return mainData

class VoteView(BaseViewDetail):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/voteQuestion.html'
		question = self.get_object()
		question.numViews +=1
		question.save()
		user = self.request.user
		if user.is_authenticated():
			voted = Voted.objects.filter(question = question, user=user)
			subscribed = Subscriber.objects.filter(user=user, question=question)
			# print(subscribed)
			if voted or user.id == question.user.id or ( question.expiry and question.expiry < timezone.now() ) or (self.request.path.endswith('result') and subscribed):
				template_name = 'polls/questionDetail.html'
		return [template_name]
	
	def get_context_data(self, **kwargs):

		context = super(VoteView, self).get_context_data(**kwargs)
		user = self.request.user
		subscribed_questions = []
		user_already_voted = False
		if user.is_authenticated():
			createExtendedUser(user)
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state:
				userFormData = {"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state}
				context['signup_part_form'] = MySignupPartForm(userFormData)
			profilepicUrl = user.extendeduser.get_profile_pic_url()
			if not profilepicUrl.startswith('http'):
				profilepicUrl = r"https://www.askbypoll.com"+profilepicUrl
			subscribed_questions = Subscriber.objects.filter(user=self.request.user)
			data = {
				"id":user.id,
				"username":user.username,
				"email":user.email,
				"avatar":profilepicUrl
			}
			data = json.dumps(data)
			message = base64.b64encode(data.encode('utf-8'))
			timestamp = int(time.time())
			key = settings.DISQUS_SECRET_KEY.encode('utf-8')
			msg = ('%s %s' % (message.decode('utf-8'), timestamp)).encode('utf-8')
			digestmod = hashlib.sha1
			sig = hmac.HMAC(key, msg, digestmod).hexdigest()
			ssoData = dict(
				message=message,
				timestamp=timestamp,
				sig=sig,
				pub_key=settings.DISQUS_API_KEY,
			)
			context['ssoData'] = ssoData
			question_user_vote = Voted.objects.filter(user=user,question=context['question'])
			if question_user_vote:
				user_already_voted = True
			context['user_already_voted'] = user_already_voted
		sub_que = []
		for sub in subscribed_questions:
			sub_que.append(sub.question.id)
		context['subscribed'] = sub_que
		context['expired'] = False
		followers = [ x.user for x in Follow.objects.filter(target_id=context['question'].user.id,deleted_at__isnull=True) ]
		following = [ x.target for x in Follow.objects.filter(user_id=context['question'].user.id,deleted_at__isnull=True) ]
		context['connection'] = len(followers) + len(following)
		if context['question'].expiry and context['question'].expiry < timezone.now():
			context['expired'] = True
		return context

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = request.POST.get('question')
		question = Question.objects.get(pk=questionId)
		queSlug = question.que_slug
		queBet = request.POST.get('betAmountHidden')
		if queBet:
			queBet = int(queBet)
		# print(request.is_ajax())
		# queSlug = "None"
		# print(user,user.is_authenticated())
		if user.is_authenticated():
			if request.is_ajax():
				if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state:
					return HttpResponse(json.dumps({}),content_type='application/json')
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state:
				url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
				return HttpResponseRedirect(url)
			if request.POST.get('choice'):
				if request.is_ajax():
					return HttpResponse(json.dumps({}),content_type='application/json')
				choiceId = request.POST.get('choice')
				choice = Choice.objects.get(pk=choiceId)
				# questionId = request.POST.get('question')
				# question = Question.objects.get(pk=questionId)
				# queSlug = question.que_slug
				voted_questions = user.voted_set.filter(user=user,question=question)
				if not voted_questions:
					if question.isBet and queBet:
						vote = Vote(user=user, choice=choice, betCredit=queBet)
						user.extendeduser.credits -= queBet
						user.extendeduser.save()
					else:
						vote = Vote(user=user, choice=choice)
					voted = Voted(user=user, question=question)
					# subscribed = Subscriber(user=user, question=question)
					subscribed, created = Subscriber.objects.get_or_create(user=user, question=question)
					vote.save()
					voted.save()
					# subscribed.save()
			else:
				# error to show no choice selected
				data={}
				data['form_errors'] = "Please select a choice"
				return HttpResponse(json.dumps(data),
	                            content_type='application/json')
		else:
				if request.is_ajax():
					return HttpResponse(json.dumps({}),content_type='application/json')
				next_url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
				extra_params = '?next=%s'%next_url
				url = reverse('account_login')
				full_url = '%s%s'%(url,extra_params)
				if request.is_ajax():
					return HttpResponse(json.dumps({}),content_type='application/json')
				return HttpResponseRedirect(full_url)
		url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
		visible_public = True
		if question.privatePoll:
			visible_public = False
			points = 20
		else:
			points = 10
		activity = {'actor': user.username, 'verb': 'voted', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug,"visible_public":visible_public}
		if question.isBet and queBet:
			activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":queBet, "action":"voteBet","visible_public":visible_public}
			feed = client.feed('notification', user.id)
			feed.add_activity(activity)
			activity = {'actor': user.username, 'verb': 'votedBet', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":queBet,"visible_public":visible_public}
		following_id_list = [x.user_id for x in Subscriber.objects.filter(question_id=question.id) if x.user_id != question.user_id]
		while user.id in following_id_list:
			following_id_list.remove(user.id)
		if user.id != question.user_id:
			feed = client.feed('notification', question.user_id)
			feed.add_activity(activity)
		for following_id in following_id_list:
			feed = client.feed('notification', following_id)
			feed.add_activity(activity)
		feed = client.feed('user', question.user_id)
		feed.add_activity(activity)
		feed = client.feed('user', user.id)
		feed.add_activity(activity)
		feed = client.feed('flat', user.id)
		feed.add_activity(activity)
		activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":points, "action":"vote","visible_public":visible_public}
		feed = client.feed('notification', user.id)
		feed.add_activity(activity)
		user.extendeduser.credits += points
		user.extendeduser.save()
		return HttpResponseRedirect(url)
		
class EditView(BaseViewDetail):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/editQuestion.html'
		return [template_name]

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		context = super(EditView, self).get_context_data(object=self.object)
		question = context['question']
		canEdit = True
		if (question.voted_set.count() > 0 and not request.user.is_superuser):
			canEdit = False
		if question.user != request.user and not request.user.is_superuser:
			canEdit = False
		if not canEdit:
			url = reverse('polls:polls_vote', kwargs={'pk':question.id,'que_slug':question.que_slug})
			return HttpResponseRedirect(url)
		else:
			context["data"] = Category.objects.all()
			if question.expiry:
				tim = question.expiry#.strftime("%Y-%m-%d %H:%M:%S")
				# context["expiry_date"] = datetime.datetime.strptime(tim, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
				context["qExpiry_year"]= tim.year
				context["qExpiry_month"]= tim.month
				context["qExpiry_day"]= tim.day
				context["qExpiry_hr"]= tim.hour
				context["qExpiry_min"]= tim.minute
				context["qExpiry_ap"] = "AM"
				if tim.hour > 11:
					context["qExpiry_ap"] = "PM"
					if tim.hour > 12:
						context["qExpiry_hr"] -= 12
			categories = ""
			for cat in question.questionwithcategory_set.all():
				categories += cat.category.category_title+","
			context["question_categories"] = categories
			return self.render_to_response(context)
		
class DeleteView(BaseViewDetail):
	model = Question
	
	def get_context_data(self, **kwargs):
		return super(DeleteView, self).get_context_data(**kwargs)
	
	def get(self, request, *args, **kwargs):
		url = reverse('polls:index')
		question = self.get_object()
		if question.user == request.user or request.user.is_superuser:
			question.delete()
		return HttpResponseRedirect(url)

class CreatePollView(BaseViewList):
	template_name = 'polls/createPoll.html'
	context_object_name = 'data'
	
	def get_queryset(self):
		createExtendedUser(self.request.user)
		context = {}
		user = self.request.user
		if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state:
			userFormData = {"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state}
			context['signup_part_form'] = MySignupPartForm(userFormData)
		context['categories'] = Category.objects.all()
		groups = [x.group.name for x in ExtendedGroup.objects.filter(user_id = user.id)]
		context['groups'] = groups
		return context
	
	def post(self, request, *args, **kwargs):
		user = request.user
		edit = False
		ajax = False
		previousBet = True
		errors = {}
		question = None
		curtime = datetime.datetime.now();
		home_visible = 1
		if user.extendeduser.company_id > 1:
			home_visible=0
		# print(request.POST)
		queBetAmount = request.POST.get("betAmount")
		if queBetAmount:
			queBetAmount = int(queBetAmount)
		queBetChoiceText = request.POST.get("betChoice")
		queBetChoice = None
		# print("BET AMOUNT",queBetAmount)
		if request.GET.get("ajax"):
			ajax = True
		if request.GET.get("qid"):
			edit = True
		if not user.is_authenticated():
			url = reverse('account_login')
		elif request.POST:
			qText = request.POST.get('qText')	
			qText = qText.replace('\n', ' ').replace('\r', '')
			if not qText.strip():
				errors['qTextError'] = "Question required"
			qDesc = request.POST.get('qDesc')
			qExpiry = None
			if edit:
				question = Question.objects.get(pk=request.GET.get("qid"))
				if request.POST.get("oldExpiryTime") != "clean":
					curtime = timezone.now();
					qExpiry = question.expiry
				previousBet = question.isBet
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]
			# print(qeyear, qemonth, qeday, qehr, qemin, qeap)
			if qeyear != 0 or qemonth != 0 or qeday != 0 or qehr != 0 or qemin != -1: 
				if qeap.lower() == 'pm' and qehr != 12:
					qehr = qehr + 12
				elif qeap.lower() == 'am' and qehr == 12:
					qehr = 0
				# qExpiry = request.POST.get('qExpiry')
				print(qeyear, qemonth, qeday, qehr, qemin, qeap)
				try:
					curtime = datetime.datetime.now();
					qExpiry = datetime.datetime(qeyear, qemonth, qeday,hour=qehr,minute=qemin)
					if qExpiry < curtime:
						raise Exception
				except:
					errors['expiryError'] = "Invalid date time"
			# print(qExpiry)
			# if not qExpiry:
			# 	qExpiry = None
			choice1 = ""
			choice2 = ""
			choice3 = ""
			choice4 = ""
			choice1Image = ""
			choice2Image = ""
			choice3Image = ""
			choice4Image = ""
			choice1Present = False
			choice2Present = False
			if request.POST.getlist('choice1') != [''] and request.POST.getlist('choice1') != ['',''] or request.FILES.get('choice1'):
				choice1Present = True
			if request.POST.getlist('choice2') != [''] and request.POST.getlist('choice2') != ['',''] or request.FILES.get('choice2'):
				choice2Present = True
			imagePathList = []
			images = []
			choices = []
			selectedCats = request.POST.get('selectedCategories','').split(",")
			selectedGnames = request.POST.get('selectedGroups','').split(",")
			if not list(filter(bool, selectedCats)):
				errors['categoryError'] = "Please Select a category"
			choice1 = request.POST.getlist('choice1')[0].strip()
			if choice1:
				choices.append(choice1)
			if edit and request.POST.get('imagechoice1',""):
				choiceid = request.POST.get('imagechoice1').split("---")[1]
				choice1Image = Choice.objects.get(pk=choiceid).choice_image
				imagePathList.append(choice1Image.path)
			else:
				choice1Image = request.FILES.get('choice1')
			if choice1Image:
				images.append(choice1Image)
			choice2 = request.POST.getlist('choice2')[0].strip()
			if choice2:
				choices.append(choice2)
			if edit and request.POST.get('imagechoice2',""):
				choiceid = request.POST.get('imagechoice2').split("---")[1]
				choice2Image = Choice.objects.get(pk=choiceid).choice_image
				imagePathList.append(choice2Image.path)
			else:
				choice2Image = request.FILES.get('choice2')
			if choice2Image:
				images.append(choice2Image)
			if request.POST.getlist('choice3'):
				choice3 = request.POST.getlist('choice3')[0].strip()
				if choice3:
					choices.append(choice3)
			if edit and request.POST.get('imagechoice3',""):
				choiceid = request.POST.get('imagechoice3').split("---")[1]
				choice3Image = Choice.objects.get(pk=choiceid).choice_image
				imagePathList.append(choice3Image.path)
			else:
				choice3Image = request.FILES.get('choice3')
			if choice3Image:
				images.append(choice3Image)
			if request.POST.getlist('choice4'):
				choice4 = request.POST.getlist('choice4')[0].strip()
				if choice4:
					choices.append(choice4)
			if edit and request.POST.get('imagechoice4',""):
				choiceid = request.POST.get('imagechoice4').split("---")[1]
				choice4Image = Choice.objects.get(pk=choiceid).choice_image
				imagePathList.append(choice4Image.path)
			else:
				choice4Image = request.FILES.get('choice4')
			if choice4Image:
				images.append(choice4Image)
			isAnon = request.POST.get('anonymous')
			isPrivate = request.POST.get('private')
			isBet = request.POST.get('bet')
			isProtectResult = request.POST.get('protectResult',False)
			if isAnon:
				anonymous = 1
			else:
				anonymous = 0
			if isPrivate:
				private = 1
			else:
				private = 0
			if isBet:
				bet = 1
			else:
				bet = 0
			if isProtectResult:
				protectResult = 1
			else:
				protectResult = 0
			# return if any errors
			betError = ""
			if bet and isPrivate:
				betError += "Prediction Poll cannot be private.<br>"
			if bet and not qExpiry:
				betError += "Prediction Poll should have expiry.<br>"
			if bet and qExpiry and (qExpiry > curtime + datetime.timedelta(days=7)):
				betError += "Prediction Poll expiry should not be more that 7 days.<br>"
			# if qExpiry:
			# 	print((qExpiry - curtime).days, curtime, qExpiry)
			# print("0000000000000000000000000",queBetAmount)
			if queBetAmount and (queBetAmount < 10 or queBetAmount > user.extendeduser.credits):
				betError += "Prediction Poll credits between 10 and %s"%(user.extendeduser.credits)
			if betError:
				errors['betError'] = betError
			if not (choice1.strip() or choice1Image) or not (choice2.strip() or choice2Image):
				errors['choiceError'] = "Choice required"
			if len(choices)!=len(set(choices)):
				errors['duplicateChoice'] = "Please provide different choices"
			imageSize = 128, 128
			"""
			for i,image1 in enumerate(images):
				for j,image2 in enumerate(images):
					if i != j:
						image1obj = Image.open(image1)
						image2obj = Image.open(image2)
						#image2obj.load()
						#image1obj.load()
						if not ImageChops.difference(image1obj,image2obj).getbbox():
							errors['duplicateImage'] = "Please provide different images as choice"
							break
				if 'duplicateImage' in errors:
					break
			"""
			if errors or ajax:
				return HttpResponse(json.dumps(errors), content_type='application/json')
			# mark bet poll as private untill verified by admin
			if bet and not user.is_superuser:
				private = 1
			if edit:
				# question = Question.objects.get(pk=request.GET.get("qid"))
				question.question_text=qText
				question.description=qDesc
				question.expiry=qExpiry
				question.isAnonymous=anonymous
				question.privatePoll=private
				question.isBet = bet
				question.protectResult = protectResult
			else:
				question = Question(user=user, question_text=qText, description=qDesc, expiry=qExpiry, pub_date=curtime,isAnonymous=anonymous,privatePoll=private,isBet=bet,home_visible=home_visible,protectResult=protectResult)
			question.save()
			sub,created = Subscriber.objects.get_or_create(user=user,question=question)
			# sub.save()
			if edit:
				for choice in question.choice_set.all():
					if choice.choice_image:
						if os.path.isfile(choice.choice_image.path) and choice.choice_image.path not in imagePathList:
							os.remove(choice.choice_image.path)
					choice.delete()
				for que_cat in question.questionwithcategory_set.all():
					que_cat.delete()
			# print("selectedcates",selectedCats,list(filter(bool, selectedCats)))
			if list(filter(bool, selectedCats)):
				for cat in selectedCats:
					if cat:
						category = Category.objects.filter(category_title=cat)[0]
						qWcat = QuestionWithCategory(question=question,category=category)
						qWcat.save()
			else:
				category = Category.objects.filter(category_title="Miscellaneous")[0]
				qWcat = QuestionWithCategory(question=question,category=category)
				qWcat.save()
			if choice1 or choice1Image:
				choice = Choice(question=question,choice_text=choice1,choice_image=choice1Image)
				choice.save()
				if queBetAmount and queBetChoiceText == "choice1":
					queBetChoice = choice
			if choice2 or choice2Image:
				choice = Choice(question=question,choice_text=choice2,choice_image=choice2Image)
				choice.save()
				if queBetAmount and queBetChoiceText == "choice2":
					queBetChoice = choice
			if choice3 or choice3Image:
				choice = Choice(question=question,choice_text=choice3,choice_image=choice3Image)
				choice.save()
				if queBetAmount and queBetChoiceText == "choice3":
					queBetChoice = choice
			if choice4 or choice4Image:
				choice = Choice(question=question,choice_text=choice4,choice_image=choice4Image)
				choice.save()
				if queBetAmount and queBetChoiceText == "choice4":
					queBetChoice = choice
		if queBetChoice:
			vote = Vote(user=question.user,choice=queBetChoice,betCredit=queBetAmount)
			vote.save()
			voted = Voted(user=question.user,question=question)
			voted.save()
			question.user.extendeduser.credits -= queBetAmount
			question.user.extendeduser.save()
		# send mail to the admin for verification
		if bet and not user.is_superuser:
			qIdBet = question.id
			qSlugBet = question.que_slug
			qUrlBet = "https://www.askbypoll.com/polls/"+str(qIdBet)+"/"+qSlugBet
			qUserBet = question.user
			qTextBet = question.question_text
			subject = "Verify Bet Question"
			message = str(qUserBet)+" created bet on %s url %s"%(qTextBet,qUrlBet)
			send_mail(subject, message, 'support@askbypoll.com',['support@askbypoll.com','kewal07@gmail.com'], fail_silently=False)
		visible_public = True
		if question.privatePoll or question.isAnonymous:
			visible_public = False
		# if not (question.isAnonymous or question.privatePoll):
		user = question.user
		actor_user_name = user.username
		actor_user_url = '/user/'+str(user.id)+"/"+user.extendeduser.user_slug
		actor_user_pic = user.extendeduser.get_profile_pic_url()
		activity = {'actor': actor_user_name, 'verb': 'question', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':actor_user_name,'actor_user_pic':actor_user_pic,'actor_user_url': actor_user_url,"visible_public":visible_public}
		if queBetChoice:
			activity = {'actor': actor_user_name, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':actor_user_name,'actor_user_pic':actor_user_pic,'actor_user_url': actor_user_url, "points":queBetAmount, "action":"questionBet","visible_public":visible_public}
			feed = client.feed('notification', user.id)
			feed.add_activity(activity)
			activity = {'actor': actor_user_name, 'verb': 'questionBet', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':actor_user_name,'actor_user_pic':actor_user_pic,'actor_user_url': actor_user_url, 'points':queBetAmount,"visible_public":visible_public}
		following_id_list = [ x.user_id for x in Follow.objects.filter(target_id=user.id,deleted_at__isnull=True)]
		feed = client.feed('user',user.id)
		feed.add_activity(activity)
		if visible_public:
			feed = client.feed('flat',user.id)
			feed.add_activity(activity)
			for following_id in following_id_list:
				feed = client.feed('notification', following_id)
				feed.add_activity(activity)
		url = reverse('polls:polls_vote', kwargs={'pk':question.id,'que_slug':question.que_slug})
		# add credits only when the poll has been made public by the super user
		if not private and question.isBet and request.user.is_superuser:
			user = question.user
			actor_user_name = user.username
			actor_user_url = '/user/'+str(user.id)+"/"+user.extendeduser.user_slug
			actor_user_pic = user.extendeduser.get_profile_pic_url()
			activity = {'actor': actor_user_name, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':actor_user_name,'actor_user_pic':actor_user_pic,'actor_user_url': actor_user_url, "points":10, "action":"asked"}
			feed = client.feed('notification', user.id)
			feed.add_activity(activity)
			user.extendeduser.credits += 10
			user.extendeduser.save()
		if not edit:
			if list(filter(bool, selectedGnames)):
				for gName in selectedGnames:
					if gName:
						group_user_set = Group.objects.filter(name=gName)[0].user_set.all()
						for group_user in group_user_set:
							group_user_email = group_user.email
							msg = EmailMessage(subject="Invitation", from_email=request.user.email,to=[group_user_email])
							msg.template_name = "group-mail-question"
							msg.global_merge_vars = {
			                    'inviter': request.user.first_name,
			                    'companyname':request.user.extendeduser.company.name,
			                    'questionUrl':"www.askbypoll.com"+url,
			                    'questionText':question.question_text
			                }
							msg.send()
		return HttpResponseRedirect(url)

class PollsSearchView(SearchView):
    
    def extra_context(self):
        queryset = super(PollsSearchView, self).get_results()
        queryset = [x for x in queryset if x.object.privatePoll == 0]
        return {'query': queryset,}

class FollowPollView(BaseViewList):

	def post(self,request,*args,**kwargs):
		follow = request.POST.get('follow')
		qId = request.POST.get('question').replace("follow","")
		question = Question.objects.get(pk=qId)
		if follow == "true":
			sub = Subscriber(user=request.user,question=question)
			sub.save()
		elif follow == "false":
			sub = Subscriber.objects.filter(user=request.user,question=question)[0]
			sub.delete()
		data = {}
		data['sub_count'] = question.subscriber_set.count()
		return HttpResponse(json.dumps(data),content_type='application/json')

class ReportAbuse(BaseViewList):

	def get(self,request,*args,**kwargs):
		qIdBan = request.GET.get('qIdBan')
		user = request.user
		subject = "Report Abuse"
		message = str(user)+" reported abuse on the question "+qIdBan
		send_mail(subject, message, 'support@askbypoll.com',['support@askbypoll.com','kewal07@gmail.com'], fail_silently=False)
		data = {}
		return HttpResponse(json.dumps(data),content_type='application/json')

def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(question_auto=request.GET.get('qText', ''))[:5]
    suggestions = [[result.object.question_text,result.object.id,result.object.que_slug] for result in sqs if result.object.privatePoll == 0]
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')

def createExtendedUser(user):
	if not user.is_authenticated():
		pass
	elif hasattr(user,'extendeduser'):
		# user_slug = request.user.extendeduser.user_slug
		pass
	elif user.socialaccount_set.all():
		social_set = user.socialaccount_set.all()[0]
		# print((social_set.extra_data))
		if not (ExtendedUser.objects.filter(user_id = user.id)):
			if social_set.provider == 'facebook':
				facebook_data = social_set.extra_data
				img_url =  "https://graph.facebook.com/{}/picture?width=140&&height=140".format(facebook_data.get('id',''))
				gender_data = facebook_data.get('gender','')[0].upper()
				birth_day = facebook_data.get('birthday','2002-01-01')
				extendedUser = ExtendedUser(user=user, imageUrl = img_url, birthDay = birth_day,gender=gender_data)
				extendedUser.save()
			if social_set.provider == 'google':
				google_data = social_set.extra_data
				img_url = google_data.get('picture')
				if 'gender' in google_data :
					gender_data = google_data.get('gender','')[0].upper()
				else:
					gender_data = 'D'
				extendedUser = ExtendedUser(user=user, imageUrl = img_url, gender=gender_data)
				extendedUser.save()
			if social_set.provider == 'twitter':
				twitter_data = social_set.extra_data
				img_url = twitter_data.get('profile_image_url')
				city_data = twitter_data.get('location','')
				extendedUser = ExtendedUser(user=user, imageUrl = img_url, city=city_data)
				extendedUser.save()

def comment_mail(request):
	to_email = []
	que_text = request.POST.get('que_text')
	que_url = request.POST.get('que_url')
	com_author = request.user.first_name
	que_author = []
	if request.user.id != request.POST.get('to_user_id'):
		que_author.append(request.POST.get('que_author'))
		to_email.append(User.objects.filter(pk=request.POST.get('to_user_id'))[0].email)
	for sub_user in Subscriber.objects.filter(question_id=request.POST.get('que_id')):
		sub_email = sub_user.user.email
		if sub_email not in to_email and sub_user.user.id != request.user.id:
			to_email.append(sub_email)
			que_author.append(sub_user.user.first_name)
	# print(to_email)
	doNotSendList = ['reading.goddess@yahoo.com','mrsalyssadandy@gmail.com','ourmisconception@gmail.com','sdtortorici@gmail.com','valeriepetsoasis@aol.com','gladys.adams.ga@gmail.com','denysespecktor@gmail.com','kjsmilesatme@gmail.com']
	for index,to_mail in enumerate(to_email):
		if (not to_email in doNotSendList):
			msg = EmailMessage(subject="Discussion @ AskByPoll", from_email="askbypoll@gmail.com",to=[to_mail])
			msg.template_name = "commetnotificationquestionauthor"           # A Mandrill template name
			msg.global_merge_vars = {                       # Merge tags in your template
		    	"QuestionAuthor" : que_author[index],
		    	"CommentAuthor" : com_author,
		    	"QuestionURL" : que_url,
		    	"QuestionText" : que_text
				}
			msg.send()
	user = request.user
	actor_user_name = user.username
	actor_user_url = '/user/'+str(user.id)+"/"+user.extendeduser.user_slug
	actor_user_pic = user.extendeduser.get_profile_pic_url()
	activity = {'actor': actor_user_name, 'verb': 'credits', 'object': que_text, 'question_text':que_text, 'question_url':que_url, 'actor_user_name':actor_user_name,'actor_user_pic':actor_user_pic,'actor_user_url': actor_user_url, "points":20, "action":"comment"}
	feed = client.feed('notification', user.id)
	feed.add_activity(activity)
	request.user.extendeduser.credits += 20
	request.user.extendeduser.save()
	return HttpResponse(json.dumps({}),content_type='application/json')

def error_CompanyName(request):
	return render(request,'error404.html')

def privacyPolicy(request):
	return render(request,'privacyPolicy.html')

class MyUnsubscribeView(BaseViewList):
	template_name = 'unsubscribe.html'

	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		error={}
		ajax = False
		if request.GET.get("ajax"):
			ajax = True
		emailToUnsubscribe = request.POST.get('unsubscribeEmail')
		if(emailToUnsubscribe):
			userId = User.objects.filter(email=emailToUnsubscribe).values('id')
			if(userId):
				unsubscribeUser = ExtendedUser.objects.get(user_id = userId)
				unsubscribeUser.mailSubscriptionFlag = 1
				unsubscribeUser.save()
			else:
				error['nouser'] = "No user exists with given email id. Please provide your correct email id"
		else:
			error['emptyemail'] = "Please provide your registered email id to unsubscribe."
		if error or ajax:
			if(('emptyemail' in error) or ('nouser' in error)):
				return HttpResponse(json.dumps(error), content_type='application/json')
			else:
				print("here")
				error['success'] = "You are successfully unsubscribed from all email notifications."
				return HttpResponse(json.dumps(error), content_type='application/json')

class QuestionUpvoteView(BaseViewList):
	template_name = 'index.html'

	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		try:
			error={}
			response={}
			votedQuestionId = int(request.GET.get("qId"))
			vote = int(request.GET.get("vote"))

			isAlreadyVotedByUser = QuestionUpvotes.objects.filter(user_id = request.user.id, question_id = votedQuestionId)
			questionVoted = Question.objects.get(pk=votedQuestionId)
			if(isAlreadyVotedByUser):
				if((isAlreadyVotedByUser[0].vote and vote == 1) or (not(isAlreadyVotedByUser[0].vote) and vote == 0)):
					response={"message":"You already voted"}
					return HttpResponse(json.dumps(response), content_type='application/json')
				diff = 2
			else:
				diff = 1
				request.user.extendeduser.credits += 2 
				request.user.extendeduser.save()
				user = request.user
				question = questionVoted
				activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":2, "action":"up_down_vote"}
				feed = client.feed('notification', user.id)
				feed.add_activity(activity)	
			upVote, created = QuestionUpvotes.objects.get_or_create(user_id=request.user.id, question_id = votedQuestionId)
			if vote == 1:
				questionVoted.upvoteCount += diff
				questionVoted.user.extendeduser.credits += diff * 2
				user = questionVoted.user
				question = questionVoted
				activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":diff * 2, "action":"upvote"}
			else:
				questionVoted.upvoteCount -= diff
				questionVoted.user.extendeduser.credits -= diff * 2
				user = questionVoted.user
				question = questionVoted
				activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":diff * 2, "action":"downvote"}
			questionVoted.save()
			questionVoted.user.extendeduser.save()
			feed = client.feed('notification', questionVoted.user.id)
			feed.add_activity(activity)	
			countVotes = questionVoted.upvoteCount
			upVote.vote = vote
			upVote.save()
			response = {"message":"Done", "count":countVotes}
				
			return HttpResponse(json.dumps(response), content_type='application/json')

		except Exception as e:
			import os,sys
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			print(e)

class CompanyIndexView(BaseViewList):
	context_object_name = 'data'
	paginate_by = 50

	def render_to_response(self, context, **response_kwargs):
		response = super(CompanyIndexView, self).render_to_response(context, **response_kwargs)
		# # print(self.request.COOKIES.get("location"))
		# if not self.request.COOKIES.get("location"):
		# 	# print("setting location cookie")
		# 	response.set_cookie("location","global")
		return response

	def get_template_names(self):
		request = self.request
		template_name = 'polls/company.html'
		# if request.path.endswith('category') and not request.GET.get('category'):
		# 	template_name = 'polls/categories.html'
		return [template_name]
	
	def get_queryset(self):
		createExtendedUser(self.request.user)
		request = self.request
		user = request.user
		context = {}
		mainData = []
		latest_questions = []
		curtime = timezone.now()
		# print(request.path.replace("/",""))
		company_name = request.path.replace("/","")
		company_obj = Company.objects.filter(name=company_name)
		if company_obj:
			company_obj = company_obj[0]
		else:
			return HttpResponseRedirect("/") #this should be a 404 page
		# if user.is_authenticated():
		# 	print(reverse('polls:mypolls', kwargs={'pk':user.id,'user_name':user.extendeduser.user_slug}),request.path, user.is_authenticated() and request.path == reverse('polls:mypolls', kwargs={'pk': user.id, 'user_name':user.extendeduser.user_slug}))
		# global_location = ""
		# country_list =[]
		# if request.COOKIES.get("location","global").lower() != "global":
		# 	global_location = request.COOKIES.get("location").lower()
		# 	country_list = polls.continent_country_dict.continent_country_dict.get(global_location)
		# print(global_location)
		# print(country_list)

		# if request.path.endswith('category') and not request.GET.get('category'):
		# 	mainData = Category.objects.all()
		# 	return mainData
		# elif request.path.endswith('featuredpolls'):
		# 	adminpolls = Question.objects.filter(user__is_superuser=1,privatePoll=0).order_by('-pub_date')
		# 	featuredpolls = Question.objects.filter(featuredPoll=1,privatePoll=0).order_by('-pub_date')
		# 	latest_questions.extend(featuredpolls)
		# 	latest_questions.extend(adminpolls)
		# 	if latest_questions:
		# 		latest_questions = list(OrderedDict.fromkeys(latest_questions))
		# 		if request.GET.get('tab') == 'mostvoted':
		# 			latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
		# 		elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
		# 			latest_questions = latest_questions
		# 		elif request.GET.get('tab') == 'leastvoted':
		# 			latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
		# 		elif request.GET.get('tab') == 'withexpiry':
		# 			toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
		# 			expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
		# 			toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
		# 			expired_polls.sort(key=lambda x: x.expiry, reverse=True)
		# 			latest_questions = []
		# 			if toexpire_polls:
		# 				latest_questions.extend(toexpire_polls)
		# 			if expired_polls:
		# 				latest_questions.extend(expired_polls)
		# 		# latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
		# 	# sendFeed()
		# elif user.is_authenticated() and request.path == reverse('polls:mypolls', kwargs={'pk': user.id, 'user_name':user.extendeduser.user_slug}):
		# 	if request.GET.get('tab') == 'mycategories':
		# 		category_questions = []
		# 		if user.extendeduser.categories:
		# 			user_categories_list = list(map(int,user.extendeduser.categories.split(',')))
		# 			user_categories = Category.objects.filter(pk__in=user_categories_list)
		# 			que_cat_list = QuestionWithCategory.objects.filter(category__in=user_categories)
		# 			category_questions = [x.question for x in que_cat_list if x.question.privatePoll == 0]
		# 			latest_questions.extend(category_questions)
		# 	elif request.GET.get('tab') == 'followed':
		# 		followed_questions = [x.question for x in Subscriber.objects.filter(user=user)]
		# 		latest_questions.extend(followed_questions)
		# 	elif request.GET.get('tab') == 'voted':
		# 		voted_questions = [x.question for x in Voted.objects.filter(user=user)]
		# 		latest_questions.extend(voted_questions)
		# 	elif request.GET.get('tab') == 'mypolls' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
		# 		asked_polls = Question.objects.filter(user=user)
		# 		latest_questions.extend(asked_polls)
		# 	if latest_questions:
		# 		latest_questions = list(OrderedDict.fromkeys(latest_questions))
		# 		latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
		# elif request.GET.get('category'):
		# 	category_title = request.GET.get('category')
		# 	category = Category.objects.filter(category_title=category_title)[0]
		# 	latest_questions = [que_cat.question for que_cat in QuestionWithCategory.objects.filter(category = category) if que_cat.question.privatePoll == 0]
		# 	latest_questions = latest_questions[::-1]
		# 	if request.GET.get('tab') == 'mostvoted':
		# 		latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
		# 	elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
		# 		latest_questions = latest_questions
		# 	elif request.GET.get('tab') == 'leastvoted':
		# 		latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
		# 	elif request.GET.get('tab') == 'withexpiry':
		# 		toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
		# 		expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
		# 		toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
		# 		expired_polls.sort(key=lambda x: x.expiry, reverse=True)
		# 		latest_questions = []
		# 		if toexpire_polls:
		# 			latest_questions.extend(toexpire_polls)
		# 		if expired_polls:
		# 			latest_questions.extend(expired_polls)
		# else:
		company_user_list = ExtendedUser.objects.filter(company_id=company_obj.id)
		company_user_list = [x.user_id for x in company_user_list]
		company_admin_list = User.objects.filter(id__in = company_user_list)
		company_admin_list = [x.username for x in company_admin_list]
		followed = Follow.objects.filter(user_id=user.id,target_id__in=company_user_list, deleted_at__isnull=True)
		latest_questions = Question.objects.filter(privatePoll=0,user_id__in=company_user_list).order_by('-pub_date')
		latest_questions = list(OrderedDict.fromkeys(latest_questions))
		if request.GET.get('tab') == 'mostvoted':
			latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=True)
		elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
			latest_questions = latest_questions
		elif request.GET.get('tab') == 'leastvoted':
			latest_questions.sort(key=lambda x: x.voted_set.count(), reverse=False)
		elif request.GET.get('tab') == 'withexpiry':
			toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
			expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
			toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
			expired_polls.sort(key=lambda x: x.expiry, reverse=True)
			latest_questions = []
			if toexpire_polls:
				latest_questions.extend(toexpire_polls)
			if expired_polls:
				latest_questions.extend(expired_polls)
		subscribed_questions = []
		if user.is_authenticated():
			subscribed_questions = Subscriber.objects.filter(user=request.user)
		sub_que = []
		for sub in subscribed_questions:
			sub_que.append(sub.question.id)
		# if country_list:
		# 	latest_questions = [x for x in latest_questions if x.user.extendeduser and x.user.extendeduser.country in country_list ]
		data = {}
		data['company_obj'] = company_obj
		data['followed'] = followed
		#print(company_user_list)
		data['companyAdmins'] = str(';'.join(company_admin_list))
		mainData.append(data)
		for mainquestion in latest_questions:
			data = {}
			data ['question'] = mainquestion
			subscribers = mainquestion.subscriber_set.count()
			data['votes'] = mainquestion.voted_set.count()
			data['subscribers'] = subscribers
			data['subscribed'] = sub_que
			data['expired'] = False
			data['upvoteCount'] = mainquestion.upvoteCount
			if mainquestion.expiry and mainquestion.expiry < curtime:
				data['expired'] = True
			user_already_voted = False
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(user=user,question=mainquestion)
				if question_user_vote:
					user_already_voted = True
			# print(mainquestion,user_already_voted,user)
			data['user_already_voted'] = user_already_voted
			mainData.append(data)
		context['data'] = mainData
		#print(context)
		return mainData

class AccessDBView(BaseViewList):

	def post(self,request,*args,**kwargs):
		# print(request.path,request.POST)
		if request.path == "/advanced_analyse":
			pollId = request.POST.get("question")
			# poll = Question.objects.get(pk=pollId)
			min_age = 0
			max_age = 9999
			if request.POST.get("age") != "nochoice":
				if request.POST.get("age") == "<19":
					max_age = 19
				elif request.POST.get("age") == "20-25":
					min_age = 20
					max_age = 25
				elif request.POST.get("age") == "26-30":
					min_age = 26
					max_age = 30
				elif request.POST.get("age") == "31-35":
					min_age = 31
					max_age = 35
				elif request.POST.get("age") == "36-50":
					min_age = 36
					max_age = 50
				elif request.POST.get("age") == ">50":
					min_age = 50
			gender = ""
			if request.POST.get("gender") != "nochoice":
				gender = request.POST.get("gender").lower()
			profession = ""
			if request.POST.get("profession") != "nochoice":
				profession = request.POST.get("profession").lower()
			country = ""
			if request.POST.get("country") != "nochoice":
				country = request.POST.get("country").lower()
			state = ""
			if request.POST.get("state") != "nochoice":
				state = request.POST.get("state").lower()
			response_dic = {}
			total_votes = 0
			# print(min_age,max_age,gender,profession)
			for idx,choice in enumerate(Choice.objects.filter(question_id=pollId)):
				choice_text = "Choice"+str(idx+1)
				response_dic[choice_text] = 0
				for vote in Vote.objects.filter(choice_id=choice.id):
					user_age = vote.user.extendeduser.calculate_age()
					user_gender = vote.user.extendeduser.gender.lower()
					user_prof = vote.user.extendeduser.profession.lower()
					user_country = vote.user.extendeduser.country.lower()
					user_state = vote.user.extendeduser.state.lower()
					add_cnt = True
					# print(user_age,user_gender,user_prof,user_prof != profession,profession,user_country,user_state)
					if not (user_age >= min_age and user_age <= max_age):
						add_cnt = False
					if gender and user_gender != gender:
						add_cnt = False
					if profession and user_prof != profession:
						add_cnt = False
					if state and user_state != state:
						add_cnt = False
					if country and user_country != country:
						add_cnt = False
					if add_cnt:
						response_dic[choice_text] += 1
						total_votes += 1
			response_dic['total_votes'] = total_votes
			# print(response_dic)
			return HttpResponse(json.dumps(response_dic), content_type='application/json')

class TriviaPView(BaseViewList):
	context_object_name = 'trivias'
	
	def get_template_names(self, **kwargs):
		template_name = 'trivia/trivia.html'
		return [template_name]

	def get_queryset(self):
		context = {}
		triviaList = Trivia.objects.order_by('-pub_date')
		for trivia in triviaList:
			print(trivia.trivia_body)
		context['trivias'] = triviaList
		return triviaList
	
