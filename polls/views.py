import os,linecache
import sys
from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound
from django.views import generic
from django.core.mail import send_mail
from polls.models import Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory,QuestionUpvotes,Survey,Survey_Question,SurveyWithCategory,SurveyVoted,VoteText,VoteApi
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
from login.models import ExtendedGroup,ExtendedGroupFuture
from django.contrib.auth.models import Group
from django.db.models import Count
import requests
import operator

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
					latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=True)
				elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
					latest_questions = latest_questions
				elif request.GET.get('tab') == 'leastvoted':
					latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=False)
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
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=False)
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
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=False)
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
			data['votes'] += VoteApi.objects.filter(question=mainquestion).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count()
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
		context['votes'] = context['question'].voted_set.count()
		context['votes'] += VoteApi.objects.filter(question=context['question']).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count()
		return context

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = request.POST.get('question')
		question = Question.objects.get(pk=questionId)
		queSlug = question.que_slug
		queBet = request.POST.get('betAmountHidden')
		points = 0
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
						user.extendeduser.credits += 20
						points = 20
						user.extendeduser.save()
					else:
						if question.privatePoll:
							user.extendeduser.credits += 20
							points = 20
						else:
							user.extendeduser.credits += 10 #for voting on normal question
							points = 10
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
		if request.is_ajax():
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
			makeFeatured = request.POST.get('makeFeatured',False)
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
			makeFeaturedError = ""
			if makeFeatured and user.extendeduser.credits - 100 >= 0:
				home_visible = 1
				if not (edit and question.home_visible == 1):
					user.extendeduser.credits -= 100
					user.extendeduser.save()
			elif makeFeatured:
				if not (edit and question.home_visible == 1):
					makeFeaturedError += "Not Enough pCoins. Please contact support.<br>"
			# return if any errors
			betError = ""
			if bet and isPrivate:
				betError += "Prediction Poll cannot be private.<br>"
			if bet and not qExpiry:
				betError += "Prediction Poll should have expiry.<br>"
			if bet and qExpiry and (qExpiry > curtime + datetime.timedelta(days=7)):
				betError += "Prediction Poll expiry should not be more that 7 days.<br>"
			if makeFeatured and isPrivate:
				makeFeaturedError += "Featured Poll cannot be private.<br>"
			if makeFeaturedError:
				errors['makeFeaturedError'] = makeFeaturedError
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
			print("--------------------------------",errors or ajax,errors,ajax)
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
				question.home_visible = home_visible
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
	if user.is_authenticated():	
		email = user.email
		extendeduserGroups = ExtendedGroupFuture.objects.filter(user_email=email)
		for extendeduserGroup in extendeduserGroups:
			user.groups.add(extendeduserGroup.group)
			extendeduserGroup.delete()

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
	if int(request.POST.get('commentLength')) > 100:
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
		company_obj = Company.objects.filter(company_slug=company_name)
		if company_obj:
			company_obj = company_obj[0]
		else:
			return HttpResponseRedirect("/") #this should be a 404 page
		company_user_list = ExtendedUser.objects.filter(company_id=company_obj.id)
		company_user_list = [x.user_id for x in company_user_list]
		company_admin_list = User.objects.filter(id__in = company_user_list)
		company_admin_list = [x.username for x in company_admin_list]
		followed = Follow.objects.filter(user_id=user.id,target_id__in=company_user_list, deleted_at__isnull=True)
		latest_questions = Question.objects.filter(privatePoll=0,user_id__in=company_user_list).order_by('-pub_date')
		survey_list = Survey.objects.filter(user_id__in = company_user_list)
		s_polls = []
		for survey in survey_list:
			s_polls.extend([ x.question for x in Survey_Question.objects.filter(survey_id=survey.id)])
		latest_questions = [item for item in latest_questions if item not in s_polls]
		latest_questions = list(OrderedDict.fromkeys(latest_questions))
		if request.GET.get('tab') == 'mostvoted':
			latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=True)
		elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
			latest_questions = latest_questions
		elif request.GET.get('tab') == 'leastvoted':
			latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count(), reverse=False)
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
			data['votes'] += VoteApi.objects.filter(question=mainquestion).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count()
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

englandDict = ["Buckinghamshire","Cambridgeshire","Cumbria","Derbyshire","Devon","Dorset","East Sussex","Essex","Gloucestershire","Hampshire","Hertfordshire","Kent","Lancashire","Leicestershire","Lincolnshire","Norfolk","North Yorkshire","Northamptonshire","Nottinghamshire","Oxfordshire","Somerset","Staffordshire","Suffolk","Surrey","Warwickshire","West Sussex","Worcestershire","London, City of","Barking and Dagenham","Barnet","Bexley","Brent","Bromley","Camden","Croydon","Ealing","Enfield","Greenwich","Hackney","Hammersmith and Fulham","Haringey","Harrow","Havering","Hillingdon","Hounslow","Islington","Kensington and Chelsea","Kingston upon Thames","Lambeth","Lewisham","Merton","Newham","Redbridge","Richmond upon Thames","Southwark","Sutton","Tower Hamlets","Waltham Forest","Wandsworth","Westminster","Barnsley","Birmingham","Bolton","Bradford","Bury","Calderdale","Coventry","Doncaster","Dudley","Gateshead","Kirklees","Knowsley","Leeds","Liverpool","Manchester","Newcastle upon Tyne","North Tyneside","Oldham","Rochdale","Rotherham","St. Helens","Salford","Sandwell","Sefton","Sheffield","Solihull","South Tyneside","Stockport","Sunderland","Tameside","Trafford","Wakefield","Walsall","Wigan","Wirral","Wolverhampton","Bath and North East Somerset","Bedford","Blackburn with Darwen","Blackpool","Bournemouth","Bracknell Forest","Brighton and Hove","Bristol, City of","Central Bedfordshire","Cheshire East","Cheshire West and Chester","Cornwall","Darlington","Derby","Durham","East Riding of Yorkshire","Halton","Hartlepool","Herefordshire","Isle of Wight","Isles of Scilly","Kingston upon Hull","Leicester","Luton","Medway","Middlesbrough","Milton Keynes","North East Lincolnshire","North Lincolnshire","North Somerset","Northumberland","Nottingham","Peterborough","Plymouth","Poole","Portsmouth","Reading","Redcar and Cleveland","Rutland","Shropshire","Slough","South Gloucestershire","Southampton","Southend-on-Sea","Stockton-on-Tees","Stoke-on-Trent","Swindon","Telford and Wrekin","Thurrock","Torbay","Warrington","West Berkshire","Wiltshire","Windsor and Maidenhead","Wokingham","York"];

nothernIreLand = ['Antrim','Ards','Armagh','Ballymena','Ballymoney','Banbridge','Belfast','Carrickfergus','Castlereagh','Coleraine','Cookstown','Craigavon','Derry','Down','Dungannon and South Tyrone','Fermanagh','Larne','Limavady','Lisburn','Magherafelt','Moyle','Newry and Mourne District','Newtownabbey','North Down','Omagh','Strabane'];

scotland = ["Aberdeen City","Aberdeenshire","Angus","Argyll and Bute","Clackmannanshire","Dumfries and Galloway","Dundee City","East Ayrshire","East Dunbartonshire","East Lothian","East Renfrewshire","Edinburgh, City of","Eilean Siar","Falkirk","Fife","Glasgow City","Highland","Inverclyde","Midlothian","Moray","North Ayrshire","North Lanarkshire","Orkney Islands","Perth and Kinross","Renfrewshire","Scottish Borders, The","Shetland Islands","South Ayrshire","South Lanarkshire","Stirling","West Dunbartonshire","West Lothian"];

wales = ["Blaenau Gwent","Bridgend","Caerphilly","Cardiff","Carmarthenshire","Ceredigion","Conwy","Denbighshire","Flintshire","Gwynedd","Isle of Anglesey","Merthyr Tydfil","Monmouthshire","Neath Port Talbot","Newport","Pembrokeshire","Powys","Rhondda, Cynon, Taff","Swansea","Torfaen","Wrexham","Vale of Glamorgan, The"];

regionDict = {
	"IN":"India","AZ":"Azerbaijan","US":"USA","PK":"Pakistan","GB":"United Kingdom","AU":"Australia","CA":"Canada","PH":"Philippines","AQ":"Antartica","BB":"Barbados","DE":"Germany","SJ":"Svalbard","AF":"Afghanistan","DZ":"Algeria","AL":"Albania","AS":"American Samoa","AO":"Angola","AI":"Anguilla","AG":"Antigua and Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BR":"Brazil","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia and Herzegovina","CN":"China","DE":"Germany","DK":"Denmark","NL":"Netherlands","PK":"Pakistan","ZW":"Zimbabwe","ZM":"Zambia","ZA":"South Africa","CH":"Switzerland","TH":"Thailand","SG":"Singapore","SE":"Sweden","TR":"Turkey","QA":"Qatar","RE":"Reunion","RO":"Romania","SA":"Saudi Arabia","RW":"Rwanda","JP":"Japan","KE":"Kenya","NO":"Norway","NP":"Nepal","PL":"Poland","NZ":"New Zealand","GB-SCT":"Scotland","EG":"Egypt"
}

class AccessDBView(BaseViewList):

	def post(self,request,*args,**kwargs):
		try:
			# print(request.path,request.POST)
			if request.path == "/advanced_analyse_choice":
				pollId = request.POST.get("question")
				choiceId = request.POST.get("choice")
				stateContry = request.POST.get("stateContry","")
				response_dic = {}
				# get gender count
				gender_dic = {}
				gender_dic['M'] = 0
				gender_dic['F'] = 0
				gender_dic['D'] = 0
				# get age count
				age_dic = {}
				age_dic['over_50'] = 0
				age_dic['bet_36_50'] = 0
				age_dic['bet_31_35'] = 0
				age_dic['bet_26_30'] = 0
				age_dic['bet_20_25'] = 0
				age_dic['under_19'] = 0
				# get profession count
				prof_dic = {}
				# get country count
				country_dic = {}
				# get state count
				state_dic = {}
				vote_list = []
				email_list_voted = []
				if choiceId == "nochoice":
					vote_list = Voted.objects.filter(question_id=pollId)
					vote_api_list = VoteApi.objects.filter(question_id=pollId)
				else:
					vote_list = Vote.objects.filter(choice_id=choiceId)
					vote_api_list = VoteApi.objects.filter(choice_id=choiceId)
				for vote in vote_list:
					user_extendeduser = vote.user.extendeduser
					email_list_voted.append(vote.user.email)
					gender_dic[user_extendeduser.gender] += 1
					user_age = user_extendeduser.calculate_age()
					if user_age > 50:
						age_dic['over_50'] += 1
					elif user_age > 35:
						age_dic['bet_36_50'] += 1
					elif user_age > 30:
						age_dic['bet_31_35'] += 1
					elif user_age > 25:
						age_dic['bet_26_30'] += 1
					elif user_age > 19:
						age_dic['bet_20_25'] += 1
					elif user_age > 0:
						age_dic['under_19'] += 1
					prof_dic[user_extendeduser.profession] = prof_dic.get(user_extendeduser.profession,0) + 1
					country = user_extendeduser.country
					if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
						country = 'United Kingdom'
					country_dic[country] = country_dic.get(country,0) + 1
					state = user_extendeduser.state
					if country == stateContry:
						if country == 'United Kingdom':
							if state in englandDict:
								state_dic['England'] = state_dic.get('England',0) + 1
							elif state in nothernIreLand:
								state_dic['Northern Ireland'] = state_dic.get('Northern Ireland',0) + 1
							elif state in scotland:
								state_dic['Scotland'] = state_dic.get('Scotland',0) + 1
							elif state in wales:
								state_dic['Wales'] = state_dic.get('Wales',0) + 1
						else:
							state_dic[state] = state_dic.get(state,0) + 1
				for vote in vote_api_list:
					if vote.age and vote.profession and vote.gender:
						gender_dic[vote.gender] += 1
						user_age = vote.age
						if user_age > 50:
							age_dic['over_50'] += 1
						elif user_age > 35:
							age_dic['bet_36_50'] += 1
						elif user_age > 30:
							age_dic['bet_31_35'] += 1
						elif user_age > 25:
							age_dic['bet_26_30'] += 1
						elif user_age > 19:
							age_dic['bet_20_25'] += 1
						elif user_age > 0:
							age_dic['under_19'] += 1
						prof_dic[vote.profession] = prof_dic.get(vote.profession,0) + 1
						country = vote.country
						if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
							country = 'United Kingdom'
						country_dic[country] = country_dic.get(country,0) + 1
						state = vote.state
						if country == stateContry:
							if country == 'United Kingdom':
								if state in englandDict:
									state_dic['England'] = state_dic.get('England',0) + 1
								elif state in nothernIreLand:
									state_dic['Northern Ireland'] = state_dic.get('Northern Ireland',0) + 1
								elif state in scotland:
									state_dic['Scotland'] = state_dic.get('Scotland',0) + 1
								elif state in wales:
									state_dic['Wales'] = state_dic.get('Wales',0) + 1
							else:
								state_dic[state] = state_dic.get(state,0) + 1
				response_dic["state"] = state_dic
				response_dic["country"] = country_dic
				response_dic["profession"] = prof_dic
				response_dic["gender"] = gender_dic
				response_dic["age"] = age_dic
				return HttpResponse(json.dumps(response_dic), content_type='application/json')
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
				total_votes_extra = 0
				choices = []
				for idx,choice in enumerate(Choice.objects.filter(question_id=pollId)):
					choice_dic = {}
					choice_text = "Choice"+str(idx+1)
					choice_dic["key"] = choice_text
					choice_dic["val"] = 0
					choice_dic["extra_val"] = 0
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
							choice_dic["val"] += 1
							total_votes += 1
							choice_dic["extra_val"] += 1
							total_votes_extra += 1
					for vote in VoteApi.objects.filter(choice_id=choice.id):
						if vote.age and vote.profession and vote.gender:
							user_age = vote.age
							user_gender = vote.gender.lower()
							user_prof = vote.profession.lower()
							user_country = vote.country.lower()
							user_state = vote.state.lower()
							add_cnt = True
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
								choice_dic["val"] += 1
								total_votes += 1
						choice_dic["extra_val"] += 1
						total_votes_extra += 1
					choices.append(choice_dic)
				response_dic['choices'] = choices
				response_dic['total_votes'] = total_votes
				response_dic['total_votes_extra'] = total_votes_extra
				# print(response_dic)
				return HttpResponse(json.dumps(response_dic), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

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

class CreateSurveyView(BaseViewList):
	def post(self, request, *args, **kwargs):
		try:
			print(request.POST)
			print(request.GET)
			edit = False
			curtime = datetime.datetime.now();
			survey_id = -1
			qExpiry = None
			if request.GET.get("sid"):
				edit = True
				survey_id = int(request.GET.get("sid"))
				survey = Survey.objects.get(pk=request.GET.get("sid"))
				if request.POST.get("oldExpiryTime") != "clean":
					curtime = timezone.now()
					qExpiry = survey.expiry
			user = request.user
			post_data = request.POST
			errors = {}
			survey_name = post_data.get("surveyName").strip()
			survey_desc = post_data.get("surveyDescription")
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]
			surveyError = ""
			if not survey_name:
				surveyError += "Survey Name is Required<br>"
			# print(qeyear, qemonth, qeday, qehr, qemin, qeap)
			if qeyear != 0 or qemonth != 0 or qeday != 0 or qehr != 0 or qemin != -1: 
				if qeap.lower() == 'pm' and qehr != 12:
					qehr = qehr + 12
				elif qeap.lower() == 'am' and qehr == 12:
					qehr = 0
				try:
					curtime = datetime.datetime.now()
					qExpiry = datetime.datetime(qeyear, qemonth, qeday,hour=qehr,minute=qemin)
					if qExpiry < curtime:
						raise Exception
				except:
					surveyError += "Invalid date time<br>"
			selectedCats = request.POST.get('selectedCategories','').split(",")
			selectedGnames = request.POST.get('selectedGroups','').split(",")
			if not list(filter(bool, selectedCats)):
				surveyError += "Please Select a category<br>"
			question_count = json.loads(post_data.get("question_count"))
			polls_list = []
			print(question_count)
			if len(question_count) < 1:
				surveyError += "Atleast 1 question is required<br>"
			if surveyError:
				errors['surveyError'] = surveyError
			imagePathList = []
			for que_index in question_count:
				poll = {}
				print(que_index)
				print(post_data.get("qText"+str(que_index)))
				que_text = post_data.get("qText"+str(que_index)).strip()
				que_desc = post_data.get("qDesc"+str(que_index)).strip()
				que_type = post_data.get("qType"+str(que_index)).strip()
				protectResult = post_data.get("protectResult"+str(que_index),False)
				poll['text'] = que_text
				poll['desc'] = que_desc
				poll['type'] = que_type
				poll['protectResult'] = protectResult
				choices = []
				images = []
				queError = ""
				if not que_text:
					queError += "Question is required.<br>"
				if que_type != "text":
					choice_list = json.loads(post_data.get("choice_count")).get(que_index)
					print(choice_list)
					if len(choice_list) < 2:
						queError += "Atleast 2 choices are required"
					elif len(choice_list) > 5:
						queError += "Maximum 5 choices can be provided"
					for choice_count in choice_list:
						choice_elem_id = 'questionDiv'+que_index+'choice'+str(choice_count)
						choice_image_edit_elem_id = 'questionDiv'+que_index+'imagechoice'+str(choice_count)
						choice = request.POST.getlist(choice_elem_id)[0].strip()
						choices.append(choice)
						if edit and request.POST.get(choice_image_edit_elem_id,""):
							choiceid = request.POST.get(choice_image_edit_elem_id).split("---")[1]
							choiceImage = Choice.objects.get(pk=choiceid).choice_image
							imagePathList.append(choiceImage.path)
						else:
							choiceImage = request.FILES.get(choice_elem_id,"")
						images.append(choiceImage)
						if not choice and not choiceImage:
							errors[choice_elem_id] = "Choice required"
					if len(choices)!=len(set(choices)):
						queError += "Please provide different choices<br>"
				if queError:
					errors["qText"+str(que_index)] = queError
				poll['choice_texts'] = choices
				poll['choice_images'] = images
				polls_list.append(poll)
			print(polls_list)
			print(errors)
			if errors:
				return HttpResponse(json.dumps(errors), content_type='application/json')
			else:
				survey = createSurvey(survey_id,survey_name,survey_desc,qExpiry,curtime,user,selectedCats)
				createSurveyPolls(survey,polls_list,curtime,user,qExpiry,edit,imagePathList)
				url = reverse('polls:survey_vote', kwargs={'pk':survey.id,'survey_slug':survey.survey_slug})
				if list(filter(bool, selectedGnames)):
					for gName in selectedGnames:
						if gName:
							gName = request.user.username+'_'+request.user.extendeduser.company.name+'-'+gName
							group_user_set = Group.objects.filter(name=gName)[0].user_set.all()
							for group_user in group_user_set:
								group_user_email = group_user.email
								msg = EmailMessage(subject="Invitation", from_email=request.user.email,to=[group_user_email])
								msg.template_name = "group-mail-question"
								msg.global_merge_vars = {
				                    'inviter': request.user.first_name,
				                    'companyname':request.user.extendeduser.company.name,
				                    'questionUrl':"www.askbypoll.com"+url,
				                    'questionText':survey.survey_name
				                }
								msg.send()
			errors['success'] = True
			errors['id'] = survey.id
			errors['survey_slug'] = survey.survey_slug
			return HttpResponse(json.dumps(errors), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

def createSurvey(survey_id,survey_name,survey_desc,qExpiry,curtime,user,selectedCats):
	try:
		survey = None
		if survey_id > 0:
			survey = Survey.objects.get(pk=survey_id)
			survey.survey_name = survey_name
			survey.description = survey_desc
			survey.expiry = qExpiry
		else:
			survey = Survey( user=user, pub_date=curtime, created_at=curtime, survey_name=survey_name, description=survey_desc, expiry=qExpiry)
		survey.save()
		if survey_id > 0:
			for scat in survey.surveywithcategory_set.all():
				scat.delete()
		if list(filter(bool, selectedCats)):
			for cat in selectedCats:
				if cat:
					category = Category.objects.filter(category_title=cat)[0]
					scat,created = SurveyWithCategory.objects.get_or_create(survey=survey,category=category)
					# scat.save()
		return survey
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def createSurveyPolls(survey,polls_list,curtime,user,qExpiry,edit,imagePathList):
	try:
		if edit:
			survey_polls = Survey_Question.objects.filter(survey=survey)
			print(survey_polls)
			for poll in survey_polls:
				print(poll)
				question = poll.question
				if poll.question_type != "text":
					for choice in question.choice_set.all():
						if choice.choice_image:
							if os.path.isfile(choice.choice_image.path) and choice.choice_image.path not in imagePathList:
								os.remove(choice.choice_image.path)
						choice.delete()
				question.delete()
		for poll in polls_list:
			protectResult = 0
			if poll['protectResult']:
				protectResult = 1
			question = Question(user=user, pub_date=curtime, created_at=curtime, expiry=qExpiry, home_visible=0, question_text=poll['text'], description=poll['desc'], protectResult=protectResult)
			question.save()
			for index,choice_text in enumerate(poll['choice_texts']):
				choice = Choice(question=question,choice_text=choice_text,choice_image=poll['choice_images'][index])
				choice.save()
			survey_que = Survey_Question(survey=survey,question=question,question_type=poll['type'])
			survey_que.save()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class SurveyVoteView(BaseViewDetail):
	model = Survey
	
	def get_template_names(self):
		template_name = 'polls/voteSurvey.html'
		survey = self.get_object()
		survey.numViews +=1
		survey.save()
		return [template_name]
	
	def get_context_data(self, **kwargs):

		context = super(SurveyVoteView, self).get_context_data(**kwargs)
		user = self.request.user
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
			question_user_vote = SurveyVoted.objects.filter(user=user,survey=context['survey'])
			if question_user_vote:
				question_user_vote = question_user_vote[0]
				if question_user_vote.survey_question_count == question_user_vote.user_answer_count:
					user_already_voted = True
			context['user_already_voted'] = user_already_voted
		context['expired'] = False
		if context['survey'].expiry and context['survey'].expiry < timezone.now():
			context['expired'] = True
		context['polls'] = []
		for x in Survey_Question.objects.filter(survey_id=context['survey'].id):
			poll_dict = {"poll":x.question,"type":x.question_type}
			poll_dict['user_already_voted'] = False
			question_user_vote = Voted.objects.filter(user=user,question=x.question)
			if question_user_vote:
				poll_dict['user_already_voted'] = True
				if x.question_type == "text":
					poll_dict['answer'] = VoteText.objects.filter(user_id=user.id,question_id=x.question.id)[0].answer_text
			context['polls'].append(poll_dict)
		return context

	def post(self, request, *args, **kwargs):
		try:
			print(request.POST,request.path)
			user = request.user
			questionId = request.POST.get('question')
			question = Question.objects.get(pk=questionId)
			que_type = request.POST.get('questionType')
			queSlug = question.que_slug
			if user.is_authenticated():
				choice_list = request.POST.getlist('choice'+str(questionId))
				print(choice_list)
				choice_list = list(filter(None, choice_list))
				print(choice_list)
				if choice_list:
					if que_type != "text":
						for choiceId in choice_list:
							choice = Choice.objects.get(pk=choiceId)
							subscribed, created = Subscriber.objects.get_or_create(user=user, question=question)
							voted,created = Voted.objects.get_or_create(user=user, question=question)
							if que_type == "radio":
								if created:
									vote,created = Vote.objects.get_or_create(user=user, choice=choice)
							else:
								vote,created = Vote.objects.get_or_create(user=user, choice=choice)
					else:
						voted,created = Voted.objects.get_or_create(user=user, question=question)
						if created:
							subscribed, created = Subscriber.objects.get_or_create(user=user, question=question)
							voteText = VoteText(question=question,user=user,answer_text=choice_list[0])
							voteText.save()
					survey = Survey_Question.objects.filter(question_id=question.id)[0].survey
					survey_question_count = Survey_Question.objects.filter(survey_id=survey.id).count()
					survey_voted,created = SurveyVoted.objects.get_or_create(survey=survey,user=user,survey_question_count=survey_question_count)
					survey_voted.user_answer_count += 1
					survey_voted.save()
				else:
					data={}
					data[str(questionId)] = "Please enter an answer"
					return HttpResponse(json.dumps(data),content_type='application/json')
				return HttpResponse(json.dumps({}),content_type='application/json')
			else:
					if request.is_ajax():
						return HttpResponse(json.dumps({}),content_type='application/json')
					next_url = request.path
					extra_params = '?next=%s'%next_url
					url = reverse('account_login')
					full_url = '%s%s'%(url,extra_params)
					if request.is_ajax():
						return HttpResponse(json.dumps({}),content_type='application/json')
					return HttpResponseRedirect(full_url)
			return HttpResponseRedirect(url)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class SurveyEditView(BaseViewDetail):
	model = Survey
	
	def get_template_names(self):
		template_name = 'polls/editSurvey.html'
		return [template_name]

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		context = super(SurveyEditView, self).get_context_data(object=self.object)
		survey = context['survey']
		context["clone"] = False
		# print(request.path)
		if request.path.startswith("/clonesurvey"):
			context["clone"] = True
		canEdit = True
		if (survey.surveyvoted_set.count() > 0 and not request.user.is_superuser):
			canEdit = False
		if survey.user != request.user and not request.user.is_superuser:
			canEdit = False
		if not canEdit and not request.path.startswith("/clonesurvey"):
			url = reverse('polls:survey_vote', kwargs={'pk':survey.id,'survey_slug':survey.survey_slug})
			return HttpResponseRedirect(url)
		else:
			context["data"] = Category.objects.all()
			if survey.expiry:
				tim = survey.expiry#.strftime("%Y-%m-%d %H:%M:%S")
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
			for cat in survey.surveywithcategory_set.all():
				categories += cat.category.category_title+","
			context["survey_categories"] = categories
			context['polls'] = []
			surveyResultProtected = True
			for x in Survey_Question.objects.filter(survey_id=survey.id):
				if not x.question.protectResult:
					surveyResultProtected = False
				poll_dict = {"poll":x.question,"type":x.question_type}
				context['polls'].append(poll_dict)
			context["surveyResultProtected"] = surveyResultProtected
			return self.render_to_response(context)

class SurveyDeleteView(BaseViewDetail):
	model = Survey
	
	def get_context_data(self, **kwargs):
		return super(SurveyDeleteView, self).get_context_data(**kwargs)
	
	def get(self, request, *args, **kwargs):
		url = reverse('polls:index')
		survey = self.get_object()
		survey_polls = Survey_Question.objects.filter(survey=survey)
		if survey.user == request.user or request.user.is_superuser:
			for poll in survey_polls:
				question = poll.question
				if poll.question_type != "text":
					for choice in question.choice_set.all():
						if choice.choice_image:
							if os.path.isfile(choice.choice_image.path) and choice.choice_image.path:
								os.remove(choice.choice_image.path)
				question.delete()
			survey.delete()
		return HttpResponseRedirect(url)

def survey_mail(request):
	try:
		print(request.POST)
		errors = {}
		url = reverse('polls:survey_vote', kwargs={'pk':int(request.POST.get('shareSurveyId','')),'survey_slug':request.POST.get('shareSurveySlug','')})
		selectedGnames = request.POST.get('shareselectedGroups','').split(",")
		if list(filter(bool, selectedGnames)):
			for gName in selectedGnames:
				if gName:
					gName = request.user.username+'_'+request.user.extendeduser.company.name+'-'+gName
					group_user_set = Group.objects.filter(name=gName)[0].user_set.all()
					for group_user in group_user_set:
						group_user_email = group_user.email
						msg = EmailMessage(subject="Invitation", from_email=request.user.email,to=[group_user_email])
						msg.template_name = "group-mail-survey"
						msg.global_merge_vars = {
		                    'inviter': request.user.first_name,
		                    'companyname':request.user.extendeduser.company.name,
		                    'questionUrl':"www.askbypoll.com"+url,
		                    'questionText':request.POST.get('shareSurveyName','')
		                }
						msg.send()
		return HttpResponse(json.dumps(errors), content_type='application/json')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def embed_poll(request):
	try:
		print("embed_poll")
		pollId = int(request.GET.get('pollId'))
		callback = request.GET.get('callback', '')
		analysisNeeded = True
		if request.GET.get('analysisNeeded'):
			analysisNeeded = False
		req = {}
		poll = Question.objects.get(pk=pollId)
		logo_html = '<a href="http://www.askbypoll.com" target="new"><img class="askbypoll-embed-poll-logo" src="https://www.askbypoll.com/static/newLogo.png"></a>'
		site_link_html = '<div class="askbypoll-embed-poll-powered-by"><p class="askbypoll-embed-poll-powered-by-p">Powered By <a class="askbypoll-embed-poll-askbypoll-url" href="https://www.askbypoll.com" target="new">AskByPoll</span></p></div>'
		choices = Choice.objects.filter(question_id=pollId)
		choice_html = '<div class="askbypoll-embed-poll-question-choices" id="askbypoll-embed-poll-question-choices---'+str(pollId)+'">'
		for choice in choices:
			if choice.choice_image :
				choice_html += '<div class="askbypoll-embed-poll-question-choice" id="askbypoll-embed-poll-question-choice---'+str(choice.id)+'">'
				choice_html += '<img class="askbypoll-embed-poll-question-choice-img" id="askbypoll-embed-poll-question-choice-img---'+str(choice.id)+'" src="https://www.askbypoll.com/media/choices/'+choice.get_file_name()+'">'
				choice_html += '<div class="askbypoll-progress-bar-Img-div" style="position:relative;" >'
				choice_html += '<p class="askbypoll-embed-poll-question-choice-img-text" id="askbypoll-embed-poll-question-choice---text-'+str(choice.id)+'">'
				choice_html += choice.choice_text
				choice_html += '</p>'
				choice_html += '<div class="askbypoll-embed-progress-bar" id="askbypoll-embed-progress-bar---'+str(choice.id)+'"></div>'
				choice_html += '<span class="askbypoll-poll-result" id="askbypoll-result-choice---'+str(choice.id)+'"></span>'
				choice_html += '</div></div>'
			else:
				choice_html += '<div class="askbypoll-embed-poll-choice" id="askbypoll-embed-poll-choice---'+str(choice.id)+'">'
				choice_html += '<p class="askbypoll-embed-poll-question-choice-text" id="askbypoll-embed-poll-question-choice-text---'+str(choice.id)+'">'
				choice_html += choice.choice_text
				choice_html += '</p>'
				choice_html += '<div class="askbypoll-embed-progress-bar" id="askbypoll-embed-progress-bar---'+str(choice.id)+'"></div>'
				choice_html += '<span class="askbypoll-poll-result" id="askbypoll-result-choice---'+str(choice.id)+'"></span>'
				choice_html += '</div>'
		choice_html += '</div>'
		question_html = '<div class="askbypoll-embed-poll-question" id="askbypoll-embed-poll-question---'+str(pollId)+'">'
		question_html += '<p class="askbypoll-embed-poll-question-text" id="askbypoll-embed-poll-question-text---'+str(pollId)+'">'
		question_html += poll.question_text
		question_html += '</p></div>'
		html = '<div class="askbypoll-embed-poll-wrapper" id="askbypoll-embed-poll-wrapper---'+str(pollId)+'">'
		if analysisNeeded:
			html += '<div class="askbypoll-embed-overlay" id="askbypoll-embed-overlay---'+str(pollId)+'"><span class="askbypoll-enter-details">Enter Details To Analyse Results</span>'
			html += '<select class="askbypoll-ageField askbypoll-enter" id="askbypoll-age---'+str(pollId)+'" name="age"><option value="notSelected">What\'s your Age Group?</option><option value="16"><19</option><option value="22">20-25</option><option value="28">26-30</option><option value="33">31-35</option><option value="43">36-50</option><option value="55">>50</option></select>'
			html += '<select class="askbypoll-genderField askbypoll-enter" id="askbypoll-gender---'+str(pollId)+'" name="gender"><option value="notSelected">What\'s your Gender</option><option value="Female">Female</option><option value="Male">Male</option><option value="D">Rather Not Say</option></select>'
			html += '<select class="askbypoll-professionField askbypoll-enter" id="askbypoll-profession---'+str(pollId)+'" name="profession"><option value="notSelected">What\'s your Profession</option><option value="Student">Student</option><option value="Politics">Politics</option><option value="Education">Education</option><option value="Information Technology">Information Technology</option><option value="Public Sector">Public Sector</option><option value="Social Services">Social Services</option><option value="Medical">Medical</option><option value="Finance">Finance</option><option value="Manager">Manager</option><option value="Others">Others</option></select><input type="text" class="askbypoll-emailField askbypoll-enter" id="askbypoll-email---'+str(pollId)+'" placeholder="What\'s your Email. We hate spam as much as you do." name="email"><button id="askbypoll-closeButton---'+str(pollId)+'" class="askbypoll-close-button"> Close </button> <button id="askbypoll-nextButton---'+str(pollId)+'" class="askbypoll-button"> Show me </button>'
			html += '</div>'
		html += logo_html
		html += question_html
		html += choice_html
		html += site_link_html
		html += '</div>'
		req ['html'] = html
		response = json.dumps(req)
		response = callback + '(' + response + ');'
		return HttpResponse(response,content_type="application/json")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def vote_embed_poll(request):
	try:
		callback = request.GET.get('callback', '')
		choiceId = int(request.GET.get('choiceId',0))
		pollId = int(request.GET.get('pollId'))
		alreadyVoted = request.GET.get('alreadyVoted','false')
		ipAddress = getIpAddress(request)
		# ipAddress = '139.130.4.22'

		question = Question.objects.get(pk=pollId)
		req = {}

		#if((not existingVotes or timeDifference.total_seconds()>86400) and not(choiceId == 0)):
		if((not alreadyVoted == 'true') and not(choiceId == 0)):
			url = "http://api.db-ip.com/addrinfo?addr="+ipAddress+"&api_key=ab6c13881f0376231da7575d775f7a0d3c29c2d5"
			dbIpResponse = requests.get(url)
			locationData = dbIpResponse.json()
			votedChoice = Choice.objects.get(pk=choiceId)
			votedChoiceFromApi = VoteApi(choice=votedChoice,question=question,country=regionDict[locationData['country']] ,city=locationData['city'],state=locationData['stateprov'],ipAddress=ipAddress)
			votedChoiceFromApi.save()
			totalVotes = VoteApi.objects.filter(question=question).count()
			email_list_voted = []
			choice_dic = {}
			for voteUser in Vote.objects.filter(choice__in=question.choice_set.all()):
				email_list_voted.append(voteUser.user.email)
				totalVotes += 1
				choice_dic[voteUser.choice.id] = choice_dic.get(voteUser.choice.id,0) + 1
			choices = VoteApi.objects.filter(question=question).exclude(email__in=email_list_voted).values('choice').annotate(choiceCount=Count('choice'))
			result = {}
			for i in choices:
				if totalVotes > 0:
					i['percent'] = round(((i.get('choiceCount')+choice_dic.get(i.get('choice'),0))/totalVotes)*100)
					result[i.get('choice')] = str(i.get('percent'))+'---'+str(i.get('choiceCount')+choice_dic.get(i.get('choice'),0))+'---'+str(totalVotes)
				else:
					result[i.get('choice')] = "0---0---0"
			
			req ['result'] = result
			response = json.dumps(req)
			response = callback + '(' + response + ');'
		else:
			if alreadyVoted == 'true':
				totalVotes = VoteApi.objects.filter(question=question).count()
				email_list_voted = []
				choice_dic = {}
				for voteUser in Vote.objects.filter(choice__in=question.choice_set.all()):
					email_list_voted.append(voteUser.user.email)
					totalVotes += 1
					choice_dic[voteUser.choice.id] = choice_dic.get(voteUser.choice.id,0) + 1
				choices = VoteApi.objects.filter(question=question).exclude(email__in=email_list_voted).values('choice').annotate(choiceCount=Count('choice'))
				result = {}
				for i in choices:
					if totalVotes > 0:
						i['percent'] = round(((i.get('choiceCount')+choice_dic.get(i.get('choice'),0))/totalVotes)*100)
						result[i.get('choice')] = str(i.get('percent'))+'---'+str(i.get('choiceCount')+choice_dic.get(i.get('choice'),0))+'---'+str(totalVotes)
					else:
						result[i.get('choice')] = "0---0---0"
				req ['result'] = result
			else:
				req = {}
			response = json.dumps(req)
			response = callback + '(' + response + ');'

		return HttpResponse(response,content_type="application/json")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def results_embed_poll(request):
	try:
		print(request.GET)
		print("Age")
		print(request.GET.get('age',18))
		alreadyVoted = request.GET.get('alreadyVoted','false')
		dataStored = request.GET.get('dataStored','false')
		callback = request.GET.get('callback', '')
		pollId = int(request.GET.get('pollId'))
		poll = Question.objects.get(pk=pollId)
		choices = Choice.objects.filter(question_id=pollId)

		user_age = 0
		gender = "D"
		email = ''
		profession = ''
		print(alreadyVoted, dataStored)
		if alreadyVoted == 'false' and dataStored == 'false':
			if request.GET.get('age'):
				user_age = int(request.GET.get('age',18))
			if request.GET.get('gender',"D") != "notSelected":
				gender = request.GET.get('gender',"D")[0]
			if request.GET.get('profession',"D") != "notSelected":
				profession = request.GET.get('profession','Others')
			email = request.GET.get('email','')
			ipAddress = getIpAddress(request)
			# ipAddress = '139.130.4.22'
			existingVote = VoteApi.objects.filter(question_id=pollId,ipAddress=ipAddress).order_by('-created_at')
			existingVote = existingVote[0]
			existingVote.age = user_age
			existingVote.gender = gender
			existingVote.profession = profession
			existingVote.email = email
			existingVote.save()
			if email and not User.objects.filter(email=email):
				new_user = User(first_name="User",email=email,username=email,password=email)
				new_user.save()
				new_extended_user = ExtendedUser(user=new_user)
				new_extended_user.save()
				if user_age > 0:
					new_extended_user.birthDay = datetime.date.today().year - user_age
				if profession:
					new_extended_user.profession = profession
				new_extended_user.gender = gender
				new_extended_user.country = existingVote.country
				new_extended_user.state = existingVote.state
				new_extended_user.city = existingVote.city
				new_extended_user.save()
				subscribed, created = Subscriber.objects.get_or_create(user=new_user, question=poll)
				voted, created = Voted.objects.get_or_create(user=new_user, question=poll)
				vote, created = Vote.objects.get_or_create(user=new_user, choice=existingVote.choice)
			elif email:
				old_user = User.objects.filter(email=email)[0]
				subscribed, created = Subscriber.objects.get_or_create(user=old_user, question=poll)
				voted, created = Voted.objects.get_or_create(user=old_user, question=poll)
				vote, created = Vote.objects.get_or_create(user=old_user, choice=existingVote.choice)
		choice_data = {}
		percent = {}
		totalVotes = 0
		for index,choice in enumerate(choices):
			choice_data[choice.id] = "choice" + str(index)
			percent["choice" + str(index)] = 0
		# get gender count
		gender_dic = {}
		gender_dic['M'] = 0
		gender_dic['F'] = 0
		gender_dic['D'] = 0
		# get age count
		age_dic = {}
		age_dic['over_50'] = 0
		age_dic['bet_36_50'] = 0
		age_dic['bet_31_35'] = 0
		age_dic['bet_26_30'] = 0
		age_dic['bet_20_25'] = 0
		age_dic['under_19'] = 0
		# get profession count
		prof_dic = {}
		# get country count
		country_dic = {}
		# get state count
		state_dic = {}
		email_list_voted = []
		for voteUser in Vote.objects.filter(choice__in=choices):
			email_list_voted.append(voteUser.user.email)
			totalVotes += 1
			percent[choice_data[voteUser.choice_id]] = percent.get(choice_data[voteUser.choice_id],0) + 1
			voteApi = voteUser.user.extendeduser
			gender = voteApi.gender
			user_age = voteApi.calculate_age()
			profession = voteApi.profession
			country = voteApi.country
			gender_dic[gender] += 1
			if user_age > 50:
				age_dic['over_50'] += 1
			elif user_age > 35:
				age_dic['bet_36_50'] += 1
			elif user_age > 30:
				age_dic['bet_31_35'] += 1
			elif user_age > 25:
				age_dic['bet_26_30'] += 1
			elif user_age > 19:
				age_dic['bet_20_25'] += 1
			elif user_age > 0:
				age_dic['under_19'] += 1
			prof_dic[profession] = prof_dic.get(profession,0) + 1
			if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
				country = 'United Kingdom'
			country_dic[country] = country_dic.get(country,0) + 1
		for voteApi in VoteApi.objects.filter(question_id=pollId):
			if email and email in email_list_voted:
				pass
			else:
				totalVotes += 1
				percent[choice_data[voteApi.choice_id]] = percent.get(choice_data[voteApi.choice_id],0) + 1
				gender = voteApi.gender
				user_age = voteApi.age
				profession = voteApi.profession
				country = voteApi.country
				if gender and user_age and profession:
					gender_dic[gender] += 1
					if user_age > 50:
						age_dic['over_50'] += 1
					elif user_age > 35:
						age_dic['bet_36_50'] += 1
					elif user_age > 30:
						age_dic['bet_31_35'] += 1
					elif user_age > 25:
						age_dic['bet_26_30'] += 1
					elif user_age > 19:
						age_dic['bet_20_25'] += 1
					elif user_age > 0:
						age_dic['under_19'] += 1
					prof_dic[profession] = prof_dic.get(profession,0) + 1
					# if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
					# 	country = 'United Kingdom'
					country_dic[country] = country_dic.get(country,0) + 1	
		logo_html = '<a href="http://www.askbypoll.com" target="new"><img class="askbypoll-embed-poll-logo" src="https://www.askbypoll.com/static/newLogo.png"></a>'
		site_link_html = '<div class="askbypoll-embed-poll-powered-by"><p class="askbypoll-embed-poll-powered-by-p">Powered By <a class="askbypoll-embed-poll-askbypoll-url" href="https://www.askbypoll.com" target="new">AskByPoll</span></p></div>'
		html = '<input class="askbypoll-embed-tab-radio" id="askbypoll-tab---1---'+str(pollId)+'" type="radio" name="tabs" checked> <label class="askbypoll-embed-tab-radio-label" for="askbypoll-tab---1---'+str(pollId)+'">Results</label><input class="askbypoll-embed-tab-radio" id="askbypoll-tab---2---'+str(pollId)+'" type="radio" name="tabs"><label class="askbypoll-embed-tab-radio-label" for="askbypoll-tab---2---'+str(pollId)+'">Age</label><input class="askbypoll-embed-tab-radio" id="askbypoll-tab---3---'+str(pollId)+'" type="radio" name="tabs"><label class="askbypoll-embed-tab-radio-label" for="askbypoll-tab---3---'+str(pollId)+'">Gender</label><input class="askbypoll-embed-tab-radio" id="askbypoll-tab---4---'+str(pollId)+'" type="radio" name="tabs"><label class="askbypoll-embed-tab-radio-label" for="askbypoll-tab---4---'+str(pollId)+'">Profession</label><input class="askbypoll-embed-tab-radio" id="askbypoll-tab---5---'+str(pollId)+'" type="radio" name="tabs"><label class="askbypoll-embed-tab-radio-label" for="askbypoll-tab---5---'+str(pollId)+'">Location</label>'
		html += '<section class="askbypoll-embed-content askbypoll-embed-content'+str(pollId)+'" id="askbypoll-content---1---'+str(pollId)+'"><div class="askbypoll-embed-poll-wrapper" id="askbypoll-embed-poll-wrapper---'+str(pollId)+'">'+logo_html+'<div class="askbypoll-embed-poll-question" id="askbypoll-embed-poll-question---'+str(pollId)+'"><p class="askbypoll-embed-poll-question-text" id="askbypoll-embed-poll-question-text---'+str(pollId)+'">'+poll.question_text+'</p></div><div class="askbypoll-embed-poll-question-choices" id="askbypoll-embed-poll-question-choices---'+str(pollId)+'" >'
		# print(choice_data,percent,totalVotes)
		for index,choice in enumerate(choices):
			choice_text = "Option "+str(index)
			# print(percent[choice_data[choice.id]])
			# print(percent[choice_data[choice.id]]/totalVotes)
			choice_percent = int((percent[choice_data[choice.id]]/totalVotes) * 100)
			if choice.choice_text:
				choice_text = choice.choice_text
			if choice.choice_image:
				html += '<div class="askbypoll-embed-poll-question-choice" id="askbypoll-embed-poll-question-choice---'+str(choice.id)+'"><img class="askbypoll-embed-poll-question-choice-img" id="askbypoll-embed-poll-question-choice-img---'+str(choice.id)+'" src="https://www.askbypoll.com/media/choices/'+choice.get_file_name()+'"><div class="askbypoll-progress-bar-Img-div" style="position:relative;"><p class="askbypoll-embed-poll-question-choice-img-text" id="askbypoll-embed-poll-question-choice---text-'+str(choice.id)+'">'+choice_text+'</p><div class="askbypoll-embed-progress-bar" id="askbypoll-embed-progress-bar---'+str(choice.id)+'" style="display: inline-block; width:'+str(choice_percent)+'%; background: yellow;"></div><span class="askbypoll-poll-result" id="askbypoll-result-choice---'+str(choice.id)+'">'+str(choice_percent)+'%</span></div></div>'
			else:
				html += '<div class="askbypoll-embed-poll-choice" id="askbypoll-embed-poll-choice---'+str(choice.id)+'"><p class="askbypoll-embed-poll-question-choice-text" id="askbypoll-embed-poll-question-choice-text---'+str(choice.id)+'">'+choice_text+'</p><div class="askbypoll-embed-progress-bar" id="askbypoll-embed-progress-bar---'+str(choice.id)+'" style="display: inline-block; width: '+str(choice_percent)+'%; background: yellow;"></div><span class="askbypoll-poll-result" id="askbypoll-result-choice---'+str(choice.id)+'">'+str(choice_percent)+'%</span></div>'
		html += '</div><div class="askbypoll-embed-poll-powered-by"><p class="askbypoll-embed-poll-powered-by-p">Powered By <a class="askbypoll-embed-poll-askbypoll-url" href="https://www.askbypoll.com" target="new">AskByPoll</a></p></div></div></section>'
		html += '<section class="askbypoll-embed-content askbypoll-embed-content'+str(pollId)+'" id="askbypoll-content---2---'+str(pollId)+'"><div class="askbypoll-embed-content-div" id="askbypoll-agechart---'+str(pollId)+'" ></div></section>'
		html += '<section class="askbypoll-embed-content askbypoll-embed-content'+str(pollId)+'" id="askbypoll-content---3---'+str(pollId)+'"><div class="askbypoll-embed-content-div" id="askbypoll-genderchart---'+str(pollId)+'" ></div></section>'
		html += '<section class="askbypoll-embed-content askbypoll-embed-content'+str(pollId)+'" id="askbypoll-content---4---'+str(pollId)+'"><div class="askbypoll-embed-content-div" id="askbypoll-professionchart---'+str(pollId)+'" ></div></section>'
		html += '<section class="askbypoll-embed-content askbypoll-embed-content'+str(pollId)+'" id="askbypoll-content---5---'+str(pollId)+'"><div class="askbypoll-embed-content-div" id="askbypoll-regions_div---'+str(pollId)+'" ></div></section>'
		req = {}
		req ['html'] = html
		req["gender_dic"] = gender_dic
		req['age_dic'] = age_dic
		req['prof_dic'] = prof_dic
		req["country_dic"] = country_dic
		response = json.dumps(req)
		response = callback + '(' + response + ');'
		return HttpResponse(response,content_type="application/json")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def getIpAddress(request):
	""" use requestobject to fetch client machine's IP Address """
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')    ### Real IP address of client Machine
	return ip

import xlwt
gender_excel_dic = {
	"M":1,
	"F":2,
	"D":3
}
prof_excel_dic = {
	"Student":1,
	"Politics":2,
	"Education":3,
	"Information Technology":4,
	"Public Sector":5,
	"Social Services":6,
	"Medical":7,
	"Finance":8,
	"Manager":9,
	"Others":10
}
age_excel_dic ={
	1:"Upto 19",
	2:"20 - 25",
	3:"26 - 30",
	4:"31 - 35",
	5:"36 - 50",
	6:"50+"
}

normal_style = xlwt.easyxf(
	"""
	font:name Verdana
	"""
)

border_style = xlwt.easyxf(
	"""
	font:name Verdana;
	border: top thin, right thin, bottom thin, left thin;
	align: vert centre, horiz left;
	"""
)

def excel_view(request):
	 
	survey_id = -1
	survey = ""
	errors = {}
	if request.GET.get("sid"):
		survey_id = int(request.GET.get("sid",-1))
		try:
			survey = Survey.objects.get(pk=survey_id)
		except:
			errors['notfound'] = "Survey provided not found"
			return HttpResponseNotFound(errors,content_type="application/json")
		response = HttpResponse(content_type='application/ms-excel')
		fname = "Survey_%s_Data.xls"%(survey_id)
		response['Content-Disposition'] = 'attachment; filename=%s' % fname
		wb = xlwt.Workbook()
		ws0 = wb.add_sheet('Definitions', cell_overwrite_ok=True)
		ws1 = wb.add_sheet('Raw Data', cell_overwrite_ok=True)
		# write to the description sheet
		write_to_description(ws0)
		# description sheet end
		ws1.write(0,0,"Country",normal_style)
		ws1.write(0,1,"State",normal_style)
		ws1.write(0,2,"Gender",normal_style)
		ws1.write(0,3,"Age Group",normal_style)
		ws1.write(0,4,"Profession",normal_style)
		i = 1
		voted_list = SurveyVoted.objects.filter(survey_id = survey_id)
		for voted in voted_list:
			j = 5
			vote_user = voted.user
			ws1.write(i,0,vote_user.extendeduser.country,normal_style)
			ws1.write(i,1,vote_user.extendeduser.state,normal_style)
			ws1.write(i,2,gender_excel_dic.get(vote_user.extendeduser.gender),normal_style)
			ws1.write(i,3,get_age_group_excel(vote_user.extendeduser.calculate_age()),normal_style)
			ws1.write(i,4,prof_excel_dic.get(vote_user.extendeduser.profession),normal_style)
			for index,survey_question in enumerate(Survey_Question.objects.filter(survey_id = survey_id)):
				question = survey_question.question
				question_type = survey_question.question_type
				excel_text = ""
				choice_list = []
				if question_type != "text":
					choice_list = Choice.objects.filter(question_id=question.id)
				excel_text = "Q"+str(index+1)
				answer_text = ""
				if question_type == "text":
					vote_text = VoteText.objects.filter(user_id=vote_user.id,question_id=question.id)
					if vote_text:
						answer_text = vote_text[0].answer_text
				elif question_type == "radio":
					for c_index,choice in enumerate(choice_list):
						if Vote.objects.filter(user_id=vote_user.id,choice=choice):
							answer_text = str(c_index+1)
				elif question_type == "checkbox":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						if Vote.objects.filter(user_id=vote_user.id,choice=choice):
							answer_text = 1
						ws1.write(0,j,excel_text,normal_style)
						ws1.write(i,j,answer_text,normal_style)
						j += 1
				if question_type != "checkbox":
					ws1.write(0,j,excel_text,normal_style)
					ws1.write(i,j,answer_text,normal_style)
					j += 1
			i += 1
		wb.save(response)
		return response
	errors['notfound'] = "No data provided"
	return HttpResponseNotFound(errors,content_type="application/json")

def write_to_description(ws0):
	ws0.col(0).width = 25*256
	ws0.write(0,0,"Single Select Questions Have 1 as lowest & 5 as highest Rating",normal_style)
	ws0.write(1,0,"Multi Select Questions are displayed as Q_Choice No & its respective rating",normal_style)
	ws0.write_merge(3,3,0,1,"Gender",border_style)
	ws0.write(4,0,"Male",border_style)
	ws0.write(4,1,1,border_style)
	ws0.write(5,0,"Female",border_style)
	ws0.write(5,1,2,border_style)
	ws0.write(6,0,"Not Disclosed",border_style)
	ws0.write(6,1,3,border_style)
	ws0.write_merge(8,8,0,1,"Age Group",border_style)
	x = 9
	for key,val in age_excel_dic.items():
		ws0.write(x,0,val,border_style)
		ws0.write(x,1,key,border_style)
		x += 1
	x += 1
	ws0.write_merge(x,x,0,1,"Profession",border_style)
	x += 1
	sorted_prof_excel_dic = sorted(prof_excel_dic.items(), key=operator.itemgetter(1))
	print(sorted_prof_excel_dic)
	for key_val in sorted_prof_excel_dic:
		ws0.write(x,0,key_val[0],border_style)
		ws0.write(x,1,key_val[1],border_style)
		x += 1

def get_age_group_excel(age):
	res = -1
	if age <= 19:
		res = 1
	elif age >19 and age <=25:
		res = 2
	elif age >25 and age <=30:
		res = 3
	elif age >30 and age <= 35:
		res = 4
	elif age >35 and age <= 50:
		res = 5
	elif age > 50:
		res = 6
	return res

class PDFView(generic.DetailView):
	model = Survey

	def get_template_names(self):
		template_name = "polls/pdf_report_survey.html"
		return [template_name]
	
	def get_context_data(self, **kwargs):
		context = super(PDFView, self).get_context_data(**kwargs)
		survey = context['survey']
		maxVotes = -1
		minVotes = 99999
		maxVotedChoiceList = []
		minVotedChoiceList = []
		survey_questions = Survey_Question.objects.filter(survey_id = survey.id)
		survey_voted = SurveyVoted.objects.filter(survey_id = survey.id)
		surveytotalResponses = len(survey_voted)
		incompleteResponses = 0
		for voted in survey_voted:
			if voted.survey_question_count != voted.user_answer_count:
				incompleteResponses += 1
		completeRate = 0
		# print(surveytotalResponses,incompleteResponses,int((surveytotalResponses-incompleteResponses)/surveytotalResponses))
		if surveytotalResponses > 0:
			completeRate = int(((surveytotalResponses-incompleteResponses)/surveytotalResponses)*100)
		survey_polls = []
		maxVotedQuestionCount = -1
		maxVotedQuestion = -1
		for x in survey_questions:
			questionChoices = x.question.choice_set.all()
			totalResponses = x.question.voted_set.count()
			if maxVotedQuestionCount < totalResponses and x.question_type != "text":
				maxVotedQuestion = x.question.id
				maxVotedQuestionCount = totalResponses
			maxVotedChoice = ""
			maxVotedChoiceStr = ""
			maxVotedCount = -1
			minVotedCount = 99999
			choice_dict = {} 
			choice_vote_count = {}
			total_choice_vote = 0
			choice_vote_count_filter = {}
			total_choice_vote_filter = 0
			age_dict = {}
			gender_dict = {}
			gender_dict['M'] = 0
			gender_dict['F'] = 0
			gender_dict['D'] = 0
			prof_dict = {}
			country_dict = {}
			age_dict_filter = {}
			gender_dict_filter = {}
			gender_dict_filter['M'] = 0
			gender_dict_filter['F'] = 0
			gender_dict_filter['D'] = 0
			prof_dict_filter = {}
			country_dict_filter = {}
			que_text_answers = []
			if x.question_type == "text":
				for votetext in VoteText.objects.filter(question_id = x.question.id):
					que_text_answers.append(votetext.answer_text)
					if len(que_text_answers) == 10:
						break
			else:
				for index,choice in enumerate(questionChoices):
					choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0)
					choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0)
					vote_set = choice.vote_set
					numVotes = vote_set.count()
					# print(numVotes,choice_dict,choice.choice_text + " : " + str(numVotes))
					if not choice_dict.get(numVotes):
						choice_dict[numVotes] = []
					choice_dict[numVotes].append("Choice " + str(index+1)) # + " : " + str(numVotes))
					if(numVotes >= maxVotedCount):
						maxVotedCount = numVotes
						maxVotedChoice = choice.id
						maxVotedChoiceStr = "Choice"+str(index+1)
					if(numVotes <= minVotedCount):
						minVotedCount = numVotes
					# print(Vote.objects.filter(choice_id = choice.id))
					# print(VoteApi.objects.filter(choice_id = choice.id))
					for vote in Vote.objects.filter(choice_id = choice.id):
						choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
						total_choice_vote += 1
						age = vote.user.extendeduser.calculate_age()
						if age > 25 and age < 31:
							choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
							total_choice_vote_filter += 1
						gender = vote.user.extendeduser.gender
						profession = vote.user.extendeduser.profession
						country = vote.user.extendeduser.country
						age_dict = get_age_data(age,age_dict)
						gender_dict[gender] = gender_dict.get(gender,0) + 1
						prof_dict[profession] = prof_dict.get(profession,0) + 1
						if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
								country = 'United Kingdom'
						country_dict[country] = country_dict.get(country,0) + 1
					for vote in VoteApi.objects.filter(choice_id=choice.id):
						age = vote.age
						gender = vote.gender
						profession = vote.profession
						country = vote.country
						if age and gender and profession:
							if age > 25 and age < 31:
								choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
								total_choice_vote_filter += 1
							choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
							total_choice_vote += 1
							age_dict = get_age_data(age,age_dict)
							gender_dict[gender] = gender_dict.get(gender,0) + 1
							prof_dict[profession] = prof_dict.get(profession,0) + 1
							if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
									country = 'United Kingdom'
							country_dict[country] = country_dict.get(country,0) + 1
					for vote in Vote.objects.filter(choice_id = maxVotedChoice):
						age = vote.user.extendeduser.calculate_age()
						gender = vote.user.extendeduser.gender
						profession = vote.user.extendeduser.profession
						country = vote.user.extendeduser.country
						age_dict_filter = get_age_data(age,age_dict_filter)
						gender_dict_filter[gender] = gender_dict.get(gender,0) + 1
						prof_dict_filter[profession] = prof_dict.get(profession,0) + 1
						if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
								country = 'United Kingdom'
						country_dict_filter[country] = country_dict.get(country,0) + 1
					for vote in VoteApi.objects.filter(choice_id = maxVotedChoice):
						age = vote.age
						gender = vote.gender
						profession = vote.profession
						country = vote.country
						if age and gender and profession:
							age_dict_filter = get_age_data(age,age_dict_filter)
							gender_dict_filter[gender] = gender_dict.get(gender,0) + 1
							prof_dict_filter[profession] = prof_dict.get(profession,0) + 1
							if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
									country = 'United Kingdom'
							country_dict_filter[country] = country_dict.get(country,0) + 1
			survey_polls.append({ "question":x.question, "q_type":x.question_type, "totalResponses":totalResponses, "maxVotes":choice_dict.get(maxVotedCount,""), "minVotes":choice_dict.get(minVotedCount,""), "choice_graph":choice_vote_count, "choice_graph_filter":choice_vote_count_filter, "total_choice_vote":total_choice_vote, "total_choice_vote_filter":total_choice_vote_filter, "age_graph":age_dict, "gender_graph":gender_dict, "prof_graph":prof_dict, "country_graph":country_dict, "age_graph_filter":age_dict_filter,"gender_graph_filter":gender_dict_filter, "prof_graph_filter":prof_dict_filter, "country_graph_filter":country_dict_filter, "maxVotedChoiceStr":maxVotedChoiceStr, "que_text_answers":que_text_answers })
		context["surveytotalResponses"] = surveytotalResponses
		context["incompleteResponses"] = completeRate
		context["polls"] = survey_polls
		context["maxVotedQuestion"] = maxVotedQuestion
		# print(context)
		return context

def get_age_data(user_age,age_dic):
	age_dic['over_50'] = age_dic.get('over_50',0)
	age_dic['bet_36_50'] = age_dic.get('bet_36_50',0)
	age_dic['bet_31_35'] = age_dic.get('bet_31_35',0)
	age_dic['bet_26_30'] = age_dic.get('bet_26_30',0)
	age_dic['bet_20_25'] = age_dic.get('bet_20_25',0)
	age_dic['under_19'] = age_dic.get('under_19',0)
	if user_age > 50:
		age_dic['over_50'] = age_dic.get('over_50',0) + 1
	elif user_age > 35:
		age_dic['bet_36_50'] = age_dic.get('bet_36_50',0) + 1
	elif user_age > 30:
		age_dic['bet_31_35'] = age_dic.get('bet_31_35',0) + 1
	elif user_age > 25:
		age_dic['bet_26_30'] = age_dic.get('bet_26_30',0) + 1
	elif user_age > 19:
		age_dic['bet_20_25'] = age_dic.get('bet_20_25',0) + 1
	elif user_age > 0:
		age_dic['under_19'] = age_dic.get('under_19',0) + 1
	return age_dic
