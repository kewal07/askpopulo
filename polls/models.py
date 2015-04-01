import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
# Create your models here.


class Question(models.Model):
	question_text = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	expiry =  models.DateTimeField(null=True,blank=True)
	description = models.CharField(max_length=400,null=True,blank=True)
	def __str__(self):
		return self.question_text
	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'

class Choice(models.Model):
	question = models.ForeignKey(Question)
	choice_text = models.CharField(max_length=200)

class Vote(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	choice = models.ForeignKey(Choice)

class Subscriber(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)