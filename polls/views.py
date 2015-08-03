import os
from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from django.core.mail import send_mail
from polls.models import Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory
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
from login.models import ExtendedUser
from login.forms import MySignupPartForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

# Create your views here.

class IndexView(generic.ListView):
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
			adminpolls = Question.objects.filter(user__is_superuser=1,privatePoll=0).order_by('-pub_date')
			featuredpolls = Question.objects.filter(featuredPoll=1,privatePoll=0).order_by('-pub_date')
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
					category_questions = [x.question for x in que_cat_list if x.question.privatePoll == 0]
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
			latest_questions = [que_cat.question for que_cat in QuestionWithCategory.objects.filter(category = category) if que_cat.question.privatePoll == 0]
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
			latest_questions = Question.objects.filter(privatePoll=0).order_by('-pub_date')
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
			data ['question'] = mainquestion
			subscribers = mainquestion.subscriber_set.count()
			data['votes'] = mainquestion.voted_set.count()
			data['subscribers'] = subscribers
			data['subscribed'] = sub_que
			data['expired'] = False
			if mainquestion.expiry and mainquestion.expiry < curtime:
				data['expired'] = True
			user_already_voted = False
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(user=user,question=mainquestion)
				if question_user_vote:
					user_already_voted = True
			data['user_already_voted'] = user_already_voted
			mainData.append(data)
		context['data'] = mainData
		return mainData

class VoteView(generic.DetailView):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/voteQuestion.html'
		question = self.get_object()
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
				profilepicUrl = r"http://askbypoll.com"+profilepicUrl
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
		if context['question'].expiry and context['question'].expiry < timezone.now():
			context['expired'] = True
		return context

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = request.POST.get('question')
		question = Question.objects.get(pk=questionId)
		queSlug = question.que_slug
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
					vote = Vote(user=user, choice=choice)
					voted = Voted(user=user, question=question)
					subscribed = Subscriber(user=user, question=question)
					vote.save()
					voted.save()
					subscribed.save()
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
		return HttpResponseRedirect(url)
		
class EditView(generic.DetailView):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/editQuestion.html'
		return [template_name]
	
	def get_context_data(self, **kwargs):
		context = super(EditView, self).get_context_data(**kwargs)
		question = self.get_object()
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
		#print(context)
		return context
		
class DeleteView(generic.DetailView):
	model = Question
	
	def get_context_data(self, **kwargs):
		return super(DeleteView, self).get_context_data(**kwargs)
	
	def get(self, request, *args, **kwargs):
		url = reverse('polls:index')
		question = self.get_object()
		question.delete()
		return HttpResponseRedirect(url)

class CreatePollView(generic.ListView):
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
		return context
	
	def post(self, request, *args, **kwargs):
		user = request.user
		edit = False
		ajax = False
		errors = {}
		question = None
		curtime = datetime.datetime.now();
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
					qExpiry = question.expiry
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]
			print(qeyear, qemonth, qeday, qehr, qemin, qeap)
			if qeyear != 0 or qemonth != 0 or qeday != 0 or qehr != 0 or qemin != -1: 
				if qeap.lower() == 'pm' and qehr != 12:
					qehr = qehr + 12
				elif qeap.lower() == 'am' and qehr == 12:
					qehr = 0
				# qExpiry = request.POST.get('qExpiry')
				print(qeyear, qemonth, qeday, qehr, qemin, qeap)
				try:
					qExpiry = datetime.datetime(qeyear, qemonth, qeday,hour=qehr,minute=qemin)
					if qExpiry < curtime:
						raise Exception
				except:
					errors['expiryError'] = "Invalid date time"
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
			if isAnon:
				anonymous = 1
			else:
				anonymous = 0
			if isPrivate:
				private = 1
			else:
				private = 0
			# return if any errors
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
			if edit:
				# question = Question.objects.get(pk=request.GET.get("qid"))
				question.question_text=qText
				question.description=qDesc
				question.expiry=qExpiry
				question.isAnonymous=anonymous
				question.privatePoll=private
			else:
				question = Question(user=user, question_text=qText, description=qDesc, expiry=qExpiry, pub_date=curtime,isAnonymous=anonymous,privatePoll=private)
			question.save()
			sub = Subscriber(user=user,question=question)
			sub.save()
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
			if choice2 or choice2Image:
				choice = Choice(question=question,choice_text=choice2,choice_image=choice2Image)
				choice.save()
			if choice3 or choice3Image:
				choice = Choice(question=question,choice_text=choice3,choice_image=choice3Image)
				choice.save()
			if choice4 or choice4Image:
				choice = Choice(question=question,choice_text=choice4,choice_image=choice4Image)
				choice.save()
		url = reverse('polls:polls_vote', kwargs={'pk':question.id,'que_slug':question.que_slug})
		return HttpResponseRedirect(url)

class PollsSearchView(SearchView):
    
    def extra_context(self):
        queryset = super(PollsSearchView, self).get_results()
        queryset = [x for x in queryset if x.object.privatePoll == 0]
        return {'query': queryset,}

class FollowPollView(generic.ListView):

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

class ReportAbuse(generic.ListView):

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
	# print("comment mail")
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
		# print(index,to_mail)
		# print("&&&&&&&&&&&&")
		# print(que_author[index])
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
	return HttpResponse(json.dumps({}),content_type='application/json')

def error_CompanyName(request):
	return render(request,'error404.html')

class MyUnsubscribeView(generic.ListView):
	template_name = 'unsubscribe.html'

	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		error={}
		ajax = False
		if request.GET.get("ajax"):
			ajax = True
			print("Ajax call detected")
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

