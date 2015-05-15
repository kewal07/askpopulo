from django.conf.urls import patterns, include, url
from login import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
    url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/$',views.LoggedInView.as_view(),name='loggedIn'),
	url(r'^$',views.RedirectLoginView.as_view(),name='loginRedirect'),
	url(r'^editprofile$',views.EditProfileView.as_view(),name='edit_profile'),
	url(r'^logout$',views.logout_view,name="logout"),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
)
