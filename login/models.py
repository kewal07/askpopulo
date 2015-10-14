from django.db import models
from django.conf import settings
import os
import uuid
from django.template.defaultfilters import slugify
from datetime import date
from PIL import Image
import hmac
import hashlib
from stream_django.activity import Activity
# from stream_django.feed_manager import feed_manager
# from django.db.models.signals import post_delete, post_save
#from django.contrib.auth.models import User
# Create your models here.

def get_company_default():
	return Company.objects.get(id=1)
	
def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "profilepic%s.%s" % (instance.user_pk, ext)
	# profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'profile'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

def get_file_path_cover(instance, filename):
	ext = filename.split('.')[-1]
	filename = "company_cover_pic%s.%s" % (instance.id, ext)
	# profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'company'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

def get_file_path_background(instance, filename):
	ext = filename.split('.')[-1]
	filename = "company_background_pic%s.%s" % (instance.id, ext)
	# profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'company'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

def get_file_path_logo(instance, filename):
	ext = filename.split('.')[-1]
	filename = "company_logo_pic%s.%s" % (instance.id, ext)
	# profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'company'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

class BaseModel(models.Model):
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

class Follow(BaseModel):
    '''
    A simple table mapping who a user is following.
    For example, if user is Kyle and Kyle is following Alex,
    the target would be Alex.
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set')
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set')

class Company(BaseModel):
	name = models.CharField(max_length=255)
	description = models.CharField(max_length=255,null=True,blank=True)
	logo = models.ImageField(upload_to=get_file_path_logo,blank=True,null=True)
	cover_image = models.ImageField(upload_to=get_file_path_cover,blank=True,null=True)
	background_image = models.ImageField(upload_to=get_file_path_background,blank=True,null=True)
	company_slug = models.SlugField(null=True,blank=True)
	company_url = models.CharField(max_length=255,null=True,blank=True)
	company_facebook = models.CharField(max_length=255,null=True,blank=True)
	company_twitter = models.CharField(max_length=255,null=True,blank=True)

	def save(self, *args, **kwargs):
		cname = self.name
		cslug = slugify(cname)
		if not cslug and not cslug.strip():
			cslug = None
		self.company_slug = cslug
		super(Company, self).save(*args, **kwargs)

	def __str__(self):
		return self.name
		
	def get_profile_pic_name(self,imageUrl):
		return imageUrl.path.split(os.sep)[-1]

	def get_folder_day(self,imageUrl):
		folder_day = ""
		try:
			day = imageUrl.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day

	def get_pic_url(self,imageUrl):
		if imageUrl:
			return "/media/company/"+self.get_folder_day(imageUrl)+os.sep+self.get_profile_pic_name(imageUrl)
		
	def get_logo_url(self):
		default_pic_url = "/static/pollsLogo.png"
		if self.logo:
			default_pic_url = self.get_pic_url(self.logo)
		return default_pic_url

	def get_cover_url(self):
		default_pic_url = "/static/pollsLogo.png"
		if self.cover_image:
			default_pic_url = self.get_pic_url(self.cover_image)
		return default_pic_url

	def get_background_url(self):
		default_pic_url = "/static/polls/images/bg2.jpg"
		if self.background_image:
			default_pic_url = self.get_pic_url(self.background_image)
		return default_pic_url

class ExtendedUser(models.Model):
	tdate = date.today()
	def_bday = tdate.replace(year = tdate.year - 14)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	user_pk = models.CharField(max_length=255)
	imageUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	birthDay = models.DateField(default=def_bday)
	gender = models.CharField(max_length=1,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	bio = models.CharField(max_length=1024,blank=True,null=True)
	profession = models.CharField(max_length=512,blank=True,null=True)
	user_slug = models.SlugField(null=True,blank=True)
	categories = models.CharField(max_length=100,default='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26',blank=True,null=True)
	mailSubscriptionFlag = models.BooleanField(default=0)
	credits = models.IntegerField(default=100)
	company = models.OneToOneField(Company,default=get_company_default)
	
	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		uname = self.user.username
		# uname = ''.join(e for e in uname if e.isalnum())
		uslug = slugify(uname)
		if not uslug and not uslug.strip():
			uslug = None
		self.user_slug = uslug
		digestmod = hashlib.sha1
		msg = self.user.email.encode('utf-8')
		key = self.user.username.encode('utf-8')
		sig = hmac.HMAC(key, msg, digestmod).hexdigest()
		self.user_pk = sig
		super(ExtendedUser, self).save(*args, **kwargs)
		"""
		if self.imageUrl:
			size = 128, 128
			im = Image.open(self.imageUrl)
			im.thumbnail(size)
			im.save(self.imageUrl.path)
		"""

	def get_profile_pic_name(self):
		return self.imageUrl.path.split(os.sep)[-1]

	def get_full_name(self):
		return self.user.first_name+ " "+self.user.last_name

	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.imageUrl.path.split(os.sep)[-2]
			# print(day.split("-"))
			# print(day,int(day.split("-")[0]),int(day.split("-")[2]),int(day.split("-")[3]))
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day
		
	def get_profile_pic_url(self):
		default_pic_url = "/static/login/images/defaultAvatar.png"
		# if self.user.socialaccount_set.all():
		if self.imageUrl:
			img_url = self.imageUrl.path
			#print(img_url)
			# img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
			# print(img_url)
			if img_url.find("https:/") != -1:
				img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
				return r"https://"+self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/https:/","")
			elif img_url.find("http:/") != -1:
				img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
				return r"http://"+self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/http:/","")
			else:
				# print("/media/profile/"+self.get_profile_pic_name())
				return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		# else:
		# 	if self.imageUrl:
		# 		return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		return default_pic_url	

	def calculate_age(self):
		today = date.today()
		born = self.birthDay
		try: 
			birthday = born.replace(year=today.year)
		except ValueError: # raised when birth date is February 29 and the current year is not a leap year
			birthday = born.replace(year=today.year, month=born.month+1, day=1)
		if birthday > today:
			# print(today.year - born.year - 1)
			return today.year - born.year - 1
		else:
			# print(today.year - born.year)
			return today.year - born.year


class RedemptionScheme(models.Model):
	schemeName = models.CharField(max_length=512,blank=True,null=True)
	schemeImageUrl = models.CharField(max_length=512,blank=True,null=True)
	schemeDisplayName = models.CharField(max_length=512,blank=True,null=True)
	schemeCostInRupees = models.IntegerField(default=0)
	schemeCostInPCoins = models.IntegerField(default=0)

class RedemptionCouponsSent(models.Model):
	schemeName = models.CharField(max_length=512,blank=True,null=True)
	quantity = models.IntegerField(default=0)
	to = models.CharField(max_length=512,blank=True,null=True)
	sent = models.BooleanField(default=0)
	def __unicode__(self):
		return self.quantity+' '+self.schemeName + 'to' + self.to
