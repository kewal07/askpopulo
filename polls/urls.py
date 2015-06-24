from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
	url(r'^$',views.IndexView.as_view(),name='index'),
	url(r'^mypolls/(?P<user_name>[\w\-]+)$',views.IndexView.as_view(),name='mypolls'),
	url(r'^category$',views.IndexView.as_view(),name='polls_category'),
	url(r'^polls/featuredpolls$',views.IndexView.as_view(),name='featured'),
	url(r'^polls/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',views.VoteView.as_view(),name='polls_vote'),
	url(r'^editpoll/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',login_required(views.EditView.as_view()),name='polls_edit'),
	url(r'^deletepoll/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',login_required(views.DeleteView.as_view()),name='polls_delete'),
	url(r'^createpoll$',login_required(views.CreatePollView.as_view()),name='polls_create'),
	# url(r'^polls/FeaturedPolls$',views.FeaturedPollView.as_view(),name='featured_old'),
	# url(r'^polls/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$',views.DetailView.as_view(),name='polls_detail'),
	url(r'^polls/autocomplete', views.autocomplete,name="polls_autocomplete"),
	url(r'^search/?$', views.PollsSearchView(), name='search_view'),
	url(r'^follow/(?P<pk>\d+)/(?P<que_slug>[\w\-]+)$', login_required(views.FollowPollView.as_view()),name="polls_follow"),
	url(r'^abuse$', login_required(views.ReportAbuse.as_view()),name="polls_abuse"),
	url(r'^categories$',views.CategoryView.as_view(),name='categories'),
)
