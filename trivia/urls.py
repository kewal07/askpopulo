from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from trivia import views

urlpatterns = [
    url(r'^$',views.TriviaView.as_view(),name='trivia'),
	]
