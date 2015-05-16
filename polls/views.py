from django.shortcuts import render
from django.core.urlresolvers import resolve,reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from polls.models import Question,Choice,Vote,Subscriber,Voted,QuestionWithCategory
from categories.models import Category
import datetime
import simplejson as json
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from haystack.forms import ModelSearchForm

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

class FeaturedPollView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'data'
	
	def get_queryset(self):
		mainData = []
		latest_questions = Question.objects.filter(user__is_superuser=1).order_by('-pub_date')[:10]
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
	
class DetailView(generic.DetailView):
	model = Question
	
	def get_template_names(self):
		template_name = 'polls/voteQuestion.html'
		question = self.get_object()
		user = self.request.user
		if user.is_authenticated():
			voted = Voted.objects.filter(question = question, user=user)
			if voted:
				template_name = 'polls/questionDetail.html'
		return [template_name]

class VoteView(generic.DetailView):
	model = Question
	template_name = 'polls/voteQuestion.html'

	def post(self, request, *args, **kwargs):
		user = request.user
		questionId = -1
		queSlug = "None"
		if request.POST.get('choice'):
			choiceId = request.POST.get('choice')
			choice = Choice.objects.get(pk=choiceId)
			questionId = request.POST.get('question')
			question = Question.objects.get(pk=questionId)
			queSlug = question.que_slug
			# if user.is_authenticated():
			voted_questions = user.voted_set.filter(user=user,question=question)
			if not voted_questions:
				vote = Vote(user=user, choice=choice)
				voted = Voted(user=user, question=question)
				vote.save()
				voted.save()
		else:
			# error to show no choice selected
			pass
		url = reverse('polls:polls_detail', kwargs={'pk':questionId,'que_slug':queSlug})
		return HttpResponseRedirect(url)

class CreatePollView(generic.ListView):
	template_name = 'polls/createPoll.html'
	context_object_name = 'data'
	
	def get_queryset(self):
		return Category.objects.all()
	
	def post(self, request, *args, **kwargs):
		url = reverse('polls:index')
		user = request.user
		if not user.is_authenticated():
			url = reverse('account_login')
		elif request.POST:
			qText = request.POST.get('qText')
			if not qText:
				self.errors['qTextError'] = "Question required"
			qDesc = request.POST.get('qDesc')
			qExpiry = request.POST.get('qExpiry')
			if not qExpiry:
				qExpiry = None
			choice1 = request.POST.getlist('choice1')[0].strip()
			choice1Image = request.FILES.get('choice1')
			choice2 = request.POST.getlist('choice2')[0].strip()
			choice2Image = request.FILES.get('choice2')
			if (not choice1 or not choice2) and (not choice1Image or not choice2Image):
				self.errors['choiceError'] = "At least 2 choices should be provided"
			choice3 = request.POST.getlist('choice3')[0].strip()
			choice3Image = request.FILES.get('choice3')
			choice4 = request.POST.getlist('choice4')[0].strip()
			choice4Image = request.FILES.get('choice4')
			selectedCats = request.POST.get('selectedCategories','').split(",")
			isAnon = request.POST.get('anonymous')
			if isAnon:
				anonymous = 1
			else:
				anonymous = 0
			question = Question(user=user, question_text=qText, description=qDesc, expiry=qExpiry, pub_date=datetime.datetime.now(),isAnonymous=anonymous)
			question.save()
			for cat in selectedCats:
				if cat:
					category = Category.objects.filter(category_title=cat)[0]
					qWcat = QuestionWithCategory(question=question,category=category)
					qWcat.save()
			if choice1 or choice1Image:
				choice1 = Choice(question=question,choice_text=choice1,choice_image=choice1Image)
				choice1.save()
			if choice2 or choice2Image:
				choice2 = Choice(question=question,choice_text=choice2,choice_image=choice2Image)
				choice2.save()
			if choice3 or choice3Image:
				choice3 = Choice(question=question,choice_text=choice3,choice_image=choice3Image)
				choice3.save()
			if choice4 or choice4Image:
				choice4 = Choice(question=question,choice_text=choice4,choice_image=choice4Image)
				choice4.save()
		return HttpResponseRedirect(url)

class PollsSearchView(SearchView):
    
    def extra_context(self):
        queryset = super(PollsSearchView, self).get_results()
        # further filter queryset based on some set of criteria
        # return queryset
        return {
            'query': queryset,
        }


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(question_auto=request.GET.get('qText', ''))[:5]
    suggestions = [[result.object.question_text,result.object.id,result.object.que_slug] for result in sqs]
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')