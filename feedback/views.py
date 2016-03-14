from django.shortcuts import render
from django.views import generic
from polls.models import Question

# Create your views here.
class IndexView(generic.ListView):
	context_object_name = "data"
	def get_template_names(self, **kwargs):
		template_name = 'feedback_templates.html'
		return [template_name]
	def get_queryset(self):
		context = {}
		context["polls"] = Question.objects.filter(user_id=4,is_feedback=1)
		return context