from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='getName')
@stringfilter
def getName(username,activityUser):
		if username == activityUser:
			return "You"
		else: 
			return activityUser