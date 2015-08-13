import os
from django.shortcuts import render
from django.views import generic
from django.conf import settings
from login.models import ExtendedUser,Follow
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
import base64
import hmac
import time
import hashlib
from login.forms import MySignupForm,FollowForm
from django.contrib.auth.models import User
from datetime import date
from stream_django.feed_manager import feed_manager
from stream_django.enrich import Enrich
from django.contrib.auth.decorators import login_required
from firebase_token_generator import create_token


class BaseViewList(generic.ListView):
	def get_context_data(self, **kwargs):
		context = super(BaseViewList, self).get_context_data(**kwargs)
		context["STREAM_API_KEY"] = settings.STREAM_API_KEY
		context['STREAM_APP_ID'] = settings.STREAM_APP_ID
		context['STREAM_API_SECRET'] = settings.STREAM_API_SECRET
		context['DISQUS_API_KEY'] = settings.DISQUS_API_KEY
		context['DISQUS_WEBSITE_SHORTNAME'] = settings.DISQUS_WEBSITE_SHORTNAME
		if self.request.user.is_authenticated():
			enricher = Enrich()
			feed = feed_manager.get_notification_feed(self.request.user.id)
			readonly_token = feed.get_readonly_token()
			context['readonly_token'] = readonly_token
			activities = feed.get(limit=25)['results']
			# notifications = enricher.enrich_activities(activities)
			notifications = activities
			notify = []
			notification_count = 0
			for notification in notifications:
				if not notification['is_seen']:
					notification_count += 1
					activity = notification['activities'][0]
					if notification['activity_count'] - 1 > 0:
						activity['activity_count'] = notification['activity_count'] - 1
					notify.append(activity)
			context['notification_count'] = notification_count
			context['notifications'] = notify
		return context

class BaseViewDetail(generic.DetailView):
	def get_context_data(self, **kwargs):
		context = super(BaseViewDetail, self).get_context_data(**kwargs)
		context["STREAM_API_KEY"] = settings.STREAM_API_KEY
		context['STREAM_APP_ID'] = settings.STREAM_APP_ID
		context['STREAM_API_SECRET'] = settings.STREAM_API_SECRET
		context['DISQUS_API_KEY'] = settings.DISQUS_API_KEY
		context['DISQUS_WEBSITE_SHORTNAME'] = settings.DISQUS_WEBSITE_SHORTNAME
		if self.request.user.is_authenticated():
			enricher = Enrich()
			feed = feed_manager.get_notification_feed(self.request.user.id)
			readonly_token = feed.get_readonly_token()
			context['readonly_token'] = readonly_token
			activities = feed.get(limit=25)['results']
			# notifications = enricher.enrich_activities(activities)
			notifications = activities
			notify = []
			notification_count = 0
			for notification in notifications:
				if not notification['is_seen']:
					notification_count += 1
					activity = notification['activities'][0]
					if notification['activity_count'] - 1 > 0:
						activity['activity_count'] = notification['activity_count'] - 1
					notify.append(activity)
			context['notification_count'] = notification_count
			context['notifications'] = notify
		return context

class EditProfileView(BaseViewList):
	
	def post(self, request, *args, **kwargs):
		url = reverse('login:editprofile', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug})
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

class RedirectLoginView(BaseViewList):

	def get(self,request,*args,**kwargs):
		user_slug = None
		user = request.user
		url = reverse('polls:index', kwargs={})
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
		else:
			url = reverse('polls:index', kwargs={})
		return HttpResponseRedirect(url)

class LoggedInView(BaseViewDetail):
	template_name = 'login/profile.html'
	model = User
	#model = settings.AUTH_USER_MODEL
	context_object_name = 'context_user'
	# print(request.path)
	# template_name=request.path

	def get_template_names(self, **kwargs):
		# request = self.request
		# user = self.request.user
		# context = super(LoggedInView, self).get_context_data(**kwargs)
		# context_user = context['context_user']
		# template_name = 'login/profile.html'
		# if user != context_user:
		template_name = 'login/public_profile.html'
		if self.request.path.endswith('editprofile'):
			template_name = 'login/profile.html'
		return [template_name]

	def get_context_data(self, **kwargs):
		context = super(LoggedInView, self).get_context_data(**kwargs)
		request_user = self.request.user
		user = context['context_user']
		public_profile = False
		if request_user != user:
			public_profile = True
		context['questions_count'] = Question.objects.filter(user_id = user.id).count()
		context['voted_count'] = Question.objects.filter(pk__in=Voted.objects.values_list('question_id').filter(user_id = user.id)).count()
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
		if not public_profile:
			form = ChangePasswordForm(UserForm(user))
			context['form'] = form
			userFormData = {"first_name":user.first_name,"last_name":user.last_name,"gender":user.extendeduser.gender,"birthDay":user.extendeduser.birthDay,"bio":user.extendeduser.bio,"profession":user.extendeduser.profession,"country":user.extendeduser.country,"state":user.extendeduser.state,"city":user.extendeduser.city,'categories':cat_list}
			loggedInForm = MySignupForm(userFormData)
			context["loggedInForm"] = loggedInForm
			feed = feed_manager.get_notification_feed(user.id)
			activities = feed.get(limit=25)['results']
			notification_activities = []
			for act in activities:
				# print("NOTTTTTTTTTTTTTTTTTT",act)
				notification_activities.extend(act['activities'])
			context['notification_activities'] = notification_activities
		ssoData = {}

		if public_profile:
			profilepicUrl = user.extendeduser.get_profile_pic_url()
			if not profilepicUrl.startswith('http'):
				profilepicUrl = r"http://askbypoll.com"+profilepicUrl
			data = {
				"id":user.id,
				"username":user.username,
				"email":user.email,
				"avatar":profilepicUrl
			}
		else:
			profilepicUrl = request_user.extendeduser.get_profile_pic_url()
			if not profilepicUrl.startswith('http'):
				profilepicUrl = r"http://askbypoll.com"+profilepicUrl
			data = {
				"id":request_user.id,
				"username":request_user.username,
				"email":request_user.email,
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
		context['questions'] = user_asked_questions
		context['voted'] = user_voted_questions
		context['subscribed'] = user_subscribed_questions
		context['categories'] = user_categories
		context['followed'] = Follow.objects.filter(user=request_user, target_id=user, deleted_at__isnull=True)
		enricher = Enrich(fields=['actor', 'object', 'question_text', 'question_url', 'question_desc','following_user_img', 'followed_username', 'followed_user_img', 'actor_user_name', 'actor_user_url', 'actor_user_pic', 'target_user_name', 'target_user_pic', 'target_user_url'])
		feed = feed_manager.get_user_feed(user.id)
		activities = feed.get(limit=25)['results']
		activities = enricher.enrich_activities(activities)
		context["activities"] = activities
		# print(dir(feed_manager))
		flat_feed = feed_manager.get_news_feeds(user.id)['flat'] 
		feed_activities = flat_feed.get(limit=25)['results']
		# print(feed_activities)
		# aggregated_feed = feed_manager.get_news_feeds(user.id)['aggregated'] 
		# feed_activities = aggregated_feed.get(limit=25)['results']
		# print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",feed_activities)
		context['flat_feed_activities'] = feed_activities
		# for act in activities:
		# 	print("____________________",act.activity_data)
		auth_payload = {"uid": str(request_user.id), "auth_data": "foo", "other_auth_data": "bar"}
		token = create_token("tX5LUw3MVHkDpZzvlHexdpVlCuHt3Hzyl2rmTqTS", auth_payload)
		context['token'] = token
		followers = [ x.user for x in Follow.objects.filter(target_id=user.id) ]
		following = [ x.target for x in Follow.objects.filter(user_id=user.id) ]
		context["followers"] = followers
		context["following"] = following
		connections = followers
		connections.extend(following)
		context["connection_count"] = len(set(connections))
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

class FollowView(BaseViewDetail):
	def post(self,request,*args,**kwargs):
	    '''
	    A view to follow other users
	    '''
	    print("**********")
	    print(request.POST)
	    print("**********")
	    output = {}
	    if request.method == "POST":
	        form = FollowForm(user=request.user, data=request.POST)

	        if form.is_valid():
	            follow = form.save()
	            if follow:
	                output['follow'] = dict(id=follow.id)
	            if not request.is_ajax():
	                return HttpResponseRedirect(request.POST.get("next"))
	        else:
	            output['errors'] = dict(form.errors.items())
	    return HttpResponse(json.dumps(output), content_type='application/json')

class MarkFeedSeen(BaseViewDetail):
	def get(self,request,*args,**kwargs):
		enricher = Enrich()
		feed = feed_manager.get_notification_feed(request.user.id)
		activities = feed.get(limit=25, mark_seen='all')['results']
		return HttpResponse(json.dumps({}), content_type='application/json')