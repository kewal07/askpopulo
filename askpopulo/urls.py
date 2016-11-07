from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from django.views.generic import TemplateView
from . import settings
from django.http import HttpResponseRedirect
from polls import views
from django.contrib.auth.decorators import login_required
import django.views.defaults

urlpatterns = [
	url(r'^grappelli/', include('grappelli.urls')),
    url(r'^user/',include('login.urls',namespace="login")),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^particle',include('particle.urls',namespace="particle")),
	url(r'^feedback',include('feedback.urls',namespace="feedback")),
	url(r'^', include('polls.urls',namespace="polls")),
	url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
	url(r'^faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
	url(r'^akamai/sureroute-test-object.html',TemplateView.as_view(template_name='sureroute-test-object.html'), name='akamaisurerootobject'),
	url(r'^akamai/sla-test-object.html',TemplateView.as_view(template_name='sla-test-object.html'), name='akamaislatestobject'),
	url(r'^(?P<company_name>[\w\-]+)$',views.CompanyIndexView.as_view(),name='company_page'),
	url(r'^trivia/',include('trivia.urls',namespace="trivia")),
	url(r'^ckeditor/', include('ckeditor_uploader.urls')),
	url(r'^404/$',django.views.defaults.page_not_found, ),
	url(r'^admin/django-ses/', include('django_ses.urls')),
	url(r'^api/', include('api.urls', namespace="api")),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
