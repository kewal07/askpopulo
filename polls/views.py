import os
from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from django.core.mail import send_mail
from polls.models import Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory
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

# Create your views here.

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'data'
	paginate_by = 50
	
	def get_queryset(self):
		request = self.request
		user = request.user
		context = {}
		mainData = []
		latest_questions = []
		if request.path.endswith('featuredpolls'):
			latest_questions = Question.objects.filter(user__is_superuser=1).order_by('-pub_date')
		elif user.is_authenticated() and request.path.endswith(user.username):
			if user.extendeduser.categories:
				user_categories_list = list(map(int,user.extendeduser.categories.split(',')))
				user_categories = Category.objects.filter(pk__in=user_categories_list)
				que_cat_list = QuestionWithCategory.objects.filter(category__in=user_categories)
				latest_questions = [x.question for x in que_cat_list]
			followed_questions = [x.question for x in Subscriber.objects.filter(user=user)]
			latest_questions.extend(followed_questions)
			if latest_questions:
				latest_questions = list(OrderedDict.fromkeys(latest_questions))
				latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
		elif request.GET.get('category'):
			category_title = request.GET.get('category')
			category = Category.objects.filter(category_title=category_title)[0]
			latest_questions = [que_cat.question for que_cat in QuestionWithCategory.objects.filter(category = category)]
			latest_questions = latest_questions[::-1]
		else:
			latest_questions = Question.objects.order_by('-pub_date')
		subscribed_questions = []
		if user.is_authenticated():
			subscribed_questions = Subscriber.objects.filter(user=request.user)
		sub_que = []
		for sub in subscribed_questions:
			sub_que.append(sub.question.id)
		for mainquestion in latest_questions:
			data = {}
			data ['question'] = mainquestion
			subscribers = mainquestion.subscriber_set.count()
			data['votes'] = mainquestion.voted_set.count()
			data['subscribers'] = subscribers
			data['subscribed'] = sub_que
			user_already_voted = False
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(user=user,question=mainquestion)
				if question_user_vote:
					user_already_voted = True
			data['user_already_voted'] = user_already_voted
			mainData.append(data)
		context['data'] = mainData
		return mainData

# class FeaturedPollView(generic.ListView):
# 	template_name = 'polls/index.html'
# 	context_object_name = 'data'
	
# 	def get_queryset(self):
# 		mainData = []
# 		latest_questions = Question.objects.filter(user__is_superuser=1).order_by('-pub_date')[:10]
# 		for mainquestion in latest_questions:
# 			data = {}
# 			data ['question'] = mainquestion
# 			subscribers = mainquestion.subscriber_set.count()
# 			data['votes'] = mainquestion.voted_set.count()
# 			data['subscribers'] = subscribers
# 			mainData.append(data)
# 		return mainData

class VoteView(generic.DetailView):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/voteQuestion.html'
		question = self.get_object()
		user = self.request.user
		if user.is_authenticated():
			voted = Voted.objects.filter(question = question, user=user)
			if voted or user.id == question.user.id:
				template_name = 'polls/questionDetail.html'
		return [template_name]
	
	def get_context_data(self, **kwargs):
		context = super(VoteView, self).get_context_data(**kwargs)
		user = self.request.user
		subscribed_questions = []
		user_already_voted = False
		if user.is_authenticated():
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
		return context

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = request.POST.get('question')
		question = Question.objects.get(pk=questionId)
		queSlug = question.que_slug
		# queSlug = "None"
		# print(user,user.is_authenticated())
		if user.is_authenticated():
			if request.POST.get('choice'):
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
				# print(questionId,queSlug)
				next_url = reverse('polls:polls_vote', kwargs={'pk':questionId,'que_slug':queSlug})
				# print(next_url)
				url = reverse('account_login')
				url += "?next="+next_url
				# print(url)
				return HttpResponseRedirect(url)
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
		return Category.objects.all()
	
	def post(self, request, *args, **kwargs):
		# url = reverse('polls:index')
		user = request.user
		edit = False
		ajax = False
		errors = {}
		question = None
		if request.GET.get("ajax"):
			ajax = True
		if request.GET.get("qid"):
			edit = True
		if not user.is_authenticated():
			url = reverse('account_login')
		elif request.POST:
			qText = request.POST.get('qText')
			if not qText.strip():
				errors['qTextError'] = "Question required"
			qDesc = request.POST.get('qDesc')
			qExpiry = None
			if edit:
				question = Question.objects.get(pk=request.GET.get("qid"))
				qExpiry = question.expiry
			qeyear = int(request.POST.getlist('qExpiry_year')[0])
			qemonth = int(request.POST.getlist('qExpiry_month')[0])
			qeday = int(request.POST.getlist('qExpiry_day')[0])
			qehr = int(request.POST.getlist('qExpiry_hr')[0])
			qemin = int(request.POST.getlist('qExpiry_min')[0])
			qeap = request.POST.getlist('qExpiry_ap')[0]
			if qeyear != 0 and qemonth != 0 and qeday != 0 and qehr != 0 and qemin != -1: 
				if qeap.lower() == 'pm' and qehr != 12:
					qehr = qehr + 12
				elif qeap.lower() == 'am' and qehr == 12:
					qehr = 0
				# qExpiry = request.POST.get('qExpiry')
				# print(qeyear, qemonth, qeday, qehr, qemin, qeap)
				try:
					qExpiry = datetime.datetime(qeyear, qemonth, qeday,hour=qehr,minute=qemin)
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
			selectedCats = request.POST.get('selectedCategories','').split(",")
			isAnon = request.POST.get('anonymous')
			if isAnon:
				anonymous = 1
			else:
				anonymous = 0
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
			else:
				question = Question(user=user, question_text=qText, description=qDesc, expiry=qExpiry, pub_date=datetime.datetime.now(),isAnonymous=anonymous)
			question.save()
			if edit:
				for choice in question.choice_set.all():
					if choice.choice_image:
						if os.path.isfile(choice.choice_image.path) and choice.choice_image.path not in imagePathList:
							os.remove(choice.choice_image.path)
					choice.delete()
				for que_cat in question.questionwithcategory_set.all():
					que_cat.delete()
			for cat in selectedCats:
				if cat:
					category = Category.objects.filter(category_title=cat)[0]
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
        return {
            'query': queryset,
        }

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

class CategoryView(generic.ListView):
	template_name = 'polls/categories.html'
	context_object_name = 'categories'
	def get_queryset(self):
		mainData = Category.objects.all()
		return mainData

def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(question_auto=request.GET.get('qText', ''))[:5]
    suggestions = [[result.object.question_text,result.object.id,result.object.que_slug] for result in sqs]
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')
