from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect
from django.views import generic
from polls.models import Question,Choice,Vote,Subscriber,Voted
# Create your views here.

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'data'
	
	def get_queryset(self):
		mainData = []
		latest_questions = Question.objects.order_by('-pub_date')[:10]
		for mainquestion in latest_questions:
			data = {}
			data ['question'] = mainquestion
			subscribers = mainquestion.subscriber_set.count()
			# totalVotes = 0
			# choices = Choice.objects.filter(question=mainquestion.id)
			# for qchoice in choices:
				# votes = qchoice.vote_set.count()
				# totalVotes += votes
			data['votes'] = mainquestion.voted_set.count()
			data['subscribers'] = subscribers
			mainData.append(data)
		return mainData
		
class VoteView(generic.ListView):
	
	# context_object_name = 'data'

	def get(self, request, *args, **kwargs):
		# print(reverse('polls:index'))
		url = reverse('polls:index')
		user = request.user
		# print ('voting')
		# print(dir(user))
		# print(user.is_authenticated())
		# print(request.GET.get('choice'))
		# print(request.GET.get('question'))
		if request.GET.get('choice'):
			# save vote
			choiceId = request.GET.get('choice')
			choice = Choice.objects.get(pk=choiceId)
			questionId = request.GET.get('question')
			question = Question.objects.get(pk=questionId)
			if user.is_authenticated():
				voted_questions = user.voted_set.filter(user=user,question=question)
				if not voted_questions:
					vote = Vote(user=user, choice=choice)
					voted = Voted(user=user, question=question)
					vote.save()
					voted.save()
		else:
			# error to show no choice selected
			pass
		if not user.is_authenticated():
			# url = 'account/login.html'
			url = reverse('account_login')
		return HttpResponseRedirect(url)
		
	# def get_template_names(self):
		# template_name = resolve('polls:index')
		# user = self.request.user
		# print ('voting')
		# print(dir(user))
		# print(user.is_authenticated())
		# if not user.is_authenticated():
			# template_name = 'account/login.html'
			# template_name = resolve('account_login')
		# return template_name
	
	# def get_queryset(self):
		# request = self.request
		# user = self.request.user
		# print ('voting')
		# # print(dir(user))
		# # print(user.is_authenticated())
		# # print(request.GET.get('choice'))
		# # print(request.GET.get('question'))
		# if request.GET.get('choice'):
			# # save vote
			# choiceId = request.GET.get('choice')
			# choice = Choice.objects.get(pk=choiceId)
			# questionId = request.GET.get('question')
			# question = Question.objects.get(pk=questionId)
			# if user.is_authenticated():
				# voted_questions = user.voted_set
				# print("voted")
				# print(voted_questions)
				# if question not in voted_questions:
					# vote = Vote(user=user, choice=choice)
					# # vote.save()
				# pass
		# else:
			# # error to show no choice selected
			# pass
		
	# def get_success_url(self):
		# return reverse('index')

# class DetailView(generic.DetailView):
	# template_name = 'polls/index.html'