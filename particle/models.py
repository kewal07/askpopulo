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
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "Particle%s.%s" % (instance.id,ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'particle'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

class Particle(models.Model):
	particle_title = models.CharField(max_length=200)
	particle_summary = models.CharField(max_length=200,null=True,blank=True)
	# particle_body = models.CharField(max_length=400,null=True,blank=True)
	particle_content = RichTextUploadingField()
	particle_slug = models.SlugField(null=True,blank=True)
	particle_featured_image = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	particle_views = models.IntegerField(blank=True,null=True,default=0)
	last_accessed = models.DateTimeField(null=True,blank=True)
	category = models.ForeignKey(Category)
	read_time = models.CharField(max_length=20)
	is_draft = models.BooleanField(default=0)
	is_featured = models.BooleanField(default=0)
	is_prime = models.BooleanField(default=0)

	class Meta:
		get_latest_by = 'created_at'

	def __str__(self):
		return self.particle_title

	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'

	def save(self, *args, **kwargs):
		p_title = self.particle_title
		short_particle_title = p_title[:50]
		if not short_particle_title.strip():
			short_particle_title = None
		p_slug = slugify(short_particle_title)
		if not p_slug and not p_slug.strip():
			p_slug = None
		self.particle_slug = p_slug
		self.last_accessed = datetime.datetime.now()
		super(Particle, self).save(*args, **kwargs)
	
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
			return "/media/particle/"+self.get_folder_day(imageUrl)+'/'+self.get_profile_pic_name(imageUrl)

	def get_img_url(self):
		if self.particle_featured_image:
			particle_image_url = self.get_pic_url(self.particle_featured_image)
			return particle_image_url
