from django.shortcuts import render
from django.views import generic
from django.conf import settings
from login.models import ExtendedUser

class LoggedInView(generic.ListView):
	template_name = 'login/profile.html'
	model = settings.AUTH_USER_MODEL
	# context_object_name = 'data'
	# print(request.path)
	# template_name=request.path
	def get_queryset(self):
		user = self.request.user
		#print(user)
		#print(dir(user))
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
		
# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'
