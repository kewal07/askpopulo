import os
from django.shortcuts import render
from django.views import generic
from django.conf import settings
from login.models import ExtendedUser
import allauth
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import resolve,reverse
from django.contrib.auth.views import logout
from allauth.account.forms import ChangePasswordForm,UserForm
from allauth.account.views import PasswordChangeView
from django.template.defaultfilters import slugify
from allauth.account.adapter import get_adapter
from polls.models import Question,Voted,Subscriber
from categories.models import Category
import json
from login.forms import MySignupForm
from django.contrib.auth.models import User
from datetime import date

class EditProfileView(generic.ListView):
	
	def post(self, request, *args, **kwargs):
		url = reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug})
		user = request.user
		extendeduser = user.extendeduser
		print(request.POST)
		# print(request.POST.get('name'))
		if request.POST.get('first_name'):
			user.first_name = request.POST.get('first_name')
		if request.POST.get('last_name'):
			user.last_name = request.POST.get('last_name')
		if request.POST.get('city',''):
			extendeduser.city=request.POST.get('city','')
		extendeduser.state=request.POST.get('state','')
		extendeduser.country=request.POST.get('country','')
		extendeduser.profession=request.POST.get('profession','')
		extendeduser.gender=request.POST.get('gender','')
		if request.POST.get('bio',''):
			extendeduser.bio=request.POST.get('bio','')
		bday_day = int(request.POST.getlist('birthDay_day')[0])
		bday_month = int(request.POST.getlist('birthDay_month')[0])
		bday_year = int(request.POST.getlist('birthDay_year')[0])
		# print(bday_year,bday_month,bday_day)
		bday = date(bday_year,bday_month,bday_day)
		extendeduser.birthDay=bday #request.POST.get('birthDay','')
		if request.FILES.get('image',''):
			if extendeduser.imageUrl:
				if os.path.isfile(extendeduser.imageUrl.path):
					os.remove(extendeduser.imageUrl.path)
			extendeduser.imageUrl=request.FILES.get('image','')
		if request.POST.getlist('categories',''):
			categories=request.POST.getlist('categories','')
			categories_list = Category.objects.values_list('id', flat=True).filter(category_title__in=categories)
			user_categories = ",".join(str(x) for x in categories_list)
			extendeduser.categories=user_categories
		user.save()
		extendeduser.save()
		if request.is_ajax():
			data={}
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state:
				data['form_errors'] = "Profile Incomplete"
				return HttpResponse(json.dumps(data),
                            content_type='application/json')
			else:
				return HttpResponse(json.dumps(data),content_type='application/json')
		return HttpResponseRedirect(url)

class RedirectLoginView(generic.ListView):

	def get(self,request,*args,**kwargs):
		user_slug = None
		user = request.user
		# print("redirect view",request.user,user.socialaccount_set.all())
		if hasattr(request.user,'extendeduser'):
			user_slug = request.user.extendeduser.user_slug
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
				user_slug = request.user.extendeduser.user_slug
		url = reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':user_slug})
		return HttpResponseRedirect(url)

class LoggedInView(generic.DetailView):
	template_name = 'login/profile.html'
	model = User
	#model = settings.AUTH_USER_MODEL
	# context_object_name = 'data'
	# print(request.path)
	# template_name=request.path
	def get_context_data(self, **kwargs):
		context = super(LoggedInView, self).get_context_data(**kwargs)
		user = self.request.user
		form = ChangePasswordForm(UserForm(user))
		user_asked_questions = Question.objects.filter(user_id = user.id).order_by('-pub_date')[:20]
		user_voted_questions = Question.objects.filter(pk__in=Voted.objects.values_list('question_id').filter(user_id = user.id))[:20]
		user_subscribed_questions = Subscriber.objects.filter(user_id=user.id).count()
		user_categories = []
		cat_list = []
		if hasattr(user,'extendeduser'):
			if user.extendeduser.categories:
				user_categories_list = list(map(int,user.extendeduser.categories.split(',')))
				user_categories = Category.objects.all().filter(pk__in=user_categories_list)
				for cat in user.extendeduser.categories.split(","):
					cat_list.append(Category.objects.get(pk=cat).category_title)
		mainData = {}
		context['form'] = form
		context['questions'] = user_asked_questions
		context['voted'] = user_voted_questions
		context['subscribed'] = user_subscribed_questions
		context['categories'] = user_categories
		# if not user.is_anonymous():	
		userFormData = {"first_name":user.first_name,"last_name":user.last_name,"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"bio":user.extendeduser.bio,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city,'categories':cat_list}
		loggedInForm = MySignupForm(userFormData)
		context["loggedInForm"] = loggedInForm
		return context
		
# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

# def change_password_view(request):
# 	return password_change(request,post_change_redirect="/")

class MyChangePasswordView(PasswordChangeView):

	def post(self,request,*args,**kwargs):
		form_class = super(MyChangePasswordView, self).get_form_class()
		form = self.get_form(form_class)
		data={}
		# print(form.save())
		if form.is_valid():
			super(MyChangePasswordView, self).form_valid(form)
		else:
			# response = self.form_invalid(form)
			# response.template_name = "login/profile.html"
			data['form_errors'] = form._errors
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		if request.is_ajax():
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		url = reverse('account_login')
		return HttpResponseRedirect(url)
		# return get_adapter().ajax_response(request, response, form=form, redirect_to=reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug}))
