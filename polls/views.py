from django.shortcuts import render
from django.views import generic
from polls.models import Question
# Create your views here.

def index(request):
	return render(request,'polls/index.html')

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_questions'
	
	def get_queryset(self):
		return Question.objects.order_by('-pub_date')[:10]

# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'