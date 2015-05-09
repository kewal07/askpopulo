from django.conf.urls import patterns, include, url
from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
	url(r'^$',views.IndexView.as_view(),name='index'),
	url(r'^vote$',views.VoteView.as_view(),name='polls_vote'),
	url(r'^createpoll$',views.CreatePollView.as_view(),name='polls_create'),
	url(r'^polls/FeaturedPolls$',views.FeaturedPollView.as_view(),name='featured'),
	url(r'^polls/(?P<pk>\d+)/$',views.DetailView.as_view(),name='polls_detail'),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
)
