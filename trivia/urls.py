from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from trivia import views

urlpatterns = patterns('',
    url(r'^$',login_required(views.TriviaView.as_view()),name='trivia'),
	)
