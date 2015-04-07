from django.db import models
from django.conf import settings
#from django.contrib.auth.models import User
# Create your models here.

class ExtendedUser(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	imageUrl = models.CharField(max_length=512,blank=True,null=True)
	birthDay = models.DateField(default="2002-01-01")
	gender = models.CharField(max_length=1,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	bio = models.CharField(max_length=1024,blank=True,null=True)
	profession = models.CharField(max_length=512,blank=True,null=True)