from django.conf.urls import patterns, include, url
from login import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
	url(r'^$',views.LoggedInView.as_view(),name='loggedIn'),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
)
