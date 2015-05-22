from django.db import models
from django.conf import settings
import os
import uuid
from django.template.defaultfilters import slugify
from datetime import date
#from django.contrib.auth.models import User
# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "profilepic%s.%s" % (instance.user.id, ext)
	profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	return os.path.join(profilePath,filename)

class ExtendedUser(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	imageUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	birthDay = models.DateField(default="2002-01-01")
	gender = models.CharField(max_length=1,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	bio = models.CharField(max_length=1024,blank=True,null=True)
	profession = models.CharField(max_length=512,blank=True,null=True)
	user_slug = models.SlugField(null=True,blank=True)
	
	def save(self, *args, **kwargs):
		self.user_slug = slugify(self.user.username)
		super(ExtendedUser, self).save(*args, **kwargs)

	def get_profile_pic_name(self):
		return self.imageUrl.path.split("\\")[-1]

	def get_full_name(self):
		return self.user.first_name+ " "+self.user.last_name
		
	def get_profile_pic_url(self):
		default_pic_url = "http://localhost:8000/static/login/images/defaultAvatar.png"
		if self.user.socialaccount_set.all():
			if self.imageUrl:
				return self.imageUrl
		else:
			if self.imageUrl:
				return "http://localhost:8000/media/profile/"+self.get_profile_pic_name()
		return default_pic_url	

	def calculate_age(self):
		today = date.today()
		born = self.birthDay
		try: 
			birthday = born.replace(year=today.year)
		except ValueError: # raised when birth date is February 29 and the current year is not a leap year
			birthday = born.replace(year=today.year, month=born.month+1, day=1)
		if birthday > today:
			print(today.year - born.year - 1)
			return today.year - born.year - 1
		else:
			print(today.year - born.year)
			return today.year - born.year
			