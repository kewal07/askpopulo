import os,linecache
from django.shortcuts import render
from django.views import generic
from django.conf import settings
from login.models import ExtendedUser, Follow, RedemptionScheme, RedemptionCouponsSent, ExtendedGroup, ExtendedGroupFuture
import allauth
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import resolve,reverse
from django.contrib.auth.views import logout
from allauth.account.forms import ChangePasswordForm,UserForm
from allauth.account.views import PasswordChangeView
from django.template.defaultfilters import slugify
from allauth.account.adapter import get_adapter
from polls.models import Question,Voted,Subscriber,Survey,SurveyVoted,Survey_Question,VoteApi,VoteText, Vote, Choice, Demographics
from categories.models import Category
import json
import base64
import hmac
import time
import hashlib
from login.forms import MySignupForm,FollowForm
from django.contrib.auth.models import User
from datetime import date
import datetime
from stream_django.feed_manager import feed_manager
from stream_django.enrich import Enrich
from django.contrib.auth.decorators import login_required
# from firebase_token_generator import create_token
import os
import sys
from django.core.mail import send_mail
from rolepermissions.verifications import has_permission
from askpopulo.roles import PageAdmin
from postman.models import Message
from referral.models import UserReferrer
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.contrib.sessions.models import Session
from django.utils import timezone
import polls
import ast

class BaseViewList(generic.ListView):
	def get_context_data(self, **kwargs):
		context = super(BaseViewList, self).get_context_data(**kwargs)
		context["STREAM_API_KEY"] = settings.STREAM_API_KEY
		context['STREAM_APP_ID'] = settings.STREAM_APP_ID
		context['STREAM_API_SECRET'] = settings.STREAM_API_SECRET
		context['DISQUS_API_KEY'] = settings.DISQUS_API_KEY
		context['DISQUS_WEBSITE_SHORTNAME'] = settings.DISQUS_WEBSITE_SHORTNAME
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		print(str(self.request.session.get('referrer')))
		if self.request.user.is_authenticated():
			if not UserReferrer.objects.filter(user_id=self.request.user.id) and self.request.session.get('referrer'): 
				UserReferrer.objects.apply_referrer(self.request.user, self.request)
			enricher = Enrich()
			messageCount = Message.objects.filter(recipient_id = self.request.user.id, read_at__isnull=True).count()
			context['messageCount'] = messageCount
			feed = feed_manager.get_notification_feed(self.request.user.id)
			readonly_token = feed.get_readonly_token()
			context['readonly_token'] = readonly_token
			activities = []
			notification_count = 0
			notify = []
			try:
				activities = feed.get(limit=25)['results']
				# notifications = enricher.enrich_activities(activities)
				notifications = activities
				for notification in notifications:
					if not notification['is_seen']:
						notification_count += 1
						activity = notification['activities'][0]
						if notification['activity_count'] - 1 > 0:
							activity['activity_count'] = notification['activity_count'] - 1
						notify.append(activity)
			except:
				pass
			context['notification_count'] = notification_count
			context['notifications'] = notify
			user_referral_code = polls.views.get_user_referral_id(user_id=self.request.user.id)
			context['referral_code'] = user_referral_code
		return context

class BaseViewDetail(generic.DetailView):
	def get_context_data(self, **kwargs):
		context = super(BaseViewDetail, self).get_context_data(**kwargs)
		context["STREAM_API_KEY"] = settings.STREAM_API_KEY
		context['STREAM_APP_ID'] = settings.STREAM_APP_ID
		context['STREAM_API_SECRET'] = settings.STREAM_API_SECRET
		context['DISQUS_API_KEY'] = settings.DISQUS_API_KEY
		context['DISQUS_WEBSITE_SHORTNAME'] = settings.DISQUS_WEBSITE_SHORTNAME
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		if self.request.user.is_authenticated():
			if not UserReferrer.objects.filter(user_id=self.request.user.id) and self.request.session.get('referrer'): 
				UserReferrer.objects.apply_referrer(self.request.user, self.request)
			enricher = Enrich()
			messageCount = Message.objects.filter(recipient_id = self.request.user.id, read_at__isnull=True).count()
			context['messageCount'] = messageCount
			feed = feed_manager.get_notification_feed(self.request.user.id)
			readonly_token = feed.get_readonly_token()
			context['readonly_token'] = readonly_token
			notification_count = 0
			notify = []
			try:
				activities = feed.get(limit=25)['results']
				# notifications = enricher.enrich_activities(activities)
				notifications = activities
				for notification in notifications:
					if not notification['is_seen']:
						notification_count += 1
						activity = notification['activities'][0]
						if notification['activity_count'] - 1 > 0:
							activity['activity_count'] = notification['activity_count'] - 1
						notify.append(activity)
			except:
				pass
			context['notification_count'] = notification_count
			context['notifications'] = notify
			user_referral_code = polls.views.get_user_referral_id(user_id=self.request.user.id)
			context['referral_code'] = user_referral_code
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
			print(request.GET)
			if not user.extendeduser.gender or not user.extendeduser.birthDay or not user.extendeduser.profession or not user.extendeduser.country or not user.extendeduser.state or not user.extendeduser.city:
				data['form_errors'] = "Profile Incomplete"
				return HttpResponse(json.dumps(data),
                            content_type='application/json')
			else:
				question = request.GET.get("question")
				choice = request.GET.get("choice")
				if question and choice:
					polls.views.save_poll_vote(user,question,choice,queBet=None)
				return HttpResponse(json.dumps(data),content_type='application/json')
		return HttpResponseRedirect(url)

class RedirectLoginView(generic.ListView):

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
				if not UserReferrer.objects.filter(user_id=request.user.id) and  request.session.get('referrer'):
					UserReferrer.objects.apply_referrer(request.user, request)
				user_slug = request.user.extendeduser.user_slug
				url = reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':user_slug})
		else:
			url = reverse('polls:index', kwargs={})
		return HttpResponseRedirect(url)
	def get_context_data(self,**kwargs):
		return {}

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
		if public_profile:
			user_asked_questions = Question.objects.filter(user_id = user.id,privatePoll=0,isAnonymous=0).order_by('-pub_date')
		else:
			user_asked_questions = Question.objects.filter(user_id = user.id).order_by('-pub_date')
		survey_list = Survey.objects.filter(user_id=user.id)
		s_polls = []
		for survey in survey_list:
			s_polls.extend([ x.question for x in Survey_Question.objects.filter(survey_id=survey.id)])
		user_asked_questions = [item for item in user_asked_questions if item not in s_polls][:20]
		user_voted_questions = Question.objects.filter(pk__in=Voted.objects.values_list('question_id').filter(user_id = user.id))
		user_voted_questions = [item for item in user_voted_questions if item not in s_polls][:20]
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
			notification_activities.extend(act['activities'])
		context['notification_activities'] = notification_activities
		ssoData = {}
		#if public_profile:
		profilepicUrl = user.extendeduser.get_profile_pic_url()
		if not profilepicUrl.startswith('http'):
			profilepicUrl = r"https://askbypoll.com"+profilepicUrl
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
		context['questions'] = user_asked_questions
		context['voted'] = user_voted_questions
		context['questions_count'] = len(user_asked_questions)
		context['voted_count'] = len(user_voted_questions)
		context['subscribed'] = user_subscribed_questions
		context['categories'] = user_categories
		context['followed'] = Follow.objects.filter(user=request_user, target_id=user, deleted_at__isnull=True)
		enricher = Enrich(fields=['actor', 'object', 'question_text', 'question_url', 'question_desc','following_user_img', 'followed_username', 'followed_user_img', 'actor_user_name', 'actor_user_url', 'actor_user_pic', 'target_user_name', 'target_user_pic', 'target_user_url'])
		feed = feed_manager.get_user_feed(user.id)
		activities = feed.get(limit=25)['results']
		context["activities"] = activities
		flat_feed = feed_manager.get_news_feeds(user.id)['flat'] 
		feed_activities = flat_feed.get(limit=25)['results']
		context['flat_feed_activities'] = feed_activities
		auth_payload = {"uid": str(request_user.id), "auth_data": "foo", "other_auth_data": "bar"}
		# token = create_token("tX5LUw3MVHkDpZzvlHexdpVlCuHt3Hzyl2rmTqTS", auth_payload)
		# context['token'] = token
		followers = [ x.user for x in Follow.objects.filter(target_id=user.id,deleted_at__isnull=True) ]
		following = [ x.target for x in Follow.objects.filter(user_id=user.id,deleted_at__isnull=True) ]
		context["followers"] = followers
		context["following"] = following
		connections = []
		connections.extend(followers)
		connections.extend(following)
		context["connection_count"] = len(set(connections))
		context["credits"] = user.extendeduser.credits
		return context
		
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
		output = {}
		data_form = {}
		data_form['target'] = request.POST.get('target')
		data_form['next'] = request.POST.get('next')
		data_form['company'] = request.POST.get('company',0)
		data_form['remove'] = request.POST.get('remove')
		follow_company = False
		if int(data_form.get("company",0)) == 1:
			# data_form.remove("company")
			follow_company = True
		data_list = []
		data_list.append(data_form)
		print(data_list)
		if follow_company:
			company_id = int(request.POST.get("target"))
			user_id_list = [x.user_id for x in ExtendedUser.objects.filter(company_id=company_id)]
			data_list = []
			for userid in user_id_list:
				data_form['target'] = userid
				data_list.append(data_form)
		if request.method == "POST":
			for data in data_list:
				form = FollowForm(user=request.user, data=data)

				if form.is_valid():
					follow = form.save()
				if follow:
					output['follow'] = dict(id=follow.id)
				else:
					output['errors'] = dict(form.errors.items())
			if not request.is_ajax():
				return HttpResponseRedirect(request.POST.get("next"))
			return HttpResponse(json.dumps(output), content_type='application/json')

class MarkFeedSeen(BaseViewDetail):
	def get(self,request,*args,**kwargs):
		enricher = Enrich()
		feed = feed_manager.get_notification_feed(request.user.id)
		activities = feed.get(limit=25, mark_seen='all')['results']
		return HttpResponse(json.dumps({}), content_type='application/json')

class RedeemView(BaseViewList):
	model = RedemptionScheme
	template_name = 'redeem.html'
	context_object_name = 'redemptionData'
	def get_context_data(self, **kwargs):
		context = super(RedeemView, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		context['schemes'] = RedemptionScheme.objects.all()
		return context
	def post(self,request,*args,**kwargs):
		try:
			request_user = self.request.user
			orderList = "Request from " + request_user.first_name + " " + request_user.last_name + "( " +request_user.username + " )\n"
			availablepCoins = int(self.request.user.extendeduser.credits)
			availableSchemes = RedemptionScheme.objects.all()
			couponRequest = []
			response = {}
			print(request.POST)
			totalOrder = 0
			for scheme in availableSchemes:
				orderQty = 0
				if request.POST.get(scheme.schemeName):
						orderQty = int(request.POST.get(scheme.schemeName))
				if(orderQty > 0):
					newCouponRequest = RedemptionCouponsSent(schemeName=scheme.schemeName,quantity=orderQty,to=self.request.user.email,sent=0)
					couponRequest.append(newCouponRequest)
					# create order list to send mail here
					orderList += newCouponRequest.schemeName + " ::: " + str(newCouponRequest.quantity) + "\n"
					availablepCoins -= int(orderQty * scheme.schemeCostInPCoins)
					totalOrder += int(orderQty * scheme.schemeCostInPCoins)

			if(totalOrder > 0):
				if(availablepCoins < 100):
					response['insufficientpCoins'] = 'You have insuficient pCoins. Remove some selections and try again'
					return HttpResponse(json.dumps(response), content_type='application/json')
				else:
					response['validationPassed'] = 'All Coupons are valid'
					response['remainingCredits'] = availablepCoins
					response['successMessage'] = 'You will receive coupons in your mail box within 2 working days.'
					currentUser = ExtendedUser.objects.filter(pk = request.user.extendeduser.id)[0]
					currentUser.credits = availablepCoins
					currentUser.save()
					for req in couponRequest:
						req.save();
					# send Mail Here
					send_mail('RedemptionOrder',orderList,'support@askbypoll.com',['support@askbypoll.com','sandeep.singh.2328@gmail.com','kewal07@gmail.com'])
					return HttpResponse(json.dumps(response), content_type='application/json')
			elif totalOrder <= 0:
				response['insufficientpCoins'] = 'No schemes were selected'
				return HttpResponse(json.dumps(response), content_type='application/json')
			return HttpResponse(json.dumps(response), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

class AdminDashboard(BaseViewDetail):
	model = User

	def get_template_names(self, **kwargs):
		template_name = 'login/company_admin.html'
		# if self.request.is_ajax():
		# 	template_name = ''
		return [template_name]
	
	def get(self, request, *args, **kwargs):
		try:
			self.object = self.get_object()
			data = super(AdminDashboard, self).get_context_data(object=self.object)
			choice_id_text_data = {}
			user = self.request.user
			if self.object != user:
				user_slug = user.extendeduser.user_slug
				url = reverse('login:loggedIn', kwargs={'pk':user.id,'user_slug':user_slug})
				return HttpResponseRedirect(url)
			# Why are we taking everything here itself. Better to query on specific clicks
			polls_vote_list = []
			survey_list = Survey.objects.filter(user_id=user.id).order_by('-pub_date')
			polls = Question.objects.filter(user_id = user.id, is_survey = 0, is_feedback = 0).order_by('-pub_date')
			# s_polls = []
			# s_polls = Question.objects.filter(user_id = user.id, is_survey = 1).order_by('-pub_date')
			# for survey in survey_list:
			# 	s_polls.extend([ x.question for x in Survey_Question.objects.filter(survey_id=survey.id)])
			# polls = [item for item in polls if item not in s_polls]
			total_views = 0
			dash_graph = []
			cur_time = datetime.datetime.now()
			month_names = ['Jan','Feb','March','Apr','May','June','July','Aug','Sep','Oct','Nov','Dec']
			for i in range(3):
				month_num = (cur_time.month - i)
				year_considered = cur_time.year
				if month_num < 1:
					month_num += 12
					year_considered -= 1
				month_name = month_names[month_num-1]
				# print(cur_time.month,month_num,cur_time.year,month_name,year_considered)
				# dash_polls = Question.objects.filter(user_id = user.id,pub_date__month=month_num)
				dash_polls = [ x for x in polls if x.pub_date.month == month_num and x.pub_date.year == year_considered]
				# print(dash_polls)
				dash_polls_count = len(dash_polls)
				dash_views = 0
				dash_votes = 0
				for poll in dash_polls:
					dash_views += poll.numViews
					dash_votes += Voted.objects.filter(question_id=poll.id).count()
					dash_votes += VoteApi.objects.filter(question=poll).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True).count()
				dash_dict = {}
				dash_dict['month_name'] = month_name
				dash_dict['polls'] = dash_polls_count
				dash_dict['views'] = dash_views
				dash_dict['votes'] = dash_votes
				dash_graph.append(dash_dict)
			# print(dash_graph)
			data['dash_graph'] = dash_graph
			for que in polls:
				pole_dict = {}
				pole_dict['poll'] = que
				voted_list = Voted.objects.filter(question_id=que.id)
				pole_dict['votes'] = len(voted_list)
				email_already_considered = [x.user.email for x in voted_list]
				pole_dict['allvotes'] = pole_dict['votes'] + VoteApi.objects.filter(question=que).exclude(email__in=email_already_considered).count()
				pole_dict['votes'] += VoteApi.objects.filter(question=que).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).exclude(email__in=email_already_considered).count()
				#pole_dict['votes'] += VoteApi.objects.filter(question=que).exclude(age__isnull=True,gender__isnull=True,profession__isnull=True,email__in=email_already_considered).count()
				total_views += que.numViews
				polls_vote_list.append(pole_dict)
				for index,choice in enumerate(Choice.objects.filter(question_id=que.id)):
					key = str(que.id) + "---" + str(choice.id)
					val = "Choice "+str(index+1)
					if choice.choice_text:
						val = choice.choice_text
					choice_id_text_data[key] = val
			groups = ExtendedGroup.objects.filter(user_id = user.id).values('group_id')
			group_list = []
			for group in groups:
				groupNamePrefixLength = len(user.username+'_'+user.extendeduser.company.name+'-')
				group_dict = {}
				tempGroup = Group.objects.get(pk=group['group_id'])
				group_dict['groupId'] = tempGroup.id
				group_dict['groupName'] = tempGroup.name[groupNamePrefixLength:]
				groupMembers = tempGroup.user_set.all()
				group_dict['groupMembers'] = []
				group_dict['groupMembersIncomplete'] = []
				for x in groupMembers:
					if hasattr(x,'extendeduser'):
						group_dict['groupMembers'].append(x)
					else:
						group_dict['groupMembersIncomplete'].append(x)
				group_dict['groupMembersFuture'] = [x.user_email.replace("@"," at ") for x in ExtendedGroupFuture.objects.filter(group=tempGroup)]
				group_list.append(group_dict)
			polls_count = len(polls)
			groups_count = len(groups)
			survey_count = len(survey_list)
			survey_detail_list = []
			for survey in survey_list:
				sur_dict={}
				totalVoted = 0
				sur_dict['survey'] = survey
				surveyVoted = SurveyVoted.objects.filter(survey_id=survey.id)
				totalParticipants = len(surveyVoted)
				sur_dict['votes'] = totalParticipants
				total_views += survey.numViews
				survey_questions = Survey_Question.objects.filter(survey_id=survey.id)
				incompleteResponses = 0				
				for voted in surveyVoted:
					if voted.survey_question_count != voted.user_answer_count:
						incompleteResponses += 1
				completeRate = 0
				if totalParticipants > 0:
					completeRate = int(((totalParticipants-incompleteResponses)/totalParticipants)*100)
				sur_dict["incompleteResponses"] = completeRate

				extra_demographics = Demographics.objects.filter(survey_id=survey.id)
				demo_list = []
				if extra_demographics:
					extra_demographics = ast.literal_eval(extra_demographics[0].demographic_data)
					for key,val in extra_demographics.items():
						demo = {}
						demo["name"] = key
						demo["values"] = val
						demo_list.append(demo)
				sur_dict["demo_list"] = demo_list				

				sur_dict['polls'] = []
				for x in survey_questions:
					# maxVotes = -1
					# minVotes = 99999
					maxVotedChoiceList = []
					minVotedChoiceList = []
					choice_dict = {}
					maxVotedCount = -1
					minVotedCount = 99999
					questionChoices = x.question.choice_set.all()
					totalResponses = x.question.voted_set.count()
					comment_choice_data = {}
					choice_data = {}
					comments = []
					for index,choice in enumerate(questionChoices):
						vote_set = choice.vote_set
						numVotes = vote_set.count()
						# print(numVotes,choice_dict,choice.choice_text + " : " + str(numVotes))
						if not choice_dict.get(numVotes):
							choice_dict[numVotes] = []
						choice_dict[numVotes].append("Choice " + str(index+1)) # + " : " + str(numVotes))
						if(numVotes >= maxVotedCount):
							maxVotedCount = numVotes
						if(numVotes <= minVotedCount):
							minVotedCount = numVotes
						choice_data[choice.id] = "Choice " + str(index+1)
						key = str(x.question.id) + "---" + str(choice.id)
						val = "Choice "+str(index+1)
						if choice.choice_text:
							val = choice.choice_text
						choice_id_text_data[key] = val
					for voteText in VoteText.objects.filter(question_id=x.question.id):
						comment_text = ""
						votes = Vote.objects.filter(user_id=voteText.user.id,choice__in=questionChoices)
						for vote in votes:
							comment_text += choice_data.get(vote.choice.id) + ","
						if comment_text:
							comment_text = comment_text[:-1] + " :"
						comment_text += voteText.answer_text
						comments.append(comment_text)

					sur_dict['polls'].append({"question":x.question,"q_type":x.question_type,"totalResponses":totalResponses,"maxVotes":choice_dict.get(maxVotedCount,""),"minVotes":choice_dict.get(minVotedCount,""), "comments":comments})
				survey_detail_list.append(sur_dict)
				# sur_dict['polls'] = [ {"question":x.question,"q_type":x.question_type} for x in Survey_Question.objects.filter(survey_id=survey.id)]
				# survey_detail_list.append(sur_dict)
			votes_count = Voted.objects.filter(question_id__in=Question.objects.values_list('id').filter(user_id = user.id)).count()
			followers = [ x.user for x in Follow.objects.filter(target_id=user.id,deleted_at__isnull=True) ]
			following = [ x.target for x in Follow.objects.filter(user_id=user.id,deleted_at__isnull=True) ]
			activeUsers = getAllLoggedInUsers()
			credits = user.extendeduser.credits
			activities = []
			feed_activities = []
			try:
				feed = feed_manager.get_user_feed(user.id)
				activities = feed.get(limit=25)['results']
				flat_feed = feed_manager.get_news_feeds(user.id)['flat'] 
				feed_activities = flat_feed.get(limit=25)['results']
			except Exception as e:
				exc_type, exc_obj, tb = sys.exc_info()
				f = tb.tb_frame
				lineno = tb.tb_lineno
				filename = f.f_code.co_filename
				linecache.checkcache(filename)
				line = linecache.getline(filename, lineno, f.f_globals)
				print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			data["activities"] = activities
			data['flat_feed_activities'] = feed_activities
			data["followers"] = followers
			data["following"] = following
			data["activeUsers"] = 11 
			followers_count = len(followers)
			following_count = len(following)
			data['followers_count'] = followers_count
			data['following_count'] = following_count
			data['credits'] = credits
			data['polls'] = polls_vote_list
			data['polls_count'] = polls_count
			data['groups'] = group_list
			data['groups_count'] = groups_count
			data['surveys'] = survey_detail_list
			data['surveys_count'] = survey_count
			data['votes_count'] = votes_count
			data['total_views'] = total_views
			data['categories'] = Category.objects.all()
			data['choice_id_text_data'] = choice_id_text_data
			data["feedback_polls"] = Question.objects.filter(user_id=4,is_feedback=1)
			data["demographics_captured"] = ["Age","Gender","Location","Profession"]
			# print(data)
			# return data
			return self.render_to_response(data)
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

class CreateGroup(BaseViewList):
	def post(self, request, *args, **kwargs):
		emailList = request.POST.get('groupMembers').split(';')
		isEdit = request.POST.get('isGroupEdit')
		groupName = request.user.username+'_'+request.user.extendeduser.company.name+'-'+request.POST.get("groupName")
		print(isEdit)
		print(groupName)
		response = {}
		try:
			group, created = Group.objects.get_or_create(name = groupName)
			if isEdit == 'no' and not created:
				response['error'] = 'Group name already exists.'
				return HttpResponse(json.dumps(response), content_type='application/json')
			extendedGroup, created = ExtendedGroup.objects.get_or_create(user=request.user, group = group)
			group_user_set = group.user_set.all()
			already_added_users = [x.email for x in group_user_set]
			for email in emailList:
				if email:
					user = User.objects.filter(email = email)
					if user:
						if email not in already_added_users:
							user = list(user)[0]
							user.groups.add(group)
						else:
							already_added_users.remove(email)
					else:
						extendedGroupFuture,created = ExtendedGroupFuture.objects.get_or_create(user_email=email,group=group)
						# extendedGroupFuture.save()
						msg = EmailMessage(subject="Invitation", from_email="support@askbypoll.com",to=[email])
						msg.template_name = "invitation-mail"
						msg.global_merge_vars = {
						'inviter': request.user.first_name,
						'companyname':request.user.extendeduser.company.name
						}
						msg.send()
			for email in already_added_users:
				user = User.objects.filter(email = email)[0]
				group.user_set.remove(user)
			if(isEdit == 'yes'):
					response['success'] = 'Group edited successfully.'
			else:
				response['success'] = 'Group created successfully.'
			return HttpResponse(json.dumps(response), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class EditGroup(BaseViewList):
	def get(self, request, *args, **kwargs):
		groupId = request.GET.get('groupId','')
		response = {}
		try:
			if(groupId or not groupId==''):
				group = Group.objects.get(pk = groupId)
				groupNamePrefixLength = len(request.user.username+'_'+request.user.extendeduser.company.name+'-')
				response['groupName'] = group.name[groupNamePrefixLength:]
				response['mailList'] = ''
				for user in group.user_set.all():
					response['mailList'] += user.email +';'
				return HttpResponse(json.dumps(response), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

class DeleteGroup(BaseViewList):
	def get(self, request, *args, **kwargs):
		groupId = request.GET.get('groupId','')
		response = {}
		try:
			if(groupId or not groupId==''):
				group = Group.objects.get(pk = groupId)
				group.delete()
				response['success'] = "Group deleted successfully."
				return HttpResponse(json.dumps(response), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

def getAllLoggedInUsers():
	# Query all non-expired sessions
	# use timezone.now() instead of datetime.now() in latest versions of Django
	sessions = Session.objects.filter(expire_date__gte=timezone.now())
	uid_list = []

	for session in sessions:
		data = session.get_decoded()
		uid_list.append(data.get('_auth_user_id', None))
	return len(User.objects.filter(id__in=uid_list));