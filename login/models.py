from django.db import models
from django.conf import settings
import os
import uuid
from django.template.defaultfilters import slugify
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