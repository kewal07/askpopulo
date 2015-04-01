from django.shortcuts import render
from django.views import generic
from polls.models import Question,Choice,Vote,Subscriber
# Create your views here.

def index(request):
	return render(request,'polls/index.html')

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'data'
	
	def get_queryset(self):
		mainData = []
		latest_questions = Question.objects.order_by('-pub_date')[:10]
		for mainquestion in latest_questions:
			data = {}
			data ['question'] = mainquestion
			subscribers = len(Subscriber.objects.filter(question=mainquestion.id))
			totalVotes = 0
			choices = Choice.objects.filter(question=mainquestion.id)
			for qchoice in choices:
				votes = Vote.objects.filter(choice=qchoice.id)
				totalVotes += len(votes)
			data['votes'] = totalVotes
			data['subscribers'] = subscribers
			mainData.append(data)
		return mainData

# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'