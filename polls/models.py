import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
import os
from categories.models import Category
from django.template.defaultfilters import slugify
from login.models import ExtendedUser
from PIL import Image
# Create your models here.

shakey=settings.SHAKEY

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "choice%s_%s.%s" % (instance.question.que_pk,instance.choice_pk, ext)
	profilePath = (os.path.join(settings.BASE_DIR,'media/choices/'))
	return os.path.join(profilePath,filename)

class Question(models.Model):
	que_pk = models.CharField(max_length=255)
	question_text = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	expiry =  models.DateTimeField(null=True,blank=True)
	description = models.CharField(max_length=400,null=True,blank=True)
	isAnonymous = models.BooleanField(default=0)
	que_slug = models.SlugField(null=True,blank=True)
	
	def save(self, *args, **kwargs):
		short_q_text = self.question_text[:50]
		self.que_slug = slugify(short_q_text)
		digestmod = hashlib.sha1
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(Question, self).save(*args, **kwargs)
	def __str__(self):
		return self.question_text
	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'

class Choice(models.Model):
	choice_pk = models.CharField(max_length=255)
	question = models.ForeignKey(Question)
	choice_text = models.CharField(max_length=200)
	choice_image = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	def __str__(self):
		return self.choice_text
	def get_file_name(self):
		return self.choice_image.path.split("\\")[-1]
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		msg = ("%s %s"%(self.choice_text,datetime.datetime.now())).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(Choice, self).save(*args, **kwargs)
		if self.choice_image:
			size = 128, 128
			im = Image.open(self.choice_image)
			im.thumbnail(size)
			im.save(self.choice_image.path)

class Vote(models.Model):
	vote_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	choice = models.ForeignKey(Choice)
	def __str__(self):
		return self.choice.choice_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(Vote, self).save(*args, **kwargs)

class Subscriber(models.Model):
	subscriber_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	def __str__(self):
		return self.question.question_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(Subscriber, self).save(*args, **kwargs)
		
class Voted(models.Model):
	voted_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	def __str__(self):
		return self.question.question_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(Voted, self).save(*args, **kwargs)

class QuestionWithCategory(models.Model):
	queWithCat_pk = models.CharField(max_length=255)
	question = models.ForeignKey(Question)
	category = models.ForeignKey(Category)
	def __str__(self):
		return self.category.category_title
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		msg = ("%s %s %s"%(self.question.question_text,self.category.category_title,datetime.datetime.now())).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		super(QuestionWithCategory, self).save(*args, **kwargs)
	
