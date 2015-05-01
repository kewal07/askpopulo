from django.shortcuts import render
from django.views import generic
from django.conf import settings
from login.models import ExtendedUser
import allauth
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import resolve,reverse

# from allauth.account.signals import user_signed_up
# from django.dispatch import receiver

# @receiver(user_signed_up, dispatch_uid="some.unique.string.id.for.allauth.user_signed_up")
# def user_signed_up_(request, user, **kwargs):
    # # user signed up now send email
    # # send email part - do your self
	
class EditProfileView(generic.ListView):
	
	def post(self, request, *args, **kwargs):
		url = reverse('login:loggedIn')
		user = request.user
		extendeduser = user.extendeduser
		print(request.POST)
		print(request.POST.get('name'))
		user.first_name = request.POST.get('name').split()[0]
		user.last_name = request.POST.get('name').split()[1]
		extendeduser.city=request.POST.get('city','')
		extendeduser.birthDay=request.POST.get('dob','')
		extendeduser.state=request.POST.get('state','')
		extendeduser.country=request.POST.get('country','')
		extendeduser.profession=request.POST.get('prof','')
		extendeduser.gender=request.POST.get('gender','')
		extendeduser.bio=request.POST.get('bio','')
		user.save()
		extendeduser.save()
		return HttpResponseRedirect(url)

class LoggedInView(generic.ListView):
	template_name = 'login/profile.html'
	model = settings.AUTH_USER_MODEL
	# context_object_name = 'data'
	# print(request.path)
	# template_name=request.path
	def get_queryset(self):
		user = self.request.user
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
		print(dir(user.extendeduser.imageUrl))
		print(user.extendeduser.imageUrl)
		
# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'
