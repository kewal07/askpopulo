from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
import rest_framework.authtoken.views
from api import views

urlpatterns = [
	#url(r'^gettoken$',rest_framework.authtoken.views.obtain_auth_token,name='gettoken'),
	url(r'^gettoken$',views.AuthToken.as_view(),name='gettoken'),
	url(r'^user_detail/(?P<pk>[0-9]+)$', views.UserDetail.as_view(), name='userdetail'),
	url(r'^survey_list/(?P<user>[0-9]+)', views.getSurveyList, name='getsurveylist'),
	url(r'^survey_detail/(?P<pk>[0-9]+)', views.SurveyDetail.as_view(), name='getsurveydetail'),
]
