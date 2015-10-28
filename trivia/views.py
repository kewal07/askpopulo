from django.shortcuts import render
from login.views import BaseViewList
from trivia.models import Trivia
# Create your views here.

class TriviaView(BaseViewList):
	context_object_name = 'trivias'
	
	def get_template_names(self, **kwargs):
		template_name = 'trivia/trivia.html'
		return [template_name]

	def get_queryset(self):
		context = {}
		triviaList = Trivia.objects.order_by('-pub_date')
		for trivia in triviaList:
			print(trivia.trivia_body)
		context['trivias'] = triviaList
		return triviaList
	
		