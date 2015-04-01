from django.conf.urls import patterns, include, url
from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
	url(r'^$',views.IndexView.as_view(),name='index'),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
)
