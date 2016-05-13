from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='url_target_blank', is_safe=True)
def url_target_blank(text):
	return text.replace('<a ', '<a target="_blank" ')
url_target_blank = register.filter(url_target_blank)

@register.filter(name='get_required')
def get_required(v):
	ret = ''
	if v:
		ret='required'
	return ret

@register.filter(name='get_selected')
def get_selected(v1,v2):
	ret = ""
	if v1==v2:
		ret = "selected"
	return ret

@register.filter(name='get_checked')
def get_selected(v1):
	ret = ""
	if v1:
		ret = "checked"
	return ret