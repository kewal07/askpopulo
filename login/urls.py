from django.conf.urls import patterns, include, url
from login import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'askpopulo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^', views.index),
    url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/$',login_required(views.LoggedInView.as_view()),name='loggedIn'),
    url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/dashboard$',login_required(views.AdminDashboard.as_view()),name='adminDashboard'),
	url(r'^$',login_required(views.RedirectLoginView.as_view()),name='loginRedirect'),
	url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/editprofile$',login_required(views.LoggedInView.as_view()),name='editprofile'),
	url(r'^editprofile$',login_required(views.EditProfileView.as_view()),name='edit_profile'),
	url(r'^logout$',views.logout_view,name="logout"),
	url(r'^changepassword$',login_required(views.MyChangePasswordView.as_view()),name="change_password"),
	url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/follow$',login_required(views.FollowView.as_view()),name='follow'),
	url(r'^notifications_read$',login_required(views.MarkFeedSeen.as_view()),name='notifications_read'),
	url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/redemption$',login_required(views.RedeemView.as_view()),name='redeem'),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
)
