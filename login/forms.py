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
	birthDay = forms.DateField(widget=CustomDateInput)
	bio = forms.CharField( max_length=1024, label="About Me", widget=forms.Textarea(attrs={'placeholder': 'Tell me something about yourself'}),required=False)
	professionList = ["","Student","Politics","Education","Information Technology","Public Sector","Social Services","Medical","Finance","Manager","Others"]
	profession = forms.ChoiceField([(i,i) for i in professionList],required=True)
	country = forms.ChoiceField([(i,i) for i in countryAndStateList.countryList],required=True)
	state = forms.ChoiceField([(i,i) for i in countryAndStateList.stateList],required=True)
	city = forms.CharField( max_length=512, widget=forms.TextInput(attrs={'placeholder': 'City'}),required=False)
	categories =  forms.MultipleChoiceField(required=True,widget=forms.CheckboxSelectMultiple(attrs={'class':'category_checkbox'}), choices=[(i,i) for i in Category.objects.all()])
	captcha = NoReCaptchaField(label="")
	agreement = forms.BooleanField(required=True,label="")

	def __init__(self,*args,**kwargs):
		super(MySignupForm,self).__init__(*args,**kwargs)
		self.fields.move_to_end('captcha')
		self.fields.move_to_end('agreement')

	def signup(self, request, user):
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		city=request.POST.get('city','')
		bday=request.POST.get('birthDay','')
		state=request.POST.get('state','')
		country=request.POST.get('country','')
		profession=request.POST.get('profession','')
		gender=request.POST.get('gender','')
		bio=request.POST.get('bio','').strip()
		categories=request.POST.getlist('categories','')
		categories_list = Category.objects.values_list('id', flat=True).filter(category_title__in=categories)
		user_categories = ",".join(str(x) for x in categories_list)
		extendeduser = ExtendedUser(user=user,birthDay=bday,gender=gender,city=city,state=state,country=country,bio=bio,profession=profession,imageUrl=request.FILES.get('image',''),categories=user_categories)
		extendeduser.save()