from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from allauth.account.models import EmailAddress
import os,linecache
import sys
from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound
from django.views import generic
from django.core.mail import send_mail
from polls.models import VoteColumn, Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory,QuestionUpvotes,Survey,Survey_Question,SurveyWithCategory,SurveyVoted,VoteText,VoteApi,PollTokens,EmailTemplates, PollsReferred, SurveysReferred, UsersReferred, Demographics, MatrixRatingColumnLabels, SurveySection, VoteRankAndValue
#from polls.models import PollTokens
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
from django.db.models import Count,Avg
import django.contrib.auth.hashers
from django.shortcuts import redirect
from django.template import loader
import requests
import operator
from django.template.loader import render_to_string
import ast
import re
from random import shuffle
from particle.models import Particle
from collections import OrderedDict as SortedDict
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,5}$")

# Create your views here.
shakey=(settings.SHAKEY).encode('utf-8')
cookie_prepend = "ABP_OWN_"

def checkBooleanValue(value):
	return value.lower() == "true"

class WebRtcView(BaseViewList):
	template_name = 'polls/webrtc.html'
	def get_queryset(self):
		return {}

class ThankYouView(BaseViewList):
	template_name = 'polls/thankyou.html'
	def get_queryset(self):
		return {}

class ABPChatPubNubView(BaseViewList):
	template_name = 'polls/abp_chat_pubnub.html'
	def get_queryset(self):
		return {}

class ABPChatPubNubIntervieweeView(BaseViewList):
	template_name = 'polls/abp_chat_pubnub_interviewee.html'
	def get_queryset(self):
		return {}

class TeamView(BaseViewList):
	template_name = 'polls/team.html'
	def get_queryset(self):
		return {}

class IndexView(BaseViewList):
	context_object_name = 'data'
	# paginate_by = 50

	def render_to_response(self, context, **response_kwargs):
		response = super(IndexView, self).render_to_response(context, **response_kwargs)
		if not self.request.COOKIES.get("location"):
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
		global_location = ""
		country_list =[]
		if request.COOKIES.get("location","global").lower() != "global":
			global_location = request.COOKIES.get("location").lower()
			country_list = polls.continent_country_dict.continent_country_dict.get(global_location)

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
					latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=True)
				elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
					latest_questions = latest_questions
				elif request.GET.get('tab') == 'leastvoted':
					latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=False)
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
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=False)
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
			latest_questions = Question.objects.filter(privatePoll=0,home_visible=1).order_by('-pub_date')[:50]
			latest_questions = list(OrderedDict.fromkeys(latest_questions))
			if request.GET.get('tab') == 'mostvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=False)
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
			mainData.append(get_index_question_detail(self.request,mainquestion,user,sub_que,curtime))
		particleList = Particle.objects.order_by('-pub_date')
		primer = Particle.objects.filter(is_prime=1)
		if primer:
			primer = primer.latest()
		context['primer'] = primer
		featuredParticles = []
		for x in particleList:
			if x.is_featured == 1 and x != primer:
				featuredParticles.append(x)
				if len(featuredParticles) == 4:
					break
		featuredParticles1 = featuredParticles[:2]
		featuredParticles2 = featuredParticles[2:]
		context['featuredParticles'] = featuredParticles
		context['featuredParticles1'] = featuredParticles1
		context['featuredParticles2'] = featuredParticles2
		context['data'] = mainData
		return context

class VoteView(BaseViewDetail):
	model = Question

	def get_template_names(self):
		# print(self.request.COOKIES)
		template_name = 'polls/voteQuestion.html'
		question = self.get_object()
		question.numViews +=1
		question.save()
		votedCookie = cookie_prepend+"VOTED_"+str(question.id)
		alreadyVoted = checkBooleanValue(self.request.COOKIES.get(votedCookie,""))
		user = self.request.user
		if self.request.path.startswith("/public-url"):
			template_name = 'publictemplates/question_share.html'
		elif user.is_authenticated():
			voted = Voted.objects.filter(question = question, user=user)
			subscribed = Subscriber.objects.filter(user=user, question=question)
			if voted or user.id == question.user.id or ( question.expiry and question.expiry < timezone.now() ) or (self.request.path.endswith('result') and subscribed):
				template_name = 'polls/questionDetail.html'
		elif alreadyVoted:
			template_name = 'polls/questionDetail.html'
		return [template_name]

	def get_context_data(self, **kwargs):

		context = super(VoteView, self).get_context_data(**kwargs)
		curtime = timezone.now()
		user = self.request.user
		subscribed_questions = []
		user_already_voted = False
		sub_que = []
		showDemographic = True
		if user.is_authenticated():
			createExtendedUser(user)
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
				userFormData = {"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city}
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
			subscribed_questions = []
			if user.is_authenticated():
				subscribed_questions = Subscriber.objects.filter(user=user)
			for sub in subscribed_questions:
				sub_que.append(sub.question.id)
				question_user_vote = Voted.objects.filter(user=user,question=context['question'])
			if context['question'].protectResult and user != context['question'].user:
				showDemographic = False
		context["data"] = get_index_question_detail(self.request,context['question'],user,sub_que,curtime)
		followers = len([ x.user for x in Follow.objects.filter(target_id=user.id,deleted_at__isnull=True) ])
		following = len([ x.target for x in Follow.objects.filter(user_id=user.id,deleted_at__isnull=True) ])
		context['connection'] = followers + following
		if context['question'].id == 3051:
				context['votes'] += 100
				context['subscribers'] += 150
		return context

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = request.POST.get('question')
		question = Question.objects.get(pk=questionId)
		queSlug = question.que_slug
		queBet = request.POST.get('betAmountHidden')
		if queBet:
			queBet = int(queBet)
		choiceId = request.POST.get('choice','')
		if not choiceId:
			# error to show no choice selected
			data={}
			data['form_errors'] = "Please Select A Choice"
			return HttpResponse(json.dumps(data), content_type='application/json')
		elif user.is_authenticated():
			if request.is_ajax():
				return HttpResponse(json.dumps({}),content_type='application/json')
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
				url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
				return HttpResponseRedirect(url)
			voteSuccess = False
			if question.isBet and queBet:
				voteSuccess = save_poll_vote(user,question.id,choiceId,queBet)
			else:
				voteSuccess = save_poll_vote(user,question.id,choiceId)
			if voteSuccess:
				save_references(referral_user=request.GET.get("referral",""), poll=question)
			
		else:
			if request.is_ajax():
				giveData = {}
				if not question.authenticate:
					giveData = save_poll_vote_widget(request, question.id, choiceId)
				return HttpResponse(json.dumps(giveData),content_type='application/json')
			next_url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
			extra_params = '?next=%s?referral=%s'%(next_url,request.GET.get("referral",""))
			url = reverse('account_login')
			full_url = '%s%s'%(url,extra_params)
			if request.is_ajax():
				return HttpResponse(json.dumps({}),content_type='application/json')
			return HttpResponseRedirect(full_url)
		url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
		after_poll_vote_credits_activity(question,user,queBet)
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
		canEdit = question.iseditable(request.user)
		# if (question.voted_set.count() > 0 and not request.user.is_superuser):
		# 	canEdit = False
		# if question.user != request.user and not request.user.is_superuser:
		# 	canEdit = False
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
			context['extra_choices'] = request.user.extendeduser.company.num_of_choices - question.choice_set.count()
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
		if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
			userFormData = {"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city}
			context['signup_part_form'] = MySignupPartForm(userFormData)
		context['categories'] = Category.objects.all()
		groups = [x.group.name for x in ExtendedGroup.objects.filter(user_id = user.id)]
		context['groups'] = groups
		context['extra_choices'] = user.extendeduser.company.num_of_choices - 4
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
		featuredpoll = 0
		if user.extendeduser.company_id > 1:
			home_visible=0
		queBetAmount = request.POST.get("betAmount")
		if queBetAmount:
			queBetAmount = int(queBetAmount)
		queBetChoiceText = request.POST.get("betChoice")
		queBetChoice = None
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
				featuredpoll = question.featuredPoll
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]

			if qeyear != 0 or qemonth != 0 or qeday != 0 or qehr != 0 or qemin != -1:
				if qeap.lower() == 'pm' and qehr != 12:
					qehr = qehr + 12
				elif qeap.lower() == 'am' and qehr == 12:
					qehr = 0
				try:
					curtime = datetime.datetime.now();
					qExpiry = datetime.datetime(qeyear, qemonth, qeday,hour=qehr,minute=qemin)
					if qExpiry < curtime:
						raise Exception
				except:
					errors['expiryError'] = "Invalid date time"

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
			shareImage = request.FILES.get('shareImage')

			if edit:
				if request.POST.get('imagetextshareImage',""):
					shareImage = question.featured_image
				elif question.featured_image:
					if os.path.isfile(question.featured_image.path):
							os.remove(question.featured_image.path)
					# imagePathList.append(shareImage.path)
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
			extra_choices = []
			if user.extendeduser.company.num_of_choices > 4:
				for i in range(5,user.extendeduser.company.num_of_choices+1):
					if request.POST.getlist('choice'+str(i)):
						choice = request.POST.getlist('choice'+str(i))[0].strip()
						if choice:
							choices.append(choice)
						if edit and request.POST.get('imagechoice'+str(i),""):
							choiceid = request.POST.get('imagechoice'+str(i)).split("---")[1]
							choiceImage = Choice.objects.get(pk=choiceid).choice_image
							imagePathList.append(choiceImage.path)
						else:
							choiceImage = request.FILES.get('choice'+str(i))
						if choiceImage:
							images.append(choiceImage)
						extra_choice = {}
						extra_choice["choice"] = choice
						extra_choice["image"] = choiceImage
						extra_choice["choice_id_text"] = 'choice'+str(i)
						extra_choices.append(extra_choice)
			isAnon = request.POST.get('anonymous')
			isPrivate = request.POST.get('private')
			isBet = request.POST.get('bet')
			isProtectResult = request.POST.get('protectResult',False)
			makeFeatured = request.POST.get('makeFeatured',False)
			authenticate = request.POST.get('authenticate',False)
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
			if authenticate:
				authenticate = 1
			else:
				authenticate = 0
			makeFeaturedError = ""
			if makeFeatured and user.extendeduser.credits - 100 >= 0:
				home_visible = 1
				featuredpoll = 1
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
				question.question_text=qText
				question.description=qDesc
				question.expiry=qExpiry
				question.isAnonymous=anonymous
				question.privatePoll=private
				question.isBet = bet
				question.protectResult = protectResult
				question.home_visible = home_visible
				question.featured_image = shareImage
				question.featuredPoll = featuredpoll
				question.authenticate = authenticate
			else:
				question = Question(user=user, question_text=qText, description=qDesc, expiry=qExpiry, pub_date=curtime,isAnonymous=anonymous,privatePoll=private,isBet=bet,home_visible=home_visible,protectResult=protectResult, featured_image=shareImage, featuredPoll = featuredpoll, authenticate = authenticate)
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
			for choice_dict in extra_choices:
				if choice_dict["choice"] or choice_dict["image"]:
					choice = Choice(question=question,choice_text=choice_dict["choice"],choice_image=choice_dict["image"])
					choice.save()
					if queBetAmount and queBetChoiceText == choice_dict["choice_id_text"]:
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
			                    'questionUrl':settings.CUSTOM_DOMAIN+url,
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
		qSlug = request.GET.get('qSlug')
		poll_url = reverse('polls:polls_vote', kwargs={'pk':qIdBan,'que_slug':qSlug})
		user = request.user
		subject = "Report Abuse"
		message = str(user)+" reported abuse on the question "+settings.DOMAIN_URL+poll_url
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
	else:
		extendedUser = ExtendedUser(user=user)
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
		if sub_email not in to_email and sub_user.user.id != request.user.id and sub_user.extendeduser.mailSubscriptionFlag==0:
			to_email.append(sub_email)
			que_author.append(sub_user.user.first_name)
	template_name = "polls/emailtemplates/comment_template.html"
	mail_subject = "AskByPoll : Comment on your Poll"
	for index,to_mail in enumerate(to_email):
		if (to_email):
			context = {                      
		    	"QuestionAuthor" : que_author[index],
		    	"CommentAuthor" : com_author,
		    	"QuestionURL" : que_url,
		    	"QuestionText" : que_text,
				"domain_url":settings.DOMAIN_URL
				}
			html_message = render_to_string(template_name, context)
			send_mail(mail_subject,"", 'support@askbypoll.com', [to_mail],html_message=html_message)
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
			try:
				feed = client.feed('notification', questionVoted.user.id)
				feed.add_activity(activity)
			except Exception as e:
				import os,sys
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print(e)
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
	paginate_by = 25

	def render_to_response(self, context, **response_kwargs):
		response = super(CompanyIndexView, self).render_to_response(context, **response_kwargs)
		return response

	def get_template_names(self):
		request = self.request
		template_name = 'polls/company.html'
		return [template_name]

	def get_queryset(self):
		createExtendedUser(self.request.user)
		request = self.request
		user = request.user
		context = {}
		mainData = []
		latest_questions = []
		curtime = timezone.now()
		company_name = request.path.replace("/","")
		company_obj = Company.objects.filter(company_slug=company_name)
		if company_obj:
			company_obj = company_obj[0]
		else:
			base_url = reverse("polls:index")
			return HttpResponseRedirect(reverse("polls:index")) #this should be a 404 page
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
			latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=True)
		elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
			latest_questions = latest_questions
		elif request.GET.get('tab') == 'leastvoted':
			latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=False)
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
		data = {}
		data['company_obj'] = company_obj
		data['followed'] = followed
		company_admin_list_str = str(';'.join(company_admin_list))
		data['companyAdmins'] = str(';'.join(company_admin_list))
		for mainquestion in latest_questions:
			mainData.append(get_index_question_detail(self.request,mainquestion,user,sub_que,curtime,data))
		context['data'] = mainData
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
				# get profession count
				prof_dic = {}
				# get country count
				country_dic = {}
				# get state count
				state_dic = {}
				# get age count
				age_dic = {}
				age_dic['over_50'] = 0
				age_dic['bet_36_50'] = 0
				age_dic['bet_31_35'] = 0
				age_dic['bet_26_30'] = 0
				age_dic['bet_20_25'] = 0
				age_dic['under_19'] = 0
				if int(pollId) == 3051:
					gender_dic['M'] = 50
					gender_dic['F'] = 50
					age_dic['bet_36_50'] = 20
					age_dic['bet_31_35'] = 15
					age_dic['bet_26_30'] = 40
					age_dic['bet_20_25'] = 25
					prof_dic['Others'] = 100
					country_dic['United Kingdom'] = 100
					state_dic['England'] = 100
				vote_list = []
				email_list_voted = []
				if choiceId == "nochoice":
					vote_list = Vote.objects.filter(choice_id__in=Choice.objects.filter(question_id=pollId).values("id"))
					vote_api_list = VoteApi.objects.filter(question_id=pollId)
				else:
					vote_list = Vote.objects.filter(choice_id=choiceId)
					vote_api_list = VoteApi.objects.filter(choice_id=choiceId)
				for vote in vote_list:
					user_data = ast.literal_eval(vote.user_data)
					# user_extendeduser = vote.user.extendeduser
					email_list_voted.append(vote.user.email)
					# gender_dic[user_extendeduser.gender] += 1
					# user_age = user_extendeduser.calculate_age()
					gender_dic[user_data['gender']] += 1
					user_age = user_data['birthDay']
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
					# prof_dic[user_extendeduser.profession] = prof_dic.get(user_extendeduser.profession,0) + 1
					# country = user_extendeduser.country
					prof_dic[user_data["profession"]] = prof_dic.get(user_data["profession"],0) + 1
					country = user_data["country"]
					if country == 'United Kingdom' or country=='Scotland' or country=='Wales' or country=='Northern Ireland':
						country = 'United Kingdom'
					country_dic[country] = country_dic.get(country,0) + 1
					# state = user_extendeduser.state
					state = user_data["state"]
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
					if vote.email and vote.email in email_list_voted:
						continue
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
				min_age,max_age = get_min_max_age(request.POST.get("age"))
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
				extra_data = request.POST.get("extra_data",'{}')
				extra_data = json.loads(extra_data)
				
				extra_data["gender"] = gender
				extra_data["profession"] = profession
				extra_data["country"] = country
				extra_data["state"] = state
				extra_data["min_age"] = min_age
				extra_data["max_age"] = max_age
				response_dic = {}
				all_rating = 0
				total_votes = 0
				total_votes_extra = 0
				choices = []
				survey_poll = Survey_Question.objects.filter(question_id=pollId)
				if survey_poll:
					survey_poll = survey_poll[0]
				questionType = ''
				columnLabels = ()
				if survey_poll:
					questionType = survey_poll.question_type
				if questionType == 'matrixrating':
					columnLabels = MatrixRatingColumnLabels.objects.filter(question_id=pollId)
				if survey_poll and survey_poll.question_type == "rating":
					email_list_voted = []
					all_percent = 0
					min_rating = survey_poll.min_value
					max_rating = survey_poll.max_value
					for vote in VoteText.objects.filter(question_id=pollId):
						user_data = ast.literal_eval(vote.user_data)						
						email_list_voted.append(vote.user.email)
						add_cnt = get_if_choice_vote_add(user_data,extra_data)
						if add_cnt:
							all_percent += int(vote.answer_text)
							total_votes += 1
					for vote in VoteApi.objects.filter(choice_id=choice.id):
						if vote.email and vote.email in email_list_voted:
							pass
						else:
							if vote.age and vote.profession and vote.gender:
								if vote.user_data :
									user_data = ast.literal_eval(vote.user_data)
								else:
									user_data = {}
								user_data = get_user_data_from_api(vote,user_data)
								add_cnt = get_if_choice_vote_add(user_data,extra_data)
								if add_cnt:
									all_percent += float(vote.answer_text)
									total_votes += 1
					if total_votes:
						all_rating = all_percent/total_votes
					else:
						all_rating = 0
					all_rating = (all_percent * (max_rating - min_rating))/100 + min_rating
				else:
					for idx,choice in enumerate(Choice.objects.filter(question_id=pollId)):
						choice_dic = {}
						choice_text = "Choice"+str(idx+1)
						choice_dic["key"] = choice_text
						choice_dic["id"] = choice.id
						choice_dic["val"] = 0
						choice_dic["extra_val"] = 0
						email_list_voted = []
						choice_dic["columns"] = []
						if columnLabels:
							for column in columnLabels:
								choice_dic["columns"].append({column.id:0})
						for vote in Vote.objects.filter(choice_id=choice.id):
							user_data = ast.literal_eval(vote.user_data)						
							email_list_voted.append(vote.user.email)
							add_cnt = get_if_choice_vote_add(user_data,extra_data)
							if add_cnt:
								if questionType == 'matrixrating':
									voteColumn = VoteColumn.objects.get(vote=vote)
									for column in choice_dic["columns"]:
										for i in column:
											if i == voteColumn.column_id:
												column[i] += 1
								choice_dic["val"] += 1
								total_votes += 1
								choice_dic["extra_val"] += 1
								total_votes_extra += 1
						for vote in VoteApi.objects.filter(choice_id=choice.id):
							if vote.email and vote.email in email_list_voted:
								pass
							else:
								if vote.age and vote.profession and vote.gender:
									if vote.user_data :
										user_data = ast.literal_eval(vote.user_data)
									else:
										user_data = {}
									user_data = get_user_data_from_api(vote,user_data)
									add_cnt = get_if_choice_vote_add(user_data,extra_data)
									if add_cnt:
										if questionType == 'matrixrating':
											voteColumn = vote.votecolumn.id
											for column in choice_dic["columns"]:
												for i in column:
													if i == voteColumn:
														column[i] += 1	
										choice_dic["val"] += 1
										total_votes += 1
								choice_dic["extra_val"] += 1
								total_votes_extra += 1
						choices.append(choice_dic)
				response_dic['choices'] = choices
				response_dic['rating'] = all_rating
				response_dic['total_votes'] = total_votes
				response_dic['total_votes_extra'] = total_votes_extra
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

def get_if_choice_vote_add(user_data, extra_data):
	user_age = user_data["birthDay"]
	min_age = extra_data.get("min_age",0)
	max_age = extra_data.get("max_age",9999)
	add_cnt = True
	if not (user_age >= min_age and user_age <= max_age):
		add_cnt = False
	non_str_values = ["min_age","max_age"]
	for key,val in extra_data.items():
		if key not in non_str_values:
			if val and val != "nochoice":
				user_val = user_data.get(key,"")
				if not user_val:
					add_cnt = False
				elif user_val.lower() != val.lower():
					add_cnt = False
					break
	return add_cnt

def get_min_max_age(ageStr):
	min_age = 0
	max_age = 9999
	if ageStr and ageStr != "nochoice":
		if ageStr == "<19":
			max_age = 19
		elif ageStr == "20-25":
			min_age = 20
			max_age = 25
		elif ageStr == "26-30":
			min_age = 26
			max_age = 30
		elif ageStr == "31-35":
			min_age = 31
			max_age = 35
		elif ageStr == "36-50":
			min_age = 36
			max_age = 50
		elif ageStr == ">50":
			min_age = 50
	return min_age,max_age

class TriviaPView(BaseViewList):
	context_object_name = 'trivias'

	def get_template_names(self, **kwargs):
		template_name = 'trivia/trivia.html'
		return [template_name]

	def get_queryset(self):
		context = {}
		triviaList = Trivia.objects.order_by('-pub_date')
		context['trivias'] = triviaList
		return triviaList

class CreateSurveyView(BaseViewList):
	def post(self, request, *args, **kwargs):
		try:
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
			thanks_msg = post_data.get("thanks-msg")
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]
			qSection = post_data.get("qSection")
			sectionList = []
			for i in range(1, int(qSection)+1):
				sectionList.append({"sectionName":post_data.get("sectionName---"+str(i)), "sectionOrder":i})
			qExpectedTime = post_data.get("expectedTime")
			surveyError = ""
			if not survey_name:
				surveyError += "Survey Name is Required<br>"

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
			demo_list = {}

			if len(question_count) < 1:
				surveyError += "Atleast 1 question is required<br>"
			if surveyError:
				errors['surveyError'] = surveyError
			imagePathList = []
			shareImage = request.FILES.get('shareImage')

			if edit:
				if request.POST.get('imagetextshareImage',""):
					shareImage = survey.featured_image
				elif survey.featured_image:
					if os.path.isfile(survey.featured_image.path):
							os.remove(survey.featured_image.path)

			demo_error = ""
			dup_name = []
			demographic_count = []
			if post_data.get("demographic_count"):
				demographic_count = json.loads(post_data.get("demographic_count"))
			for demographic_index in demographic_count:
				name = post_data.get("demographic_name"+str(demographic_index),"").strip()
				if not name:
					demo_error += "Demographic Name is required"
				values = post_data.get("demographic_values"+str(demographic_index),"").strip().split(",")
				values = list(filter(bool, values))
				if name in demo_list:
					dup_name.append(name)
				demo_list[name] = values
			if dup_name:
				demo_error += "Overlapping demographic names %s"%(dup_name)
			if demo_error:
				errors['demographicDiv'+str(demographic_index)] = demo_error
			for que_index in question_count:
				poll = {}
				que_text = post_data.get("qText"+str(que_index)).strip()
				que_desc = post_data.get("qDesc"+str(que_index)).strip()
				que_type = post_data.get("qType"+str(que_index)).strip()
				protectResult = post_data.get("protectResult"+str(que_index),False)
				addComment = post_data.get("addComment"+str(que_index),False)
				mandatory = post_data.get("mandatory"+str(que_index),False)
				horizontalOptions = post_data.get("horizontalOptions"+str(que_index),False)
				poll['text'] = que_text
				poll['desc'] = que_desc
				poll['type'] = que_type
				poll['protectResult'] = protectResult
				poll['addComment'] = addComment
				poll['mandatory'] = mandatory
				poll['horizontalOptions'] = horizontalOptions
				# Not taking id now but ideally should take some id maybe ?
				poll['sectionName'] = post_data.get("qSect---"+str(que_index)).strip()
				columns = []
				choices = []
				images = []
				queError = ""
				min_max = {}
				if not que_text:
					queError += "Question is required.<br>"
				if que_type == "rating":
					min_value = post_data.get(que_index+"---rating---Min",0)
					max_value = post_data.get(que_index+"---rating---Max",10)
					if min_value:
						min_value = int(min_value)
					if max_value:
						max_value = int(max_value)
					min_max["min_value"] = min_value
					min_max["max_value"] = max_value
					choice_elem_id = 'question'+que_index+'choiceDiv'
					if not (min_max["min_value"] and min_max["max_value"]):
						errors[choice_elem_id] = "Min and Max value is required.<br>"
					elif min_max["min_value"] > min_max["max_value"]:
						errors[choice_elem_id] = "Min Value should be less than Max.<br>"
				elif que_type != "text":
					choice_list = json.loads(post_data.get("choice_count")).get(que_index)
					max_choice_cnt = user.extendeduser.company.num_of_choices + 1
					if len(choice_list) < 2:
						queError += "Atleast 2 choices are required"
					elif len(choice_list) > max_choice_cnt:
						queError += "Maximum %s choices can be provided"%(max_choice_cnt)
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
				if que_type == "matrixrating":
					column_list = json.loads(post_data.get("column_count")).get(que_index)
					if len(column_list) < 2:
						queError += "Atleast 2 columns are required"
					elif len(column_list) > max_choice_cnt:
						queError += "Maximum %s columns can be provided"%(max_choice_cnt)
					for column_count in column_list:
						column_elem_id = 'questionDiv'+que_index+'column'+str(column_count)
						column = request.POST.getlist(column_elem_id)[0].strip()
						columns.append(column)
						if not column:
							errors[column_elem_id] = "Column required"
					if len(columns)!=len(set(columns)):
						queError += "Please provide different columns<br>"
				if queError:
					errors["qText"+str(que_index)] = queError
					
				if que_type == "matrixrating":
					poll['column_list'] = columns
				poll['choice_texts'] = choices
				poll['choice_images'] = images
				poll['min_max'] = min_max
				polls_list.append(poll)
			if errors:
				return HttpResponse(json.dumps(errors), content_type='application/json')
			else:
				if edit:
					for ssection in survey.surveysection_set.all():
						ssection.delete()
				survey = createSurvey(survey_id,survey_name,survey_desc,qExpiry,curtime,user,selectedCats,shareImage,thanks_msg,qExpectedTime,qSection)
				for section in sectionList:
					ssection = SurveySection(survey=survey, sectionName=section['sectionName'], sectionOrder=section['sectionOrder'])
					ssection.save()
				createSurveyPolls(survey,polls_list,curtime,user,qExpiry,edit,imagePathList)
				createDemographics(survey=survey,demographic_list=demo_list,user=user)
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
				                    'questionUrl':"localhost:8000"+url,
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
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def createDemographics(survey=None,demographic_list=None,user=None,question=None):
	if demographic_list:
		survey_id = 0
		question_id = 0
		if survey:
			survey_id = survey.id
		if question:
			question_id = question.id
		demographics = None
		if survey_id > 0:
			demographics = Demographics.objects.filter(user=user,survey_id=survey_id)
		elif question_id > 0:
			demographics = Demographics.objects.filter(user=user,question_id=question_id)
		if demographics:
			demographics = demographics[0]
			demographics.demographic_data = str(demographic_list)
		else:
			demographics = Demographics(user=user, survey_id=survey_id, question_id=question_id, demographic_data=str(demographic_list))
		demographics.save()

def createSurvey(survey_id,survey_name,survey_desc,qExpiry,curtime,user,selectedCats,shareImage,thanks_msg,qExpectedTime,qSection):
	try:
		survey = None
		if survey_id > 0:
			survey = Survey.objects.get(pk=survey_id)
			survey.survey_name = survey_name
			survey.description = survey_desc
			survey.expiry = qExpiry
			survey.featured_image = shareImage
			survey.thanks_msg = thanks_msg
			survey.number_sections = qSection
			survey.expected_time = qExpectedTime
		else:
			survey = Survey( user=user, pub_date=curtime, created_at=curtime, survey_name=survey_name, description=survey_desc, expiry=qExpiry, featured_image=shareImage, thanks_msg=thanks_msg,number_sections=qSection,expected_time=qExpectedTime)
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
			for poll in survey_polls:
				question = poll.question
				if poll.question_type != "text":
					for choice in question.choice_set.all():
						if choice.choice_image:
							if os.path.isfile(choice.choice_image.path) and choice.choice_image.path not in imagePathList:
								os.remove(choice.choice_image.path)
						choice.delete()
					for column in question.matrixratingcolumnlabels_set.all():
						column.delete()
				question.delete()
		for poll in polls_list:
			protectResult = 0
			if poll['protectResult']:
				protectResult = 1
			addComment = 0
			if poll['addComment']:
				addComment = 1
			mandatory = 0
			if poll['mandatory']:
				mandatory = 1
			horizontalOptions = 0
			if poll['horizontalOptions']:
				horizontalOptions = 1
			question = Question(user=user, pub_date=curtime, created_at=curtime, expiry=qExpiry, home_visible=0, question_text=poll['text'], description=poll['desc'], protectResult=protectResult, is_survey=1,horizontal_options=horizontalOptions)
			question.save()
			for index,choice_text in enumerate(poll['choice_texts']):
				choice = Choice(question=question,choice_text=choice_text,choice_image=poll['choice_images'][index])
				choice.save()
			min_value = poll['min_max'].get("min_value",0)
			max_value = poll['min_max'].get("max_value",10)
			surveyQuestionSection = None
			try:
				surveyQuestionSection = SurveySection.objects.get(survey=survey, sectionName=poll['sectionName'])
			except:
				surveyQuestionSection = None
			survey_que = Survey_Question(survey=survey, question=question, question_type=poll['type'], add_comment=addComment, mandatory=mandatory, min_value=min_value, max_value=max_value,section=surveyQuestionSection)
			survey_que.save()
			
			if poll['type'] == 'matrixrating':
				for column in poll['column_list']:
					column = MatrixRatingColumnLabels(question=question, columnLabel = column)
					column.save()
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
		if survey.id == 64:
			template_name = 'polls/symphonySummitVoteSurvey.html'
		elif survey.id == 67:
			template_name = 'polls/eYSharedWorkspaceSurvey.html'
		elif survey.id == 68:
			template_name = 'polls/clouCouncilSurvey.html'
		elif survey.id == 69:
			template_name = 'polls/customsurveys/foodDeliverySurveyRanchi.html'
		elif survey.id == 70:
			template_name = 'polls/customsurveys/fragrance-purchase-preference.html'
		elif survey.id == 71:
			template_name = 'polls/customsurveys/leadership-styles-and-effectiveness.html'
		elif survey.id == 72:
			template_name = 'polls/customsurveys/indian-cloud-landscape-survey.html'
		elif survey.id == 74:
			template_name = 'polls/customsurveys/employee-engagement-survey.html'
		elif survey.id == 75:
			template_name = 'polls/customsurveys/employee-retention-collateral-review-feedback.html'
		elif survey.id == 77:
			template_name = 'polls/customsurveys/collateral-review-feedback-survey.html'
		survey.numViews +=1
		survey.save()
		return [template_name]

	def get_context_data(self, **kwargs):
		context = super(SurveyVoteView, self).get_context_data(**kwargs)
		user = self.request.user
		user_already_voted = False
		if user.is_authenticated():
			createExtendedUser(user)
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
				userFormData = {"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city}
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
		extra_demographics = Demographics.objects.filter(survey_id=context['survey'].id)
		demo_list = []
		if extra_demographics:
			extra_demographics = ast.literal_eval(extra_demographics[0].demographic_data)
			for key,val in extra_demographics.items():
				demo = {}
				demo["name"] = key
				demo["values"] = val
				demo_list.append(demo)
		context["demo_list"] = demo_list
		context['expired'] = False
		if context['survey'].expiry and context['survey'].expiry < timezone.now():
			context['expired'] = True
		context['polls'] = []
		sections = SurveySection.objects.filter(survey_id=context['survey'].id).order_by('sectionOrder')
		polls_section_dict = SortedDict()
		for section in sections:
			polls_section_dict[section.sectionName] = []
		polls_section_dict['Common'] = []
		
		for i,x in enumerate(Survey_Question.objects.filter(survey_id=context['survey'].id)):
			#Finding the section in which current poll is present. If No section is choosen then section name will be None
			tempSectionName = ''
			if x.section:
				tempSectionName = x.section.sectionName
			else:
				tempSectionName = None
					
			poll_dict = {"poll":x.question,"type":x.question_type, "addComment":x.add_comment, "mandatory":x.mandatory, "min_value":x.min_value, "max_value":x.max_value,"horizontalOptions":x.question.horizontal_options,"section_name":tempSectionName}
			if x.question_type == 'matrixrating':
				poll_dict['columns'] = (MatrixRatingColumnLabels.objects.filter(question=x.question))
			poll_dict['user_already_voted'] = False
			question_user_vote = []
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(user=user,question=x.question)
				if question_user_vote:
					poll_dict['user_already_voted'] = True
					if x.question_type == "text":
						poll_dict['answer'] = VoteText.objects.filter(user_id=user.id,question_id=x.question.id)[0].answer_text
					elif x.question_type == "rating":
						myrate = int(float(VoteText.objects.filter(user_id=user.id,question_id=x.question.id)[0].answer_text))
						myrate = (myrate * (x.max_value - x.min_value))/100 + x.min_value
						allrate = VoteText.objects.filter(question_id=x.question.id).aggregate(Avg('answer_text')).get('answer_text__avg')
						allrate = (allrate * (x.max_value - x.min_value))/100 + x.min_value
						if myrate > allrate:
							to_val = myrate
							from_val = allrate
							to_str = "You"
							from_str = "Others"
						else:
							to_val = allrate
							from_val = myrate
							from_str = "You"
							to_str = "Others"
						poll_dict["to_str"] = to_str
						poll_dict["to_val"] = to_val
						poll_dict["from_str"] = from_str
						poll_dict["from_val"] = from_val
				if x.add_comment:
					voteText = VoteText.objects.filter(user_id=user.id,question_id=x.question.id)
					if voteText:
						poll_dict['answer'] = voteText[0].answer_text
			
			if tempSectionName:
				polls_section_dict[tempSectionName].append(poll_dict)
			else:
				polls_section_dict['Common'].append(poll_dict)
			context['polls'].append(poll_dict)
			
		if(not polls_section_dict['Common']):
			polls_section_dict.pop('Common',None)

		context['polls_section_dict'] = polls_section_dict
		unique_key = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds() + context['survey'].id
		context['unique_key'] = unique_key
		return context

	def post(self, request, *args, **kwargs):
		try:
			path = request.path
			user = request.user
			post_data = request.POST
			survey = self.get_object()
			survey_voted = None
			survey_questions = Survey_Question.objects.filter(survey = survey)
			votes_list = []
			errors = {}
			user_data = {}
			unique_key = post_data.get("unique_key")
			if not unique_key.strip():
				unique_key = None
			for key,val in post_data.items():
				if key.startswith("demographic-"):
					key = key.replace("demographic-","")
					if key == "gender" and val:
						val = val[0]
					user_data[key] = val
					if key != "email" and not val:
						errors["error"] = "Demographics is mandatory"
			for survey_question in survey_questions:
				vote = {}
				question_type = survey_question.question_type
				question = survey_question.question
				question_id = question.id
				question_id_str = str(question_id)
				mandatory = survey_question.mandatory
				vote["id"] = question_id
				vote["type"] = question_type
				answer = ""
				choices = []
				columns = []
				ranks = []
				if not user.is_authenticated():
					if 'email' in user_data:
						votedCheck = VoteApi.objects.filter(question=vote["id"], email=user_data['email'])
						if votedCheck:
							errors["success"]="You have already voted on this survey"
							errors["res"]={}
							break
				if question_type == "text":
					answer = post_data.get("choice"+question_id_str,"").strip()
				elif question_type == "rating":
					answer = post_data.get("range"+question_id_str,"").strip()
				elif question_type == "radio":
					choice = post_data.get("choice"+question_id_str,"").strip()
					choices.append(choice)
					answer = post_data.get("choice"+question_id_str+"Comment","").strip()
				elif question_type == "checkbox":
					choice = post_data.getlist("choice"+question_id_str,[])
					for v in choice:
						choices.append(v)
					answer = post_data.get("choice"+question_id_str+"Comment","").strip()
				elif question_type == "matrixrating":
					for qchoice in question.choice_set.all():
						choice = post_data.get(str(qchoice.id),[])
						if choice:
							choiceId = choice.split('---')[0]
							columnId = choice.split('---')[1]
							choices.append(choiceId)
							columns.append(columnId)
						else:
							errors[question_id_str] = "All Rows Are Mandatory"
							break
				elif question_type == "rank":
					for qchoice in question.choice_set.all():
						choice = post_data.get(str(qchoice.id),[])
						if choice:
							choices.append(qchoice.id)
							ranks.append(choice[0])
						else:
							ranks.append(choice[0])
					answer = post_data.get("choice"+question_id_str+"Comment","").strip()
				choices = list(filter(None, choices))
				if mandatory:
					if question_type in ["radio","checkbox"]:
						if not choices:
							errors[question_id_str] = "Please Select A Choice"
					elif not answer and question_type in ["text","rating"]:
						errors[question_id_str] = "Enter Answer"
				vote["answer"] = answer
				vote["choices"] = choices
				vote["columns"] =  columns
				vote["ranks"] = ranks
				votes_list.append(vote)
			if not errors:
				errors["success"] = "Successfull"
				errors = saveVotes(user,survey,votes_list,unique_key,user_data,request)
			return HttpResponse(json.dumps(errors),content_type='application/json')
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
				tim = survey.expiry
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
			surveyAddComment = True
			surveyMandatory = True
			surveyHorizontalOptions = True
			for x in Survey_Question.objects.filter(survey_id=survey.id):
				if not x.question.protectResult:
					surveyResultProtected = False
				if not x.add_comment:
					surveyAddComment = False
				if not x.mandatory:
					surveyMandatory = False
				if not x.question.horizontal_options:
					surveyHorizontalOptions = False
				sectionName = "undefined"
				if x.section:
					sectionName = x.section.sectionName
				poll_dict = {"poll":x.question,"type":x.question_type, "addComment":x.add_comment, "mandatory":x.mandatory, "min_value":x.min_value, "max_value":x.max_value, "sectionName":sectionName}
				context['polls'].append(poll_dict)
			context["surveyResultProtected"] = surveyResultProtected
			context["surveyAddComment"] = surveyAddComment
			context["surveyMandatory"] = surveyMandatory
			extra_demographics = Demographics.objects.filter(survey_id=survey.id)
			demo_list = []
			if extra_demographics:
				extra_demographics = ast.literal_eval(extra_demographics[0].demographic_data)
				for key,val in extra_demographics.items():
					demo = {}
					demo["name"] = key
					demo["values"] = ",".join(val)
					demo_list.append(demo)
			context["demo_list"] = demo_list
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
		errors = {}
		url = reverse('polls:survey_vote', kwargs={'pk':int(request.POST.get('shareSurveyId','')),'survey_slug':request.POST.get('shareSurveySlug','')})
		selectedGnames = request.POST.get('shareselectedGroups','').split(",")
		template_name = "polls/emailtemplates/survey_invitation.html"
		mail_subject = "Survey Invitation From :"+request.user.extendeduser.company.name
		if list(filter(bool, selectedGnames)):
			for gName in selectedGnames:
				if gName:
					gName = request.user.username+'_'+request.user.extendeduser.company.name+'-'+gName
					group_user_set = Group.objects.filter(name=gName)[0].user_set.all()
					for group_user in group_user_set:
						group_user_email = group_user.email
						#msg = EmailMessage(subject="Invitation", from_email=request.user.email,to=[group_user_email])
						context = {
		                    			'inviter': request.user.first_name,
		                    			'companyname':request.user.extendeduser.company.name,
		                    			'questionUrl':settings.DOMAIN_URL+url,
		                    			'questionText':request.POST.get('shareSurveyName',''),
							'domain_url':settings.DOMAIN_URL
		                		}
						html_message = render_to_string(template_name, context)
						send_mail(mail_subject,"", 'support@askbypoll.com', [group_user_email],html_message=html_message)
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

def get_widget_html(poll, widgetFolder="webtemplates", widgetType="basic", extra_context_data = {}):
	try:
		template_name = ""
		if widgetType:
			template_name = 'polls/'+widgetFolder+'/'+widgetType+'_widget_template.html'
		context = {"poll" : poll}
		extra_context_data['domain_url'] = settings.DOMAIN_URL
		for key in extra_context_data:
			context[key] = extra_context_data[key]
		html = render_to_string(template_name, context)
		return html
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def embed_poll(request):
	try:
		pollId = int(request.GET.get('pollId'))
		callback = request.GET.get('callback', '')
		divClass = request.GET.get('divClass','basic').replace('askbypoll-embed-poll','').replace(' ','').replace('-','')
		if not divClass:
			divClass = "basic"
		analysisNeeded = False
		if request.GET.get('analysisNeeded',"") == "true":
			analysisNeeded = True
		req = {}
		poll = Question.objects.get(pk=pollId)
		extra_context_data = {}
		extra_context_data['analysisNeeded'] = analysisNeeded
		html = get_widget_html(poll, extra_context_data=extra_context_data, widgetType=divClass)
		req ['html'] = html
		if poll.protectResult == 1:
			req['protect'] = 1
		elif poll.protectResult == 0:
			req['protect'] = 0
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
		poll = Question.objects.get(pk=pollId)
		alreadyVoted = request.GET.get('alreadyVoted','false')
		src = request.GET.get('src','')
		divClass = request.GET.get('divClass','basic').replace('askbypoll-embed-poll','').replace(' ','').replace('-','')
		if not divClass:
			divClass = "basic"
		ipAddress = getIpAddress(request)
		if not request.session.exists(request.session.session_key):
			request.session.create()
		sessionKey = request.session.session_key

		question = Question.objects.get(pk=pollId)
		req = {}
		if poll.protectResult == 0:
			req['protect'] = 0
		elif poll.protectResult == 1:
			req['protect'] = 1

		if((not alreadyVoted == 'true') and not(choiceId == 0)):
			url = "http://api.db-ip.com/addrinfo?addr="+ipAddress+"&api_key=ab6c13881f0376231da7575d775f7a0d3c29c2d5"
			dbIpResponse = requests.get(url)
			locationData = dbIpResponse.json()
			votedChoice = Choice.objects.get(pk=choiceId)
			votedChoiceFromApi = VoteApi(choice=votedChoice,question=question,country=regionDict[locationData['country']] ,city=locationData['city'],state=locationData['stateprov'],ipAddress=ipAddress, session=sessionKey, src=src)
			votedChoiceFromApi.save()
			alreadyVoted = "true"
			req['votedChoice'] = votedChoice.id
		if alreadyVoted == 'true':
			email_list_voted = []
			choice_dic = {}
			totalVotes = 0
			for voteUser in Vote.objects.filter(choice__in=question.choice_set.all()):
				email_list_voted.append(voteUser.user.email)
				totalVotes += 1
				choice_dic[voteUser.choice.id] = choice_dic.get(voteUser.choice.id,0) + 1
			choices = VoteApi.objects.filter(question=question).exclude(email__in=email_list_voted).values('choice').annotate(choiceCount=Count('choice'))
			result = {}
			choice_count_dic = {}
			for i in choices:
				choice_count_dic[i.get('choice')] = i.get('choiceCount')
				totalVotes += i.get('choiceCount')
			percent_ratio = 1.39
			if divClass in ["mu"]:
				percent_ratio = 1
			for choice in question.choice_set.all():
				result[choice.id] = {}
				choice_vote_count = choice_count_dic.get(choice.id,0) + choice_dic.get(choice.id,0)
				percent = 0
				width = 0
				if totalVotes > 0:
					percent = round(choice_vote_count/totalVotes * 100)
					width = percent
					if not choice.choice_image:
						width = round(percent/percent_ratio)
						if percent == 0 and percent_ratio > 1:
							width = 15
				result[choice.id]["percent"] = percent
				result[choice.id]["width"] = width
			req ['result'] = result
		else:
			req = {}
		req['sessionKey'] = sessionKey
		response = json.dumps(req)
		response = callback + '(' + response + ');'
		return HttpResponse(response,content_type="application/json")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def results_embed_poll(request):
	try:
		alreadyVoted = request.GET.get('alreadyVoted','false')
		dataStored = request.GET.get('dataStored','false')
		callback = request.GET.get('callback', '')
		pollId = int(request.GET.get('pollId'))
		poll = Question.objects.get(pk=pollId)
		choices = Choice.objects.filter(question_id=pollId)
		divClass = request.GET.get('divClass','basic').replace('askbypoll-embed-poll','').replace(' ','').replace('-','')
		if not divClass:
			divClass = "basic"
		sessionKey = request.GET.get('votedSession', '')
		src = request.GET.get('src', '')
		user_age = 0
		gender = 'D'
		email = ''
		profession = ''
		user_data = {}
		votedChoice = -1
		error = ""
		if alreadyVoted == 'false' and dataStored == 'false':
			if request.GET.get('age'):
				user_age = int(request.GET.get('age',18))
			if request.GET.get('gender',"D") != "notSelected":
				gender = request.GET.get('gender',"D")[0]
			if request.GET.get('profession',"Others") != "notSelected":
				profession = request.GET.get('profession','Others')
			email = request.GET.get('email','').strip()
			ipAddress = getIpAddress(request)
			# ipAddress = '139.130.4.22'
			# sessionKey = " cfp14kjtdgw078auvs59z8kto1p48kyu"
			existingVote = VoteApi.objects.filter(question_id=pollId,ipAddress=ipAddress, session=sessionKey, src=src).order_by('-created_at')
			existingVote = existingVote[0]
			existingVote.age = user_age
			existingVote.gender = gender
			existingVote.profession = profession
			if email:
				existingVote.email = email
			votedChoice = existingVote.choice_id
			existingVote.save()
			user_data["birthDay"] = user_age
			user_data["gender"] = gender
			user_data["profession"] = profession
			user_data["country"] = existingVote.country
			user_data["state"] = existingVote.state
			user_data["city"] = existingVote.city
			if email and not User.objects.filter(email=email):
				new_user = create_new_user_mail_login(request,email,poll)
				new_extended_user = new_user.extendeduser
				if user_age > 0:
					new_extended_user.birthDay = datetime.date.today() - datetime.timedelta(days = user_age * 365)
				if profession:
					new_extended_user.profession = profession
				new_extended_user.gender = gender
				new_extended_user.country = existingVote.country
				new_extended_user.state = existingVote.state
				new_extended_user.city = existingVote.city
				new_extended_user.save()
				subscribed, created = Subscriber.objects.get_or_create(user=new_user, question=poll)
				voted, created = Voted.objects.get_or_create(user=new_user, question=poll)
				if created == True:
					vote, created = Vote.objects.get_or_create(user=new_user, choice=existingVote.choice)
				else:
					votedChoice = Vote.objects.filter(user=new_user,choice__in=choices)[0].choice_id
					existingVote.delete()
					error = "Already voted using this email"
			elif email:
				old_user = User.objects.filter(email=email)[0]
				old_user.backend = 'django.contrib.auth.backends.ModelBackend'
				login(request, old_user)
				subscribed, created = Subscriber.objects.get_or_create(user=old_user, question=poll)
				voted, created = Voted.objects.get_or_create(user=old_user, question=poll)
				if created == True:
					vote, created = Vote.objects.get_or_create(user=old_user, choice=existingVote.choice, user_data=user_data)
				else:
					votedChoice = Vote.objects.filter(user=old_user,choice__in=choices)[0].choice_id
					existingVote.delete()
					error = "Already voted using this email"
		choice_data = {}
		percent = {}
		totalVotes = 0
		for index,choice in enumerate(choices):
			choice_data[choice.id] = choice
			# percent["choice" + str(index)] = 0
			percent[choice.id] = 0
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
			percent[voteUser.choice_id] = percent.get(voteUser.choice_id,0) + 1
			voteApi = voteUser.user.extendeduser
			user_data = ast.literal_eval(voteUser.user_data)
			gender = user_data["gender"]
			user_age = user_data["birthDay"]
			profession = user_data["profession"]
			country = user_data["country"]
			if not gender:
				gender = 'D'
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
			if voteApi.email and voteApi.email in email_list_voted:
				pass
			else:
				totalVotes += 1
				percent[voteApi.choice_id] = percent.get(voteApi.choice_id,0) + 1
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
					country_dic[country] = country_dic.get(country,0) + 1
		percent_ratio = 1.39
		if divClass in ["mu"]:
			percent_ratio = 1
		result = {}
		for choice,choice_vote_count in percent.items():
			result[choice] = {}
			f_percent = 0
			width = 0
			if totalVotes > 0:
				f_percent = round(choice_vote_count/totalVotes * 100)
				width = f_percent
				if not choice_data[choice].choice_image:
					width = round(f_percent/percent_ratio)
					if f_percent == 0 and percent_ratio > 1:
						width = 15
			result[choice]["percent"] = f_percent
			result[choice]["width"] = width
		req = {}
		req["choice"] = result
		if poll.protectResult == 1:
			req['protect'] = 1
		elif poll.protectResult == 0:
			req['protect'] = 0
		extra_context_data = {}
		poll_template_name = "polls/webtemplates/"+divClass+"_widget_template.html"
		extra_context_data["poll_template_name"] = poll_template_name
		html = get_widget_html(poll,widgetType="demographic_result",extra_context_data=extra_context_data)
		req ['html'] = html
		req['votedChoice'] = votedChoice
		req["error"] = error
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
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

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
		ws1.write(0,2,"City",normal_style)
		ws1.write(0,3,"Gender",normal_style)
		ws1.write(0,4,"Age Group",normal_style)
		ws1.write(0,5,"Profession",normal_style)
		i = 1
		j = 1
		survey_question_list = Survey_Question.objects.filter(survey_id = survey_id)
		survey_questions = survey_question_list.values_list('question', flat=True)

		voted_list = SurveyVoted.objects.filter(survey_id = survey_id)
		demo_list = get_demographic_list(survey_id=survey_id)
		for voted in voted_list:
			vote_user = voted.user
			user_data = {}
			addVal = 0
			for index,survey_question in enumerate(survey_question_list):
				question = survey_question.question
				question_type = survey_question.question_type
				excel_text = ""
				choice_list = Choice.objects.filter(question_id=question.id)
				excel_text = "Q"+str(index+1)
				answer_text = ""
				answer_texts = []
				excel_texts = []
				if question_type in ["text", "rating"]:
					vote_text = VoteText.objects.filter(user_id=vote_user.id,question_id=question.id)
					if vote_text:
						answer_text = vote_text[0].answer_text
						user_data = ast.literal_eval(vote_text[0].user_data)
						if question_type == "rating":
							answer_text += "%"
				elif question_type == "radio":
					for c_index,choice in enumerate(choice_list):
						vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
						if vote:
							answer_text = str(c_index+1)
							user_data = ast.literal_eval(vote[0].user_data)
					if answer_text:
						answer_texts.append(answer_text)
					else:
						answer_texts.append(0)
					excel_texts.append(excel_text)
				elif question_type == "checkbox":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
						if vote:
							answer_text = 1
							user_data = ast.literal_eval(vote[0].user_data)
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				elif question_type == "matrixrating":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
						try:
							column = VoteColumn.objects.get(user_id=vote_user.id,vote=vote,choice=choice)
						except:
							column = None
						if column:
							answer_text = MatrixRatingColumnLabels.objects.get(pk=column.column_id).columnLabel
							user_data = ast.literal_eval(vote[0].user_data)
						else:
							answer_text = 'N/A'
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				elif question_type == "rank":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
						try:
							rank = VoteRankAndValue.objects.get(user_id=vote_user.id,vote=vote,choice=choice)
						except:
							rank = None
						if rank:
							answer_text = rank.rankandvalue
							user_data = ast.literal_eval(vote[0].user_data)
						else:
							answer_text = 'N/A'
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				if survey_question.add_comment:
					excel_texts.append("Comments")
					additionalComment = VoteText.objects.filter(user=voted.user, question=question)
					if additionalComment:
						answer_texts.append(additionalComment[0].answer_text)
					else:
						answer_texts.append("No Comments")
				i,j = write_demographics_into_excel(ws1,user_data,demo_list,i)
				if answer_texts:
					for ans_index,answer in enumerate(answer_texts):
						write_result_into_excel(ws1,excel_texts[ans_index],answer,i,j+index+ans_index+addVal)
					addVal += ans_index
				else:
					write_result_into_excel(ws1,excel_text,answer_text,i,j+index+addVal)
			i += 1
		unique_keys = VoteApi.objects.filter(question_id__in=survey_questions).values_list('unique_key', flat=True).distinct()
		for unique_key in unique_keys:
			addVal = 0 
			for index,survey_question in enumerate(survey_question_list):
				question = survey_question.question
				question_type = survey_question.question_type
				excel_text = ""
				choice_list = Choice.objects.filter(question_id=question.id)
				excel_text = "Q"+str(index+1)
				answer_text = ""
				answer_texts = []
				excel_texts = []
				if question_type in ["text", "rating"]:
					vote_text = VoteApi.objects.filter(unique_key=unique_key,question_id=question.id)
					if vote_text:
						answer_text = vote_text[0].answer_text
						user_data = get_user_data_from_api(vote_text[0])
						if vote_text[0].user_data:
							extra_data = ast.literal_eval(vote_text[0].user_data)
							user_data.update(extra_data)
						if question_type == "rating":
							answer_text += "%"
				elif question_type == "radio":
					for c_index,choice in enumerate(choice_list):
						vote = VoteApi.objects.filter(unique_key=unique_key,choice=choice)
						if vote:
							answer_text = str(c_index+1)
							user_data = get_user_data_from_api(vote[0])
							if vote[0].user_data:
								extra_data = ast.literal_eval(vote[0].user_data)
								user_data.update(extra_data)
					if answer_text:
						answer_texts.append(answer_text)
					else:
						answer_texts.append(0)
					excel_texts.append(excel_text)
				elif question_type == "checkbox":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = VoteApi.objects.filter(unique_key=unique_key,choice=choice)
						if vote:
							answer_text = 1
							user_data = get_user_data_from_api(vote[0])
							if vote[0].user_data:
								extra_data = ast.literal_eval(vote[0].user_data)
								user_data.update(extra_data)
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				elif question_type == "matrixrating":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = VoteApi.objects.filter(unique_key=unique_key,choice=choice)
						if vote:
							column = vote[0].votecolumn_id
							answer_text = MatrixRatingColumnLabels.objects.get(pk=column).columnLabel
							user_data = get_user_data_from_api(vote[0])
							if vote[0].user_data:
								extra_data = ast.literal_eval(vote[0].user_data)
								user_data.update(extra_data)
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				elif question_type == "rank":
					for c_index,choice in enumerate(choice_list):
						excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
						answer_text = 0
						vote = VoteApi.objects.filter(unique_key=unique_key,choice=choice)
						if vote:
							rank = vote[0].voteRankOrValue
							answer_text = rank
							user_data = get_user_data_from_api(vote[0])
							if vote[0].user_data:
								extra_data = ast.literal_eval(vote[0].user_data)
								user_data.update(extra_data)
						answer_texts.append(answer_text)
						excel_texts.append(excel_text)
				if survey_question.add_comment:
					excel_texts.append("Comments")
					additionalComment = VoteApi.objects.filter(unique_key=unique_key, question=question)
					if additionalComment:
						answer_texts.append(additionalComment[0].answer_text)
					else:
						answer_texts.append("No Comments")
				i,j = write_demographics_into_excel(ws1,user_data,demo_list,i)
				if answer_texts:
					for ans_index,answer in enumerate(answer_texts):
						write_result_into_excel(ws1,excel_texts[ans_index],answer,i,j+index+ans_index+addVal)
					addVal += ans_index
				else:
					write_result_into_excel(ws1,excel_text,answer_text,i,j+index+addVal)
			i += 1
		wb.save(response)
		return response
	if request.GET.get("qid"):
		question_id = int(request.GET.get("qid",-1))
		try:
			question = Question.objects.get(pk=question_id)
		except:
			errors['notfound'] = "Poll provided not found"
			return HttpResponseNotFound(errors,content_type="application/json")
		response = HttpResponse(content_type='application/ms-excel')
		fname = "Poll_%s_Data.xls"%(question_id)
		response['Content-Disposition'] = 'attachment; filename=%s' % fname
		wb = xlwt.Workbook()
		ws0 = wb.add_sheet('Definitions', cell_overwrite_ok=True)
		ws1 = wb.add_sheet('Raw Data', cell_overwrite_ok=True)
		# write to the description sheet
		write_to_description(ws0,"poll")
		# description sheet end
		ws1.write(0,0,"Country",normal_style)
		ws1.write(0,1,"State",normal_style)
		ws1.write(0,2,"City",normal_style)
		ws1.write(0,3,"Gender",normal_style)
		ws1.write(0,4,"Age Group",normal_style)
		ws1.write(0,5,"Profession",normal_style)
		ws1.write(0,6,"Result",normal_style)
		i = 1
		voted_list = Voted.objects.filter(question_id = question_id)
		considered_email = []
		choice_list = Choice.objects.filter(question_id=question.id)
		for voted in voted_list:
			j = 6
			vote_user = voted.user
			considered_email.append(vote_user.email)
			user_data = {}
			for c_index,choice in enumerate(choice_list):
				vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
				if vote:
					answer_text = c_index+1
					ws1.write(i,j,answer_text,normal_style)
					user_data = ast.literal_eval(vote[0].user_data)
					j += 1
			gender = user_data["gender"]
			age = user_data["birthDay"]
			profession = user_data["profession"]
			ws1.write(i,0,user_data["country"],normal_style)
			ws1.write(i,1,user_data["state"],normal_style)
			ws1.write(i,2,user_data["city"],normal_style)
			ws1.write(i,3,gender_excel_dic.get(gender),normal_style)
			ws1.write(i,4,get_age_group_excel(age),normal_style)
			ws1.write(i,5,prof_excel_dic.get(profession),normal_style)
			i += 1
		voted_list = VoteApi.objects.filter(question_id = question_id)
		for voted in voted_list:
			j = 6
			if voted.email and voted.email in considered_email:
				continue
			if voted.gender and voted.age and voted.profession:
				ws1.write(i,0,voted.country,normal_style)
				ws1.write(i,1,voted.state,normal_style)
				ws1.write(i,2,voted.city,normal_style)
				ws1.write(i,3,gender_excel_dic.get(voted.gender),normal_style)
				ws1.write(i,4,get_age_group_excel(voted.age),normal_style)
				ws1.write(i,5,prof_excel_dic.get(voted.profession),normal_style)
				for c_index,choice in enumerate(choice_list):
					if voted.choice == choice:
						answer_text = c_index+1
						ws1.write(i,j,answer_text,normal_style)
						j += 1
				i += 1
		wb.save(response)
		return response
	errors['notfound'] = "No data provided"
	return HttpResponseNotFound(errors,content_type="application/json")

def write_to_description(ws0, obj_type="survey"):
	ws0.col(0).width = 25*256
	i = 0
	if obj_type == "survey":
		ws0.write(i,0,"Single Select Questions Have 1 as lowest & 5 as highest Rating",normal_style)
		i += 1
		ws0.write(i,0,"Multi Select Questions are displayed as Q_Choice No & its respective rating",normal_style)
		i += 2
	ws0.write_merge(i,i,0,1,"Gender",border_style)
	i += 1
	ws0.write(i,0,"Male",border_style)
	ws0.write(i,1,1,border_style)
	i += 1
	ws0.write(i,0,"Female",border_style)
	ws0.write(i,1,2,border_style)
	i += 1
	ws0.write(i,0,"Not Disclosed",border_style)
	ws0.write(i,1,3,border_style)
	i += 2
	ws0.write_merge(i,i,0,1,"Age Group",border_style)
	x = i + 1
	for key,val in age_excel_dic.items():
		ws0.write(x,0,val,border_style)
		ws0.write(x,1,key,border_style)
		x += 1
	x += 1
	ws0.write_merge(x,x,0,1,"Profession",border_style)
	x += 1
	sorted_prof_excel_dic = sorted(prof_excel_dic.items(), key=operator.itemgetter(1))
	for key_val in sorted_prof_excel_dic:
		ws0.write(x,0,key_val[0],border_style)
		ws0.write(x,1,key_val[1],border_style)
		x += 1

def get_age_group_excel(age):
	res = -1
	if age:
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
					if not choice_dict.get(numVotes):
						choice_dict[numVotes] = []
					choice_dict[numVotes].append("Choice " + str(index+1)) # + " : " + str(numVotes))
					if(numVotes >= maxVotedCount):
						maxVotedCount = numVotes
						maxVotedChoice = choice.id
						maxVotedChoiceStr = "Choice"+str(index+1)
					if(numVotes <= minVotedCount):
						minVotedCount = numVotes
					for vote in Vote.objects.filter(choice_id = choice.id):
						choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
						total_choice_vote += 1
						age = vote.user.extendeduser.calculate_age()
						if age > 25 and age < 31:
							choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count_filter.get("choice"+str(index+1),0) + 1
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
								choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count_filter.get("choice"+str(index+1),0) + 1
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
		return context

class PDFPollView(generic.DetailView):
	model = Question

	def get_template_names(self):
		template_name = "polls/pdf_report_poll.html"
		return [template_name]

	def get_context_data(self, **kwargs):
		context = super(PDFPollView, self).get_context_data(**kwargs)
		question = context['question']
		questionChoices = question.choice_set.all()
		totalResponses = question.voted_set.count()
		maxVotes = -1
		minVotes = 99999
		maxVotedChoiceList = []
		minVotedChoiceList = []
		maxVotedChoice = ""
		maxVotedChoiceStr = ""
		maxVotedCount = -1
		minVotedCount = 99999
		choice_dict = {}
		choice_vote_count = {}
		choice_vote_count_all = {}
		total_choice_vote = 0
		total_choice_vote_all = 0
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
		for index,choice in enumerate(questionChoices):
			choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0)
			choice_vote_count_all["choice"+str(index+1)] = choice_vote_count_all.get("choice"+str(index+1),0)
			choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count_filter.get("choice"+str(index+1),0)
			vote_set = choice.vote_set
			numVotes = vote_set.count()
			vote_api_set = choice.voteapi_set
			numVotes += vote_api_set.count()
			if(numVotes >= maxVotedCount):
				maxVotedCount = numVotes
				maxVotedChoice = choice.id
				maxVotedChoiceStr = "Choice"+str(index+1)
			for vote in Vote.objects.filter(choice_id = choice.id):
				choice_vote_count["choice"+str(index+1)] = choice_vote_count.get("choice"+str(index+1),0) + 1
				total_choice_vote += 1
				choice_vote_count_all["choice"+str(index+1)] = choice_vote_count_all.get("choice"+str(index+1),0) + 1
				total_choice_vote_all += 1
				user_data = ast.literal_eval(voteUser.user_data)
				gender = user_data["gender"]
				age = user_data["birthDay"]
				profession = user_data["profession"]
				country = user_data["country"]
				# age = vote.user.extendeduser.calculate_age()
				if age > 25 and age < 31:
					choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count_filter.get("choice"+str(index+1),0) + 1
					total_choice_vote_filter += 1
				# gender = vote.user.extendeduser.gender
				# profession = vote.user.extendeduser.profession
				# country = vote.user.extendeduser.country
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
				choice_vote_count_all["choice"+str(index+1)] = choice_vote_count_all.get("choice"+str(index+1),0) + 1
				total_choice_vote_all += 1
				if age and gender and profession:
					if age > 25 and age < 31:
						choice_vote_count_filter["choice"+str(index+1)] = choice_vote_count_filter.get("choice"+str(index+1),0) + 1
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
		# survey_polls.append({ "question":x.question, "q_type":x.question_type, "totalResponses":totalResponses, "maxVotes":choice_dict.get(maxVotedCount,""), "minVotes":choice_dict.get(minVotedCount,""), "choice_graph":choice_vote_count, "choice_graph_filter":choice_vote_count_filter, "total_choice_vote":total_choice_vote, "total_choice_vote_filter":total_choice_vote_filter, "age_graph":age_dict, "gender_graph":gender_dict, "prof_graph":prof_dict, "country_graph":country_dict, "age_graph_filter":age_dict_filter,"gender_graph_filter":gender_dict_filter, "prof_graph_filter":prof_dict_filter, "country_graph_filter":country_dict_filter, "maxVotedChoiceStr":maxVotedChoiceStr, "que_text_answers":que_text_answers })
		context["choice_graph"] = choice_vote_count
		context["choice_graph_all"] = choice_vote_count_all
		context["choice_graph_filter"] = choice_vote_count_filter
		context["total_choice_vote"] = total_choice_vote
		context["total_choice_vote_all"] = total_choice_vote_all
		context["total_choice_vote_filter"] = total_choice_vote_filter
		context["age_graph"] = age_dict
		context["gender_graph"] = gender_dict
		context["prof_graph"] = prof_dict
		context["country_graph"] = country_dict
		context["age_graph_filter"] = age_dict_filter
		context["gender_graph_filter"] = gender_dict_filter
		context["prof_graph_filter"] = prof_dict_filter
		context["country_graph_filter"] = country_dict_filter
		context["maxVotedChoiceStr"] = maxVotedChoiceStr
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

def sendPollMail(request):
	try:
		emailList = request.POST.get('emailList',"").split(';')
		emailListFromFile = request.POST.get('emailListFromFile',"").split(';')
		emailList.extend(emailListFromFile)
		questionId = request.POST.get('questionId')
		gethtml = request.POST.get('gethtml',"false").lower().replace("false","")
		savehtml = request.POST.get('savehtml',"false").lower().replace("false","")
		gettemplate = request.POST.get('gettemplate',"false").lower().replace("false","")
		emailtemplatename = request.POST.get('widgetType')
		sender = request.user
		response = {}
		digestmod = hashlib.sha1
		emailtemplate = EmailTemplates.objects.filter(name=emailtemplatename)
		defaultTemplate = EmailTemplates.objects.filter(name="basic_abp")[0]
		emailList = filter(bool, emailList)
		emailList = list(set(emailList))
		if emailtemplate:
			emailtemplate = emailtemplate[0]
		else:
			emailtemplate = EmailTemplates.objects.get(pk=1)
		if not emailList and not gethtml and not savehtml and not gettemplate:
			response['error'] = "You have not provided any mail Id's"
			return HttpResponse(json.dumps(response),content_type='application/json')
		else:
			question = Question.objects.get(pk=questionId)
			questionChoices = question.choice_set.all()
			extra_context_data = {}
			body_file_path = defaultTemplate.get_file_path()
			if request.POST.get("subject","undefined") != "undefined":
				mail_subject = request.POST.get("subject","").strip()
			else:
				mail_subject = emailtemplate.subject
			if request.POST.get("body1","undefined") != "undefined":
				body1 = request.POST.get("body1","").strip()
			else:
				body1 = emailtemplate.body1
			if request.POST.get("body2","undefined") != "undefined":
				body2 = request.POST.get("body2","").strip()
			else:
				body2 = emailtemplate.body2
			if request.POST.get("salutation","undefined") != "undefined":
				salutation = request.POST.get("salutation","").strip()
			else:
				salutation = emailtemplate.salutation
			if savehtml:
				templateName = request.POST.get("templateName","").strip()
				companytemplatename = templateName + "---" + request.user.extendeduser.company.company_slug
				if not templateName:
					response["error"] = "Template name required!"
				elif EmailTemplates.objects.filter(name=companytemplatename):
					response["error"] = "Template already exists!"
				if not response:
					emailtemplate = EmailTemplates(company=request.user.extendeduser.company, name=companytemplatename.strip(),body_image=defaultTemplate.body_image, subject=mail_subject.strip(), body1=body1.strip(), body2=body2.strip(), salutation=salutation.strip() )
					emailtemplate.save()
					response["display_name"] = templateName
					response["name"] = companytemplatename
				return HttpResponse(json.dumps(response),content_type='application/json')
			extra_context_data["body1"] = body1
			extra_context_data["body2"] = body2
			extra_context_data["salutation"] = salutation
			extra_context_data["user"] = request.user
			extra_context_data["body_file_path"] = body_file_path
			extra_context_data["abp"] = Company.objects.get(pk=2)
			html_message = get_widget_html(poll=question, widgetFolder="emailtemplates", widgetType="basic", extra_context_data=extra_context_data)
			html_message_form = get_widget_html(poll=question, widgetFolder="emailtemplates", widgetType="basic_form", extra_context_data=extra_context_data)
			if gethtml:
				response["success"] = html_message
				response["success_form"] = html_message_form
				response["mail_subject"] = mail_subject
				return HttpResponse(json.dumps(response),content_type='application/json')
			if gettemplate:
				response["body1"] = body1
				response["body2"] = body2
				response["salutation"] = salutation
				response["mail_subject"] = mail_subject
				return HttpResponse(json.dumps(response),content_type='application/json')

			invalidEmailList = []
			failEmailList = []
			for email in emailList:
				if email.strip():
					email = email.strip().replace(" ","")
					if not validateEmail(email):
						invalidEmailList.append(email)
					else:
						# generating unique token for every mail
						msg = ("%s %s"%(email, str(time.time()))).encode('utf-8')
						token = hmac.HMAC(shakey, msg, digestmod).hexdigest()
						extra_context_data["token"] = token
						html_message = get_widget_html(poll=question, widgetFolder="emailtemplates", widgetType="basic", extra_context_data=extra_context_data)
						try:
							send_mail(mail_subject,"", request.user.extendeduser.company.name + '< ' + 'support@askbypoll.com' + ' >',[email],html_message=html_message)
							pollToken = PollTokens(token=token,email=email,question=question)
							pollToken.save()
						except Exception as e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
							sendMailAgain = True
							while sendMailAgain:
								try:
									send_mail(mail_subject,"", request.user.extendeduser.company.name + '< ' + 'support@askbypoll.com' + ' >',[email],html_message=html_message)
									pollToken = PollTokens(token=token,email=email,question=question)
									pollToken.save()
									sendMailAgain = False
								except Exception as e:
									exc_type, exc_obj, exc_tb = sys.exc_info()
									print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			if invalidEmailList:
				response['fail'] = "%s invalid emails were provided"%(len(invalidEmailList))
			response['success'] = "Mail sent successfully to %s recipients"%((len(emailList)-len(invalidEmailList)))
			return HttpResponse(json.dumps(response),content_type='application/json')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))

def emailResponse(request):
	try:
		response = {}
		responderKey = request.GET.get('responder')
		choiceId = request.GET.get('choice')
		responderDetails = PollTokens.objects.filter(token=responderKey)
		tokenSentTime = responderDetails[0].timestamp
		tokenExpiryTime = tokenSentTime + datetime.timedelta(days = 10)
		tokenExpiryTime = tokenExpiryTime.replace(tzinfo=None)
		currentTime = timezone.now();
		tokenExpired = False

		if responderDetails:
			mailId = responderDetails[0].email
			questionId = responderDetails[0].question.id
			user = User.objects.filter(email=mailId)
			question = Question.objects.get(pk=questionId)
			choice = Choice.objects.get(pk=choiceId)
			extra_args = {}
			qExpiry = question.expiry

			if qExpiry and currentTime > qExpiry:
				extra_args = {"question_expired":True}
			else:
				if user:
					#if user is already registered on the askbypoll portal
					user = user[0]
					user.backend = 'django.contrib.auth.backends.ModelBackend'
					login(request, user)
				else:
					user = create_new_user_mail_login(request,mailId,question)
				# if all demographics are not present redirect and take note of choice
				if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
					extra_args = {"choice":choice.id,"question":question.id}
				else:
					save_poll_vote(user,question,choice)
			url = reverse('polls:polls_vote', kwargs={'pk':question.id,'que_slug':question.que_slug})
			if extra_args:
				url += "?"
				for a in extra_args:
					url += a + "=" + str(extra_args[a]) + "&"
				url = url[:-1]
		else:
			pass
			#question not found show question deleted page with redirect to home
		return HttpResponseRedirect(url)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))

def save_poll_vote_data(request):
	try:
		data = {}
		if request.POST.get('age'):
			user_age = int(request.POST.get('age',18))
		if request.POST.get('gender',"D") != "notSelected":
			gender = request.POST.get('gender',"D")[0]
		if request.POST.get('profession',"Others") != "notSelected":
			profession = request.POST.get('profession','Others')
		email = request.POST.get('email','').strip()
		pollId = int(request.POST.get('question').strip())
		choiceId = int(request.POST.get('choice').strip())
		sessionKey = request.POST.get('sessionKey','').strip()
		src = request.POST.get('src','').strip()
		ipAddress = getIpAddress(request)
		existingVote = VoteApi.objects.filter(question_id=pollId,choice_id=choiceId,ipAddress=ipAddress, session=sessionKey, src=src).order_by('-created_at')
		if existingVote:
			existingVote = existingVote[0]
			existingVote.age = user_age
			existingVote.gender = gender
			existingVote.profession = profession
			if not email:
				email = None
			existingVote.email = email
			existingVote.save()
			user_data = {}
			if user_age > 0:
				birthDay = datetime.date.today() - datetime.timedelta(days = user_age * 365)
				user_data["birthDay"] = birthDay
			user_data["gender"] = gender
			user_data["profession"] = profession
			user_data["country"] = existingVote.country
			user_data["state"] = existingVote.state
			user_data["city"] = existingVote.city
			if email:
				if User.objects.filter(email=email):
					newUser = User.objects.filter(email=email)[0]
					login_user(request,newUser)
				else:
					newUser = create_new_user_mail_login(request,email,pollId)
					save_extendeduser_data(newUser,user_data)
				save_poll_vote(newUser,pollId,choiceId)
				existingVote.delete()
				data["removecookies"] = True
		return HttpResponse(json.dumps(data), content_type='application/json')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))

def save_extendeduser_data(newUser,user_data):
	if user_data:
		extendeduser = newUser.extendeduser
		for key,val in user_data.items():
			if hasattr(extendeduser, key):
				setattr(extendeduser, key, val)
		extendeduser.save()
	return newUser

def save_user_vote_data(user_data,alreadyVoted):
	if user_data:
		extra_data = {}
		for key,val in user_data.items():
			if hasattr(alreadyVoted, key):
				setattr(alreadyVoted, key, val)
			else:
				extra_data[key] = val
		if extra_data:
			alreadyVoted.user_data = str(extra_data)
		alreadyVoted.save()

def save_poll_vote_widget(request, pollId, choiceId, answer_text=None, user_data=None, unique_key=None, votecolumn=None, voteRank=None, forced_add = False):
	try:
		ipAddress = getIpAddress(request)
		if not request.session.exists(request.session.session_key):
			request.session.create()
		sessionKey = request.session.session_key
		question = Question.objects.get(pk=pollId)
		url = "http://api.db-ip.com/addrinfo?addr="+ipAddress+"&api_key=ab6c13881f0376231da7575d775f7a0d3c29c2d5"
		dbIpResponse = requests.get(url)
		locationData = dbIpResponse.json()
		if not choiceId:
			choiceId = settings.ZERO_CHOICE
		votedChoice = Choice.objects.get(pk=choiceId)
		src = request.GET.get('src','')
		isSurveyQuestion = Survey_Question.objects.filter(question=question)
		alreadyVoted = None
		
		alreadyVoted = VoteApi.objects.filter(question=question, choice_id=choiceId, ipAddress=ipAddress, session=sessionKey, src=src)
		
		if unique_key and isSurveyQuestion and (not isSurveyQuestion[0].question_type == 'checkbox' and not isSurveyQuestion[0].question_type == 'matrixrating' and not isSurveyQuestion[0].question_type == 'rank'):
			alreadyVoted = VoteApi.objects.filter(question=question,ipAddress=ipAddress, session=sessionKey, src=src, unique_key=unique_key)
			
		if(isSurveyQuestion and (not isSurveyQuestion[0].question_type == 'checkbox' and not isSurveyQuestion[0].question_type == 'matrixrating' and not isSurveyQuestion[0].question_type == 'matrixrating')):
			if(user_data.get('email','')):
				alreadyVoted = VoteApi.objects.filter(question=question,email=user_data['email'])

		giveData = {}				
		if not alreadyVoted or forced_add:
			votedChoiceFromApi = VoteApi(choice=votedChoice,question=question,country=regionDict[locationData['country']] ,city=locationData['city'],state=locationData['stateprov'],ipAddress=ipAddress, session=sessionKey, src=src, answer_text=answer_text, unique_key=unique_key, votecolumn=votecolumn, voteRankOrValue=voteRank)
			votedChoiceFromApi.save()
			alreadyVoted = votedChoiceFromApi
			giveData["noData"] = True
		elif alreadyVoted:
			alreadyVoted = alreadyVoted[0]
			if not (alreadyVoted.age and alreadyVoted.gender and alreadyVoted.profession):
				giveData["noData"] = True
			else:
				giveData["allData"] = True
		giveData["sessionKey"] = sessionKey
		giveData["choice"] = choiceId
		if user_data:
			extra_data = {}
			for key,val in user_data.items():
				if hasattr(alreadyVoted, key):
					setattr(alreadyVoted, key, val)
				else:
					extra_data[key] = val
			if extra_data:
				alreadyVoted.user_data = str(extra_data)
			if alreadyVoted:
				alreadyVoted.save()
		return giveData
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))

def save_poll_vote(user,question,choice,queBet=None):
	try:
		questionId = int(question)
		question = Question.objects.get(pk=questionId)
	except:
		pass
	try:
		choiceId = int(choice)
		choice = Choice.objects.get(pk=choiceId)
	except:
		pass
	userVoteOnQuestion, created = Voted.objects.get_or_create(user=user,question=question)
	if created:
		userVote,created = Vote.objects.get_or_create(user=user, choice=choice)
		subscriber,created = Subscriber.objects.get_or_create(user=user,question=question)
		after_poll_vote_credits_activity(question,user,queBet)
		return True
	return False

def after_poll_vote_credits_activity(question,user,queBet=None):
	points = 0
	visible_public = True
	if question.privatePoll:
		visible_public = False

	activity = {'actor': user.username, 'verb': 'voted', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug,"visible_public":visible_public}
	if question.isBet and queBet:
		user.extendeduser.credits -= queBet
		user.extendeduser.credits += 20
		points = 20
		activity = {'actor': user.username, 'verb': 'credits', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":queBet, "action":"voteBet","visible_public":visible_public}
		feed = client.feed('notification', user.id)
		feed.add_activity(activity)
		activity = {'actor': user.username, 'verb': 'votedBet', 'object': question.id, 'question_text':question.question_text, 'question_desc':question.description, 'question_url':'/polls/'+str(question.id)+'/'+question.que_slug, 'actor_user_name':user.username,'actor_user_pic':user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(user.id)+"/"+user.extendeduser.user_slug, "points":queBet,"visible_public":visible_public}
	else:
		if question.privatePoll:
			user.extendeduser.credits += 20
			points = 20
		else:
			user.extendeduser.credits += 10 #for voting on normal question
			points = 10
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

def create_new_user_mail_login(request,mailId,question):
	try:
		questionId = int(question)
		question = Question.objects.get(id=questionId)
	except:
		pass 
	password = 'welcome'+mailId.split('@')[0]
	newUser = User(first_name="User",email=mailId,username=mailId)
	newUser.set_password(password)#no need to manually encrypt password using this
	newUser.save()
	new_extended_user = ExtendedUser(user=newUser)
	new_extended_user.save()
	newUserMailStatus = EmailAddress(email=mailId, verified=1, primary=1, user=newUser)
	newUserMailStatus.save()
	newUser.backend = 'django.contrib.auth.backends.ModelBackend'
	login(request, newUser)
	# Sending registration details to new users
	msg = EmailMessage(subject="Thank you mail", from_email="support@askbypoll.com",to=[mailId])
	msg.template_name = "emailwidgetregisterationmail"
	msg.global_merge_vars = {
		"questionText" : question.question_text,
		"userName" : mailId,
		"password" : password
	}
	msg.send()
	return newUser

def login_user(request,newUser):
	newUser.backend = 'django.contrib.auth.backends.ModelBackend'
	login(request, newUser)

def validateEmail(email):
	if not EMAIL_REGEX.match(email):
		return False
	return True

def get_user_referral_id(user_id=None,referral=""):
	import math
	refer_list = ['M','P','J','S','G','V','D','Y','A','K']
	if user_id:
		user_referral = ""
		ref_user = user_id
		while ref_user > 0:
			char_int = ref_user % 10
			ref_user = int(ref_user / 10)
			user_referral += refer_list[char_int]
		user_referral += "_ABP"
		return user_referral
	if referral:
		user_id = 0
		user_referral = referral
		user_referral = referral[:-4]
		for index,char_char in enumerate(user_referral):
			char_int = refer_list.index(char_char)
			user_id = int((math.pow(10,index) * char_int) + user_id)
		return user_id

def save_references(referral_user, poll = None, survey = None, referred_user = None):
	try:
		if referral_user:
			referral_user_id = get_user_referral_id(referral = referral_user)
			if poll:
				poll_refer, created = PollsReferred.objects.get_or_create(user_id=referral_user_id, referred_question=poll)
				poll_refer.referred_question_count += 1
				poll_refer.save()
			if survey:
				survey_refer, created = SurveysReferred.objects.get_or_create(user_id=referral_user_id, referred_survey=survey)
				survey_refer.referred_survey_count += 1
				survey_refer.save()
			if referred_user:
				user_refer, created = UsersReferred.objects.get_or_create(user_id=referral_user_id, referred_user=referred_user)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))

class ArticleView(BaseViewList):

	def get_template_names(self, **kwargs):
		template_name = self.request.path.replace("/article/","") + '.html'
		return [template_name]

	def get_queryset(self):
		context = {}
		return context

class AskByPollBusinessView(BaseViewList):
	template_name = 'abpBusiness/askbypoll-for-business.html'
	context_object_name = "abp_solutions"
	def get_queryset(self):
		import polls.abp_business_constants as abp_business_constants
		context = {}
		context["solution_caption"] = abp_business_constants.solution_caption
		return context

class AskByPollBusinessCategoryView(BaseViewList):
	template_name = 'abpBusiness/askbypoll-for-category.html'
	context_object_name = "abp_solution"
	def get_queryset(self):
		category_name = self.request.path.replace("/askbypoll-for-business/","")
		context = {}
		import polls.abp_business_constants as abp_business_constants
		for category_dict in abp_business_constants.solution_caption:
			for key, val in category_dict.items():
				if key == category_name:
					context["details"] = val["details"]
					context["brief"] = val["brief"]
			if context:
				break
		context["category"] = category_name
		return context

class AskByPollCaseStudyView(BaseViewList):
	template_name = 'abpBusiness/askbypoll-case-study.html'
	def get_queryset(self):
		return {}

class AskByPollAboutUsView(BaseViewList):
	template_name = 'askbypoll-about-us.html'
	def get_queryset(self):
		return {}

def get_number_votes(mainquestion):
	numVotes = mainquestion.voted_set.count()
	considered_email = []
	for voted in Voted.objects.filter(question=mainquestion):
		considered_email.append(voted.user.email)
	# numVotes += VoteApi.objects.filter(question=mainquestion).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).exclude(email__in=considered_email).count()
	numVotes += VoteApi.objects.filter(question=mainquestion).exclude(email__in=considered_email).count()
	return numVotes

def get_index_question_detail(request,mainquestion,user,sub_que,curtime,company_data={}):
	data = {}
	followers = [ x.user for x in Follow.objects.filter(target_id=mainquestion.user_id,deleted_at__isnull=True) ]
	following = [ x.target for x in Follow.objects.filter(user_id=mainquestion.user_id,deleted_at__isnull=True) ]
	data['connection'] = len(followers) + len(following)
	data ['question'] = mainquestion
	subscribers = mainquestion.subscriber_set.count()
	data['votes'] = get_number_votes(mainquestion)
	data['subscribers'] = subscribers
	subscribed = False
	if mainquestion.id in sub_que:
		subscribed = True
	data['subscribed'] = subscribed
	data['expired'] = False
	data['upvoteCount'] = mainquestion.upvoteCount
	upvotes = QuestionUpvotes.objects.filter(question=mainquestion)
	data['upvotedusers'] = [ x.user for x in upvotes if x.vote==1 ]
	data['downvotedusers'] = [ x.user for x in upvotes if x.vote==0 ]
	data['editable'] = mainquestion.iseditable(user)
	if mainquestion.id == 3051:
		data['votes'] += 100
		data['subscribers'] += 150
	if mainquestion.expiry and mainquestion.expiry < curtime:
		data['expired'] = True
	user_already_voted = False
	dataProvided = False
	if user.is_authenticated():
		question_user_vote = Voted.objects.filter(user=user,question=mainquestion)
		if question_user_vote:
			user_already_voted = True
			dataProvided = True
	else:
		votedCookie = cookie_prepend+"VOTED_"+str(mainquestion.id)
		user_already_voted = checkBooleanValue(request.COOKIES.get(votedCookie,""))
		dataCookie = cookie_prepend+"DATA_GIVEN_"+str(mainquestion.id)
		dataProvided = checkBooleanValue(request.COOKIES.get(dataCookie,""))
	data["dataProvided"] = dataProvided
	data['user_already_voted'] = user_already_voted
	data["company_data"] = company_data
	return data

class AutoPopulateVotesView(BaseViewList):
	template_name = 'voteonq.html'

	def get_queryset(self):
		context = {}
		return context

	def post(self, request, *args, **kwargs):
		try:
			messages = {}
			numVotes = int(request.POST.get('numberOfVotes'))
			userList = request.POST.get('userList','').split(';')
			userList = [x for x in userList if x.strip()]
			questionId = request.POST.get('questionId','')
			voteDistributionList = request.POST.get('voteDistribution','').split(':')
			voters = []
			if int(numVotes) < len(userList) or int(numVotes) == len(userList):
				for i in range(numVotes):
					mail = userList[i]
					if(not mail == '' or not mail == None):
						user = User.objects.filter(email=mail)
						if user:
							voters.append(user[0])
						else:
							messages['errorMessage'] = mail + ' is not a valid user'
							return HttpResponse(json.dumps(messages), content_type='application/json')
				question = Question.objects.get(pk=questionId)
				questionChoiceList = Choice.objects.filter(question=question).order_by('id')
				shuffle(voters)
				for i in range(len(questionChoiceList)):
					currentChoice = questionChoiceList[i]
					try:
						numOfVotesChoice = int(voteDistributionList[i])
					except:
						numOfVotesChoice = 0
					for i in range(numOfVotesChoice):
						voteUser = voters[0]
						if voteUser.extendeduser.birthDay and voteUser.extendeduser.gender and voteUser.extendeduser.city and voteUser.extendeduser.state and voteUser.extendeduser.country and voteUser.extendeduser.profession:
							save_poll_vote(voteUser,question,currentChoice)
						del voters[0]
				messages['success'] = 'Votes populated successfully'
				return HttpResponse(json.dumps(messages), content_type='application/json')
			else:
				messages['errorMessage'] = 'Not sifficient users to vote'
				return HttpResponse(json.dumps(messages), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			messages['errorMessage'] = 'Some error occured'
			return HttpResponse(json.dumps(messages), content_type='application/json')

class SendMails(BaseViewList):

	def post(self,request,*args,**kwargs):
		subject = ""
		message = ""
		error = {}
		err_msg = ""
		if request.GET.get("request","demo") or request.GET.get("request","free-trial"):
			subject = "Get Demo/Trial"
			name = request.POST.get("name","").strip()
			email = request.POST.get("email","").strip()
			phone = request.POST.get("phone","").strip()
			msg = request.POST.get("message","Hi there!!").strip()
			if not name:
				err_msg += "Name is required<br>"
			if not email:
				err_msg += "Email is required<br>"
			if err_msg:
				error["msg"] = err_msg
				return HttpResponse(json.dumps(error),content_type='application/json')
			message = " Name : "+name+"\n Email : "+email+"\n Phone : "+phone+"\n\n "+msg
		send_mail(subject, message, 'support@askbypoll.com',['shradha@askbypoll.com'], fail_silently=False)
		data = {}
		return HttpResponse(json.dumps(data),content_type='application/json')

class WidgetsView(BaseViewList):
	context_object_name = "data"
	def get_template_names(self):
		template_name = "widgets/index.html"
		return [template_name]
	def get_queryset(self):
		webWidgets = ["basic"]
		feedbackWidgets = ["feedback1", "feedback2"]
		webTemplatesFinal = []
		feedbackTemplatesFinal = []
		for x in webWidgets:
			webTemplatesFinal.append("polls/webtemplates/"+x+"_widget_template.html")
		for x in feedbackWidgets:
			feedbackTemplatesFinal.append("polls/webtemplates/"+x+"_widget_template.html")
		context = {}
		context["poll_templates"] = webTemplatesFinal
		context["feedback_template"] = feedbackTemplatesFinal
		context["demo_poll_text"] = Question.objects.get(id=4)
		context["demo_poll_image"] = Question.objects.get(id=5)
		context["demo_poll_feedback"] = Question.objects.get(id=3)
		mypolls = Question.objects.filter(user_id=self.request.user.id)
		context["mypolls"] = mypolls
		return context

class WebsiteWidgetTemplateView(generic.ListView):
	def post(self, request, *args, **kwargs):
		poll = request.POST.get("poll")
		widget_type = request.POST.get("widgetType")
		template = get_widget_html(poll=poll, widgetFolder="webtemplates", widgetType=widget_type, extra_context_data = {})
		data = {}
		data["template"] = template
		return HttpResponse(json.dumps(data),content_type='application/json')

def get_demographic_list(survey_id=None,question_id=None):
	extra_demographics = None
	demo_list = []
	if survey_id:
		extra_demographics = Demographics.objects.filter(survey_id=survey_id)
	elif question_id:
		extra_demographics = Demographics.objects.filter(question_id=question_id)
	if extra_demographics:
		extra_demographics = ast.literal_eval(extra_demographics[0].demographic_data)
		for key,val in extra_demographics.items():
			demo_list.append(key)
	return demo_list

def write_demographics_into_excel(ws1,user_data,demo_list,i):
	gender = user_data.get("gender","")
	age = user_data.get("birthDay")
	profession = user_data.get("profession","")
	ws1.write(i,0,user_data.get("country"),normal_style)
	ws1.write(i,1,user_data.get("state"),normal_style)
	ws1.write(i,2,user_data.get("city"),normal_style)
	ws1.write(i,3,gender_excel_dic.get(gender),normal_style)
	ws1.write(i,4,get_age_group_excel(age),normal_style)
	ws1.write(i,5,prof_excel_dic.get(profession),normal_style)
	j = 6
	for key in demo_list:
		ws1.write(0,j,key,normal_style)
		ws1.write(i,j,user_data.get(key),normal_style)
		j += 1
	return i,j

def write_result_into_excel(ws1,excel_text,answer_text,i,j):
	ws1.write(0,j,excel_text,normal_style)
	ws1.write(i,j,answer_text,normal_style)
	return i,j

def get_user_data_from_api(vote,user_data={}):
	user_data["birthDay"] = vote.age
	user_data["gender"] = vote.gender
	user_data["profession"] = vote.profession
	user_data["country"] = vote.country
	user_data["state"] = vote.state
	user_data["city"] = vote.city
	return user_data

def saveVotes(user,survey,votes_list,unique_key,user_data,request):
	try:
		user_voted = 0
		is_authenticated = user.is_authenticated()
		data = {}
		res_data = {}
		success_msg_text = survey.thanks_msg
		for vote in votes_list:
			if vote["type"] in ["text","rating"]:
				if vote["answer"]:
					user_voted += 1
					if is_authenticated:
						votetext = VoteText(user=user, question_id=vote["id"], answer_text=vote["answer"], user_data=user_data)
						votetext.save()
						voted = Voted(user=user, question_id=vote["id"])
						voted.save()
					else:
						res_data = save_poll_vote_widget(request, vote["id"], None, vote["answer"],user_data, unique_key, None)
			elif vote["type"] in ["radio","checkbox"]:
				if vote["choices"]:
					user_voted += 1
					for choice_id in vote["choices"]:
						if is_authenticated:
							choice = Choice.objects.get(pk=int(choice_id))
							uvote = Vote(user=user, choice=choice, user_data=user_data)
							uvote.save()
							voted,created = Voted.objects.get_or_create(user=user, question_id=vote["id"])
						else:
							answer_text = None
							if vote["answer"]:
								answer_text = vote["answer"]
							res_data = save_poll_vote_widget(request, vote["id"], choice_id, answer_text,user_data, unique_key, None, forced_add = True)
				if vote["answer"] and is_authenticated:
					votetext = VoteText(user=user, question_id=vote["id"], answer_text=vote["answer"], user_data=user_data)
					votetext.save()
			elif vote["type"] in ["matrixrating"]:
				if vote["choices"]:
					user_voted += 1
					for index,choiceId in enumerate(vote["choices"]):
						votecolumn = MatrixRatingColumnLabels.objects.get(pk=int(vote["columns"][index]))
						if is_authenticated:
							uvote, created = Vote.objects.get_or_create(user=user, choice_id=choiceId, user_data=user_data)
							if created:
								votedcolumn = VoteColumn(user=user, question_id=vote["id"], choice_id=choiceId, column=votecolumn, vote=uvote)
								votedcolumn.save()
							voted,created = Voted.objects.get_or_create(user=user, question_id=vote["id"])
						else:
							res_data = save_poll_vote_widget(request, vote["id"], choiceId, None,user_data, unique_key, votecolumn, forced_add = True)
			elif vote["type"] in ["rank"]:
				if vote["choices"]:
					user_voted += 1
					for index,choiceId in enumerate(vote["choices"]):
						rank = vote["ranks"][index]
						if is_authenticated:
							uvote, created = Vote.objects.get_or_create(user=user, choice_id=choiceId, user_data=user_data)
							if created:
								voteRank = VoteRankAndValue(user=user, question_id=vote["id"], choice_id=choiceId, rankandvalue=rank, vote=uvote)
								voteRank.save()
							voted,created = Voted.objects.get_or_create(user=user, question_id=vote["id"])
						else:
							res_data = save_poll_vote_widget(request, vote["id"], choiceId, vote['answer'],user_data, unique_key, voteRank=rank, forced_add = True)
				if vote["answer"] and is_authenticated:
					votetext = VoteText(user=user, question_id=vote["id"], answer_text=vote["answer"], user_data=user_data)
					votetext.save()
		if is_authenticated:
			survey_voted = SurveyVoted(user=user, survey=survey, survey_question_count=len(votes_list), user_answer_count=user_voted)
			survey_voted.save()
			if survey_voted.user_answer_count == 0:
				success_msg_text = "You have not answered any questions"
		data["res"] = res_data
		data["success"]=success_msg_text
		return data
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

from django.views.decorators.csrf import csrf_exempt
global users_flock
users_flock = {}
@csrf_exempt
def send(request):
	print ("called send")
	uf = open('/home/ubuntu/askpopulo/uf.txt','a')
	ufr = open('/home/ubuntu/askpopulo/uf.txt','r')
	try:
		print (request.path)
		print (request.POST)
		print (dir(request))
		print (request)
		print (request.GET)
		print (request.COOKIES)
		print (request.body)
		print(type(request.body))
		print(users_flock)
	except:
		pass
	token = "d2f7bf6e8f1bc88e12bbcb706a41da04b1477147115"
	to = 'u:hqbqssxhb7shrx3r'
	context = {}
	if request.method == 'POST':
		user_data = ast.literal_eval(str(request.body,'utf-8'))
		print (user_data)
		uf.write(user_data.get('userId') + " ---- " +user_data.get('token','null')+"\n")
		uf.close()
	else:
		try:
			gd = ast.literal_eval(request.GET.get('flockEvent'))
			for l in ufr.readlines():
				users_flock[l.split(" ---- ")[0]] = l.split(" ---- ")[1].strip()
			ufr.close()
			token = users_flock.get(gd.get('userId'))
			to = gd.get('chat')
			print (token,to)
		except:
			print ("exception")
			pass
	context['token']= token
	context['to']= to
	return render(request, 'register.html', context)

@csrf_exempt
def saveFile(request):
	print("Inside Save")
	print(request.FILES)
	print(request.FILES.get('file'))
	print(request.POST)
	ftype = request.POST.get('type',"webm")
	f = open("/home/ubuntu/askpopulo/media/fh/flockathon."+ftype,"wb")
	if request.FILES.get('file'):
		f.write(request.FILES.get('file').read())
	else:
		from base64 import b64decode
		import base64
		b64file = request.POST.get('file')
		b64file = b64file.replace('data:image/png;base64,', '').replace( ' ', '+')
#		m_p = len(b64file)%4
#		print(m_p)
#		if m_p != 0:
#			b64file += b'='*(4-m_p)
		image_data = b64decode(b64file)
		f.write(image_data)
	f.close()
	data = {}
	data['url'] ="https://www.askbypoll.com/media/fh/flockathon."+ftype
	return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def screen(request):
	token = request.path.split("/")[-1]#get('token')
	to = request.path.split("/")[-2]#GET.get('to')
	print (to,token)
	context = {}
	context['token']= token
	context['to']= to
	return render(request, 'screen.html', context)
