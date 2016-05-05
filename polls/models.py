import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
import os,sys,linecache
from categories.models import Category
from django.template.defaultfilters import slugify
from login.models import ExtendedUser,Company
from PIL import Image
import hashlib
import hmac
from datetime import date
from stream_django.activity import Activity
from django.core.urlresolvers import resolve,reverse
# Create your models here.

shakey=(settings.SHAKEY).encode('utf-8')

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "choice%s.%s" % (instance.question.id,ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'choices'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

def get_file_path_featured(instance, filename):
	ext = filename.split('.')[-1]
	filename = "featured%s.%s" % (instance.id,ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'featuredimages'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

def get_file_path_email(instance, filename):
	ext = filename.split('.')[-1]
	filename = "email%s.%s" % (instance.id,ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'emailimages'+os.sep+str(folder_day)))
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
	privatePoll = models.BooleanField(default=0)
	featuredPoll = models.BooleanField(default=0)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	upvoteCount = models.IntegerField(default=0)
	isBet = models.BooleanField(default=0)
	winning_choice = models.IntegerField(blank=True,null=True)
	numViews = models.IntegerField(blank=True,null=True,default=0)
	last_accessed = models.DateTimeField(null=True,blank=True)
	home_visible = models.BooleanField(default=1)
	protectResult = models.BooleanField(default=0)
	featured_image = models.ImageField(upload_to=get_file_path_featured,blank=True,null=True)
	is_survey = models.BooleanField(default=0)
	is_feedback = models.BooleanField(default=0)
	authenticate = models.BooleanField(default=0)
	horizontal_options = models.BooleanField(default=0)

	def iseditable(self, request_user):
		editable = False
		if request_user.is_superuser:
			editable = True
		elif request_user == self.user and self.voted_set.count() < 1 and self.voteapi_set.count() < 1:
			editable = True
		return editable
	def save(self, *args, **kwargs):
		qText = self.question_text
		# qText = ''.join(e for e in qText if e.isalnum() or e == " ")
		if not self.que_slug:
			short_q_text = qText[:50]
			if not short_q_text.strip():
				short_q_text = None
			qslug = slugify(short_q_text)
			if not qslug and not qslug.strip():
				qslug = None
			self.que_slug = qslug
		digestmod = hashlib.sha1
		msg = ("%s %s %s"%(self.question_text,self.pub_date,self.user.username)).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		self.que_pk = sig
		# self.numViews = 0
		self.last_accessed = datetime.datetime.now()
		super(Question, self).save(*args, **kwargs)
	def __str__(self):
		return self.question_text
	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'
	def get_extra_choices(self):
		ex_ch = 4 - self.choice_set.count()
		ch_list = []
		if ex_ch > 0:
			for x in range(ex_ch,4):
				ch_list.append(x+1)
		return ch_list
	def has_image(self):
		image_list = []
		if self.featured_image:
			image_list.append("/media/featuredimages/"+self.get_file_name())
		if not image_list:
			for choice in self.choice_set.all():
				if choice.choice_image:
					image_list.append("/media/choices/"+choice.get_file_name())
		return image_list
	def has_choice_image(self):
		has_choice_image = False
		for choice in self.choice_set.all():
			if choice.choice_image:
				has_choice_image = True
				break
		return has_choice_image
	def get_user_details(self):
		if self.isAnonymous:
			pic_url = "/static/login/images/defaultAvatar.png"
			user_url = ""
			user_alt = "Anonymous"
			user_name = "Anonymous"
		elif self.user.extendeduser.company_id > 1:
			pic_url = self.user.extendeduser.get_profile_pic_url()
			user_url = reverse('company_page', kwargs={'company_name':self.user.extendeduser.company.company_slug})
			# user_alt = "User %s"%(self.user.extendeduser.company.name)
			# user_name = self.user.extendeduser.company.name
			user_alt = "User %s"%(self.user.first_name)
			user_name = self.user.first_name
		else:
			pic_url = self.user.extendeduser.get_profile_pic_url()
			user_url = reverse('login:loggedIn', kwargs={'pk':self.user.id,'user_slug':self.user.extendeduser.user_slug})
			user_alt = "User %s"%(self.user.first_name)
			user_name = self.user.first_name
		user_details = {}
		user_details['pic_url'] = pic_url
		user_details['user_url'] = user_url
		user_details['user_alt'] = user_alt
		user_details['user_name'] = user_name
		return user_details
	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.featured_image.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day
	def get_file_name(self):
		return self.get_folder_day()+"/"+self.featured_image.path.split(os.sep)[-1]
	def get_featured_image_url(self):
		return "/media/featuredimages/"+self.get_file_name()

class Survey(models.Model):
	survey_pk = models.CharField(max_length=255)
	survey_name = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	expiry =  models.DateTimeField(null=True,blank=True)
	description = models.CharField(max_length=400,null=True,blank=True)
	survey_slug = models.SlugField(null=True,blank=True)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	numViews = models.IntegerField(blank=True,null=True,default=0)
	last_accessed = models.DateTimeField(null=True,blank=True)
	home_visible = models.BooleanField(default=0)
	featured_image = models.ImageField(upload_to=get_file_path_featured,blank=True,null=True)
	thanks_msg = models.CharField(max_length=400,null=True,blank=True, default="Thank You for Completing the Survey!!!")
	authenticate = models.BooleanField(default=0)
	number_sections = models.IntegerField(blank=True,null=True,default=0)
	expected_time = models.IntegerField(blank=True,null=True,default=0)

	def save(self, *args, **kwargs):
		try:
			if not self.survey_slug:
				qText = self.survey_name
				# qText = ''.join(e for e in qText if e.isalnum() or e == " ")
				short_q_text = qText[:50]
				if not short_q_text.strip():
					short_q_text = None
				qslug = slugify(short_q_text)
				if not qslug and not qslug.strip():
					qslug = None
				self.survey_slug = qslug
			digestmod = hashlib.sha1
			msg = ("%s %s %s"%(self.survey_name,self.pub_date,self.user.username)).encode('utf-8')
			sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
			self.survey_pk = sig
			# self.numViews = 0
			self.last_accessed = datetime.datetime.now()
			super(Survey, self).save(*args, **kwargs)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	def __str__(self):
		return self.survey_name
	def was_published_recently(self):
		return self.pub_date>=timezone.now()-datetime.timedelta(days=1)
		was_published_recently.admin_order_field = 'pub_date'
		was_published_recently.boolean = True
		was_published_recently.short_description = 'Published recently'
	def has_image(self):
		image_list = []
		if self.featured_image:
			image_list.append("/media/featuredimages/"+self.get_file_name())
		if not image_list:
			polls = [ x.question for x in Survey_Question.objects.filter(survey_id=self.id)]
			for poll in polls:
				for choice in poll.choice_set.all():
					if choice.choice_image:
						image_list.append("/media/choices/"+choice.get_file_name())
		return image_list
	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.featured_image.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day
	def get_file_name(self):
		return self.get_folder_day()+"/"+self.featured_image.path.split(os.sep)[-1]
	def get_featured_image_url(self):
		return "/media/featuredimages/"+self.get_file_name()

class SurveyWithCategory(models.Model):
	survey = models.ForeignKey(Survey)
	category = models.ForeignKey(Category)
	def __str__(self):
		return self.category.category_title
	def save(self, *args, **kwargs):
		super(SurveyWithCategory, self).save(*args, **kwargs)

class SurveySection(models.Model):
	sectionName = models.CharField(max_length=64)
	sectionOrder = models.IntegerField()
	survey = models.ForeignKey(Survey)
	def __str__(self):
		return self.sectionName+"---"+str(self.sectionOrder)

class Survey_Question(models.Model):
	survey = models.ForeignKey(Survey)
	question = models.ForeignKey(Question)
	question_type = models.CharField(max_length=20)
	add_comment = models.BooleanField(default=0)
	mandatory = models.BooleanField(default=0)
	min_value  = models.IntegerField(default=0)
	max_value = models.IntegerField(default=10)
	section = models.ForeignKey(SurveySection,null=True,default=None)
	def __str__(self):
		return self.survey.survey_name+"_"+self.question.question_text+"_"+self.question_type

class SurveyVoted(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	survey = models.ForeignKey(Survey)
	created_at = models.DateTimeField(auto_now_add=True)
	survey_question_count = models.IntegerField(blank=True,null=True,default=0)
	user_answer_count = models.IntegerField(blank=True,null=True,default=0)
	def __str__(self):
		return self.survey.survey_name+" : "+self.user.username
	def save(self, *args, **kwargs):
		super(SurveyVoted, self).save(*args, **kwargs)

class Choice(models.Model):
	choice_pk = models.CharField(max_length=255)
	question = models.ForeignKey(Question)
	choice_text = models.CharField(max_length=200)
	choice_image = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	def __str__(self):
		return self.choice_text
	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.choice_image.path.split(os.sep)[-2]
			# print(day.split("-"))
			# print(day,int(day.split("-")[0]),int(day.split("-")[2]),int(day.split("-")[3]))
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day
	def get_file_name(self):
		return self.get_folder_day()+"/"+self.choice_image.path.split(os.sep)[-1]
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		msg = ("%s %s"%(self.choice_text,datetime.datetime.now())).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		self.choice_pk = sig
		super(Choice, self).save(*args, **kwargs)
		"""
		if self.choice_image:
			size = 128, 128
			im = Image.open(self.choice_image)
			im.thumbnail(size)
			im.save(self.choice_image.path)
		"""

class VoteText(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	answer_text = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	user_data = models.TextField()
	def __str__(self):
		return self.answer_text
	def save(self, *args, **kwargs):
		user_data = {}
		if self.user_data:
			user_data = self.user_data
		# if not self.user_data:
		for field in self.user.extendeduser._meta.get_fields():
			# print(dir(field))
			if not field.is_relation and field.name != "imageUrl":
				if field.name == "birthDay":
					age = self.user.extendeduser.calculate_age()
					user_data[field.name] = age
				else:
					user_data[field.name] = getattr(self.user.extendeduser, field.name)
		self.user_data = str(user_data)
		super(VoteText, self).save(*args, **kwargs)

class Demographics(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	survey_id = models.IntegerField(default=0)
	question_id = models.IntegerField(default=0)
	demographic_data = models.TextField()

class Vote(models.Model):
	vote_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	choice = models.ForeignKey(Choice)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	betCredit = models.IntegerField(default=0)
	earnCredit = models.IntegerField(default=0)
	user_data = models.TextField()
	def __str__(self):
		return self.choice.choice_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		try:
			digestmod = hashlib.sha1
			msg = ("%s %s %s"%(self.choice.choice_text,self.user.username,datetime.datetime.now())).encode('utf-8')
			sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
			self.vote_pk = sig
			user_data = {}
			if self.user_data:
				user_data = self.user_data
			# if not self.user_data:
			for field in self.user.extendeduser._meta.get_fields():
				# print(dir(field))
				if not field.is_relation and field.name != "imageUrl":
					if field.name == "birthDay":
						age = self.user.extendeduser.calculate_age()
						user_data[field.name] = age
					else:
						user_data[field.name] = getattr(self.user.extendeduser, field.name)
			self.user_data = str(user_data)
			# print("-------------",self.user_data)		
			super(Vote, self).save(*args, **kwargs)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

class Subscriber(models.Model):
	subscriber_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	def __str__(self):
		return self.question.question_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		msg = ("%s %s %s"%(self.question.question_text,self.user.username,datetime.datetime.now())).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		self.subscriber_pk = sig
		super(Subscriber, self).save(*args, **kwargs)
		
class Voted(models.Model):
	voted_pk = models.CharField(max_length=255)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	created_at = models.DateTimeField(auto_now_add=True)
	# @property
	# def extra_activity_data(self):
	# 	return {'question_text': self.question.question_text,'question_url': "/polls/"+str(self.question.id)+"/"+self.question.que_slug,'question_desc': self.question.description,'actor_user_name':self.user.username,'actor_user_pic':self.user.extendeduser.get_profile_pic_url(),'actor_user_url':'/user/'+str(self.user.id)+"/"+self.user.extendeduser.user_slug,'target_user_name':self.question.user.username,'target_user_pic':self.question.user.extendeduser.get_profile_pic_url(),'target_user_url':'/user/'+str(self.question.user.id)+"/"+self.question.user.extendeduser.user_slug }
	# @property
	# def activity_object_attr(self):
	# 	return self.user.username
	def __str__(self):
		return self.question.question_text+" : "+self.user.username
	def save(self, *args, **kwargs):
		digestmod = hashlib.sha1
		msg = ("%s %s %s"%(self.question.question_text,self.user.username,datetime.datetime.now())).encode('utf-8')
		sig = hmac.HMAC(shakey, msg, digestmod).hexdigest()
		self.voted_pk = sig
		# print("Voted")
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
		self.queWithCat_pk = sig
		super(QuestionWithCategory, self).save(*args, **kwargs)

class QuestionUpvotes(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	vote = models.BooleanField(default=0)
	
class MatrixRatingColumnLabels(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	question = models.ForeignKey(Question)
	columnLabel = models.CharField(max_length=200)
	columnWeight = models.IntegerField(default=1)
	def __str__(self):
		return self.question.question_text + "__"  + self.columnLabel + "__" + str(self.columnWeight)

class VoteApi(models.Model):
	choice = models.ForeignKey(Choice)
	question = models.ForeignKey(Question)
	ipAddress = models.GenericIPAddressField(blank=True,null=True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	age = models.IntegerField(null=True)
	gender = models.CharField(max_length=1,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	profession = models.CharField(max_length=512,blank=True,null=True)
	email = models.EmailField(max_length=70,blank=True, null= True)
	session = models.CharField(max_length=512,blank=True,null=True)
	src = models.CharField(max_length=512,blank=True,null=True)
	answer_text = models.CharField(max_length=512,blank=True,null=True)
	votecolumn = models.ForeignKey(MatrixRatingColumnLabels, null=True)
	user_data = models.TextField()
	unique_key = models.CharField(max_length=512,blank=True,null=True)
	def save(self, *args, **kwargs):
		if not self.email:
			self.email = None
		super(VoteApi, self).save(*args, **kwargs)
	

class PollTokens(models.Model):
	token = models.CharField(max_length=512,blank=True,null=True)
	email = models.EmailField(max_length=254,blank=True, null= True)
	question = models.ForeignKey(Question, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)

class EmailTemplates(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	name = models.CharField(max_length=254)
	subject = models.CharField(max_length=512, default="Let us know what you think")
	body1 = models.CharField(max_length=512,blank=True, null= True)
	body2 = models.CharField(max_length=512,blank=True, null= True)
	salutation = models.CharField(max_length=512, default="Thanks & Regards")
	company = models.ForeignKey(Company)
	body_image = models.ImageField(upload_to=get_file_path_email,blank=True,null=True)
	def __str__(self):
		return self.name
	def get_display_name(self):
		display_name = self.name
		company_append_length = len(self.company.company_slug) + 3
		name_length = len(display_name)
		if name_length > company_append_length:
			company_append_string = "---" + self.company.company_slug
			if display_name[-company_append_length:] == company_append_string:
				display_name = display_name[:-company_append_length]
		return display_name
	def get_folder_day(self):
		folder_day = ""
		pathlist = self.body_image.path.split(os.sep)
		prepend_path = "media/emailimages/"
		try:
			day = pathlist[-2]
			# print(day.split("-"))
			# print(day,int(day.split("-")[0]),int(day.split("-")[2]),int(day.split("-")[3]))
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return prepend_path+folder_day
	def get_file_path(self):
		if self.body_image:
			return self.get_folder_day()+"/"+self.body_image.path.split(os.sep)[-1]
		else:
			return "static/polls/images/email_body.jpg"

class UsersReferred(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="referral_user")
	referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="referred_user")
	def __str__(self):
		return self.user.username

class PollsReferred(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	referred_question = models.ForeignKey(Question)
	referred_question_count = models.IntegerField(blank=True, null= True, default=0)
	def __str__(self):
		return self.user.username

class SurveysReferred(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	referred_survey = models.ForeignKey(Survey)
	referred_survey_count = models.IntegerField(blank=True, null= True, default=0)
	def __str__(self):
		return self.user.username	
		
class VoteColumn(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	vote = models.ForeignKey(Vote)
	choice = models.ForeignKey(Choice)
	column = models.ForeignKey(MatrixRatingColumnLabels)
	def __str__(self):
		return self.question.question_text+"__"+self.choice.choice_text+"__"+self.column.columnLabel

