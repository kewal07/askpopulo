from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
	url(r'^$',login_required(views.IndexView.as_view()),name='index'),
	url(r'^mypolls/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.IndexView.as_view()),name='mypolls'),
	url(r'^category$',login_required(views.IndexView.as_view()),name='polls_category'),
	url(r'^polls/featuredpolls$',login_required(views.IndexView.as_view()),name='featured'),
	url(r'^polls/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',login_required(views.VoteView.as_view()),name='polls_vote'),
	url(r'^polls/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)/result$',login_required(views.VoteView.as_view()),name='polls_result'),
	url(r'^editpoll/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',login_required(views.EditView.as_view()),name='polls_edit'),
	url(r'^deletepoll/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',login_required(views.DeleteView.as_view()),name='polls_delete'),
	url(r'^createpoll$',login_required(views.CreatePollView.as_view()),name='polls_create'),
	# url(r'^polls/FeaturedPolls$',views.FeaturedPollView.as_view(),name='featured_old'),
	# url(r'^polls/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',views.DetailView.as_view(),name='polls_detail'),
	url(r'^polls/autocomplete', views.autocomplete,name="polls_autocomplete"),
	url(r'^search/?$', views.PollsSearchView(), name='search_view'),
	url(r'^follow/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$', login_required(views.FollowPollView.as_view()),name="polls_follow"),
	url(r'^abuse$', login_required(views.ReportAbuse.as_view()),name="polls_abuse"),
	url(r'^comment_mail$', views.comment_mail,name="comment_mail"),
	url(r'^companyname$',views.error_CompanyName,name="error_CompanyName"),
	url(r'^privacypolicy$',views.privacyPolicy,name="privacyPolicy"),
	url(r'^unsubscribe$',views.MyUnsubscribeView.as_view(),name="unsubscribe"),
	url(r'^upvoted/$',views.QuestionUpvoteView.as_view(),name="upvote"),
	url(r'^team$',views.TeamView.as_view(),name='team'),
	url(r'^about_us$',views.TeamView.as_view(),name='aboutus'),
	url(r'^sandeep$',views.TeamView.as_view(),name='sandeep'),
	url(r'^kewal$',views.TeamView.as_view(),name='kewal'),
	url(r'^shradha$',views.TeamView.as_view(),name='shradha'),
	url(r'^ankit$',views.TeamView.as_view(),name='ankit'),
	url(r'^abhinav$',views.TeamView.as_view(),name='abhinav'),
	url(r'^advanced_analyse$',views.AccessDBView.as_view(),name='advanced_analyse'),
	url(r'^advanced_analyse_choice$',views.AccessDBView.as_view(),name='advanced_analyse_choice'),
	url(r'trivia$',views.TriviaPView.as_view(),name='trivia'),
	url(r'create_survey',views.CreateSurveyView.as_view(),name='create_survey'),
	url(r'^survey/(?P<pk>\d+)/(?P<survey_slug>[\w\-]+)$',login_required(views.SurveyVoteView.as_view()),name='survey_vote'),
	url(r'^editsurvey/(?P<pk>\d+)/(?P<survey_slug>[\w\-]+)$',login_required(views.SurveyEditView.as_view()),name='survey_edit'),
	url(r'^deletesurvey/(?P<pk>\d+)/(?P<survey_slug>[\w\-]+)$',login_required(views.SurveyDeleteView.as_view()),name='survey_delete'),
	url(r'^survey_mail$', views.survey_mail,name="survey_mail"),
)
