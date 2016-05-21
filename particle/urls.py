from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from particle import views

urlpatterns = [
    url(r'^$',views.ParticleView.as_view(),name='particle'),
    url(r'^(?P<pk>\d+)/(?P<particle_slug>[\w\-]+)$',views.ParticleDetailView.as_view(),name='particle_detail')
	]
