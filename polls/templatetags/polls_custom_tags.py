from django import template
from django.template.defaultfilters import stringfilter
from polls.models import Subscriber,Voted,QuestionUpvotes

register = template.Library()

@register.filter(name='get_user_already_voted')
def get_user_already_voted(question, user):
	user_already_voted = False
	if user.is_authenticated():
		if Voted.objects.filter(user=user,question=question):
			user_already_voted = True
	return user_already_voted

@register.filter(name='get_user_subscribed')
def get_user_subscribed(question, user):
	sub = False
	if user.is_authenticated():
		if Subscriber.objects.filter(user=user,question=question):
			sub = True
	return sub

@register.filter(name='get_user_upvoted')
def get_user_upvoted(question, user):
	upvoted = False
	if user.is_authenticated():
		if QuestionUpvotes.objects.filter(question=question, user=user, vote=1):
			upvoted = True
	return upvoted

@register.filter(name='get_user_downvoted')
def get_user_downvoted(question, user):
	downvoted = False
	if user.is_authenticated():
		if QuestionUpvotes.objects.filter(question=question, user=user, vote=0):
			downvoted = True
	return downvoted

@register.filter(name='get_user_editable')
def get_user_editable(question, user):
	editable = False
	if user.is_authenticated():
		if user.is_superuser:
			editable = True
		elif user == question.user and question.voted_set.count() < 1 and question.voteapi_set.count() < 1:
			editable = True
	return editable

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
