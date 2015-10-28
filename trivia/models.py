import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
import os
from categories.models import Category
from django.template.defaultfilters import slugify
from login.models import ExtendedUser
from PIL import Image
import hashlib
import hmac
from datetime import date
from stream_django.activity import Activity
from polls.models import Question

# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "trivia%s.%s" % (instance.id,ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'trivia'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

class Trivia(models.Model):
	trivia_title = models.CharField(max_length=200)
	trivia_header = models.CharField(max_length=200,null=True,blank=True)
	trivia_body = models.CharField(max_length=400,null=True,blank=True)
	trivia_slug = models.SlugField(null=True,blank=True)
	trivia_image = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	pub_date = models.DateTimeField('Date Published')
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	upvoteCount = models.IntegerField(default=0)
	numViews = models.IntegerField(blank=True,null=True,default=0)
	last_accessed = models.DateTimeField(null=True,blank=True)
	category = models.ForeignKey(Category)

	def __str__(self):
		return self.trivia_title

	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'

	def save(self, *args, **kwargs):
		t_title = self.trivia_title
		short_trivia_title = t_title[:50]
		if not short_trivia_title.strip():
			short_trivia_title = None
		t_slug = slugify(short_trivia_title)
		if not t_slug and not t_slug.strip():
			t_slug = None
		self.trivia_slug = t_slug
		self.last_accessed = datetime.datetime.now()
		super(Trivia, self).save(*args, **kwargs)
	
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
			return "/media/trivia/"+self.get_folder_day(imageUrl)+os.sep+self.get_profile_pic_name(imageUrl)

	def get_img_url(self):
		if self.trivia_image:
			trivia_image_url = self.get_pic_url(self.trivia_image)
			return trivia_image_url
