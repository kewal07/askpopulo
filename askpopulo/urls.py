from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from django.views.generic import TemplateView
from . import settings
from django.http import HttpResponseRedirect
from polls import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
	url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^user/',include('login.urls',namespace="login")),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^', include('polls.urls',namespace="polls")),
	url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
	url(r'^faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
	#url(r'^sitemap.xml$', redirect_to, {'url': '/static/sitemap.xml'}),
	url(r'^(?P<company_name>[\w\-]+)$',login_required(views.CompanyIndexView.as_view()),name='company_page'),
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
