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
from polls.models import Question
import json
from login.forms import MySignupForm
from django.contrib.auth.models import User

class EditProfileView(generic.ListView):
	
	def post(self, request, *args, **kwargs):
		url = reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug})
		user = request.user
		extendeduser = user.extendeduser
		print(request.POST)
		# print(request.POST.get('name'))
		user.first_name = request.POST.get('first_name')
		user.last_name = request.POST.get('last_name')
		extendeduser.city=request.POST.get('city','')
		extendeduser.birthDay=request.POST.get('birthDay','')
		extendeduser.state=request.POST.get('state','')
		extendeduser.country=request.POST.get('country','')
		extendeduser.profession=request.POST.get('profession','')
		extendeduser.gender=request.POST.get('gender','')
		extendeduser.bio=request.POST.get('bio','')
		if request.FILES.get('image',''):
			extendeduser.imageUrl=request.FILES.get('image','')
		user.save()
		extendeduser.save()
		return HttpResponseRedirect(url)

class RedirectLoginView(generic.ListView):

	def get(self,request,*args,**kwargs):
		url = reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug})
		return HttpResponseRedirect(url)

class LoggedInView(generic.DetailView):
	template_name = 'login/profile.html'
	model = User
	print(model)
	# context_object_name = 'data'
	# print(request.path)
	# template_name=request.path
	def get_context_data(self, **kwargs):
		context = super(LoggedInView, self).get_context_data(**kwargs)
		user = self.request.user
		form = ChangePasswordForm(UserForm(user))
		user_asked_questions = Question.objects.filter(user_id = user.id).order_by('-pub_date')[:10]
		mainData = {}
		context['form'] = form
		context['questions'] = user_asked_questions
		if not user.is_anonymous():
			if user.socialaccount_set.all():
				social_set = user.socialaccount_set.all()[0]
				print((social_set.extra_data))
				if not (ExtendedUser.objects.filter(user_id = user.id)):
					if social_set.provider == 'facebook':
						facebook_data = social_set.extra_data
						img_url =  "http://graph.facebook.com/{}/picture?width=140&&height=140".format(facebook_data.get('id',''))
						gender_data = facebook_data.get('gender','')[0].upper()
						birth_day = facebook_data.get('birthday','2002-01-01')
						extendedUser = ExtendedUser(user=user, imageUrl = img_url, birthDay = birth_day,gender=gender_data)
						extendedUser.save()
					if social_set.provider == 'google':
						google_data = social_set.extra_data
						img_url = google_data.get('picture')
						gender_data = google_data.get('gender','')[0].upper()
						extendedUser = ExtendedUser(user=user, imageUrl = img_url, gender=gender_data)
						extendedUser.save()
					if social_set.provider == 'twitter':
						twitter_data = social_set.extra_data
						img_url = twitter_data.get('profile_image_url')
						city_data = twitter_data.get('location','')
						extendedUser = ExtendedUser(user=user, imageUrl = img_url, city=city_data)
						extendedUser.save()
		userFormData = {"first_name":user.first_name,"last_name":user.last_name,"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"bio":user.extendeduser.bio,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city}
		context["loggedInForm"] = MySignupForm(userFormData)
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
		# print(form.save())
		if form.is_valid():
			super(MyChangePasswordView, self).form_valid(form)
		else:
			# response = self.form_invalid(form)
			# response.template_name = "login/profile.html"
			data={}
			data['form_errors'] = form._errors
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		url = reverse('account_login')
		return HttpResponseRedirect(url)
		# return get_adapter().ajax_response(request, response, form=form, redirect_to=reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug}))
