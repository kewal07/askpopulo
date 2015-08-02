from django import forms
from .models import ExtendedUser
# from allauth.account.forms import SignupForm
from django.utils.safestring import mark_safe
from django.forms import extras
from datetime import datetime
from datetime import date
from django.conf import settings
from django.forms import widgets
from . import countryAndStateList
import os
import pymysql
from categories.models import Category
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.forms.extras.widgets import SelectDateWidget

class CustomDateInput(widgets.TextInput):
	input_type = 'date'

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class MySignupForm(forms.Form):
	required_css_class = 'required'
	curyear = datetime.now().year
	image = forms.ImageField(required=False,label='Profile Image')
	first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name','autofocus': 'autofocus'}))
	last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
	gender = forms.ChoiceField(choices=[('M','M'),('F','F'),('D','NotSay')], label='Gender', widget=forms.RadioSelect(renderer=HorizontalRadioRenderer),)
	birthDay = forms.DateField(widget=SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"),years=range(curyear-100, curyear-13)),)
	bio = forms.CharField( max_length=1024, label="About Me", widget=forms.Textarea(attrs={'placeholder': 'Tell me something about yourself'}),required=False)
	professionList = ["","Student","Politics","Education","Information Technology","Public Sector","Social Services","Medical","Finance","Manager","Others"]
	profession = forms.ChoiceField([(i,i) for i in professionList],required=True)
	country = forms.ChoiceField([(i,i) for i in countryAndStateList.countryList],required=True)
	state = forms.ChoiceField([(i,i) for i in countryAndStateList.stateList],required=True)
	city = forms.CharField( max_length=512, widget=forms.TextInput(attrs={'placeholder': 'City'}),required=False)
	categories =  forms.MultipleChoiceField(required=True,widget=forms.CheckboxSelectMultiple(attrs={'class':'category_checkbox'}), choices=[(i,i) for i in Category.objects.all()])
	captcha = NoReCaptchaField(label="")
	agreement = forms.BooleanField(required=True,label="")

	def clean_birthday(self):
		birthDay = self.cleaned_data['birthday']
		# print("&&&&&&&&&&&&&&&&&&&& clean bday",birthDay)
		birthDay = date(birthDay)
		age = self.calculate_age(birthDay)
		print(birthDay,age)
		if age < 1:
			# print(self.errors)
			raise forms.ValidationError("Age should be greater than 13 years")
		return birthDay

	def calculate_age(self,born):
		today = date.today()
		# born = self.birthDay
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

	def __init__(self,*args,**kwargs):
		super(MySignupForm,self).__init__(*args,**kwargs)
		if not args:
			self.fields.move_to_end('captcha')
			self.fields.move_to_end('agreement')
		else:
			del self.fields['captcha']
			del self.fields['agreement']


	def signup(self, request, user):
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		city=request.POST.get('city','')
		# bday=request.POST.get('birthDay','')
		state=request.POST.get('state','')
		country=request.POST.get('country','')
		profession=request.POST.get('profession','')
		gender=request.POST.get('gender','')
		bio=request.POST.get('bio','').strip()
		categories=request.POST.getlist('categories','')
		categories_list = Category.objects.values_list('id', flat=True).filter(category_title__in=categories)
		user_categories = ",".join(str(x) for x in categories_list)
		# print(request.POST)
		bday_day = int(request.POST.getlist('birthDay_day')[0])
		bday_month = int(request.POST.getlist('birthDay_month')[0])
		bday_year = int(request.POST.getlist('birthDay_year')[0])
		# print(bday_year,bday_month,bday_day)
		bday = date(bday_year,bday_month,bday_day)
		# print(bday,bday_year,bday_month,bday_day)
		extendeduser = ExtendedUser(user=user,birthDay=bday,gender=gender,city=city,state=state,country=country,bio=bio,profession=profession,imageUrl=request.FILES.get('image',''),categories=user_categories)
		extendeduser.save()

class MySignupPartForm(forms.Form):
	required_css_class = 'required'
	curyear = datetime.now().year
	gender = forms.ChoiceField(choices=[('M','M'),('F','F'),('D','NotSay')], label='Gender', widget=forms.RadioSelect(renderer=HorizontalRadioRenderer),)
	birthDay = forms.DateField(widget=SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"),years=range(curyear-100, curyear-13)),)
	professionList = ["","Student","Politics","Education","Information Technology","Public Sector","Social Services","Medical","Finance","Manager","Others"]
	profession = forms.ChoiceField([(i,i) for i in professionList],required=True)
	country = forms.ChoiceField([(i,i) for i in countryAndStateList.countryList],required=True)
	state = forms.ChoiceField([(i,i) for i in countryAndStateList.stateList],required=True)

	def __init__(self,*args,**kwargs):
		super(MySignupPartForm,self).__init__(*args,**kwargs)
		# if you want to do it to all of them
		for field in self.fields.values():
			field.error_messages = {'required':'Required'}

class UnsubscribeForm(forms.Form):
	required_css_class = 'true'
	email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))