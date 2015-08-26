from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from . import settings

urlpatterns = patterns('',
    url(r'^user/',include('login.urls',namespace="login")),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^', include('polls.urls',namespace="polls")),
	url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
