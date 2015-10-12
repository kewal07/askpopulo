from django.contrib import admin
from django.conf import settings
from login.models import RedemptionScheme, RedemptionCouponsSent

admin.site.register(RedemptionScheme)
admin.site.register(RedemptionCouponsSent)

# Register your models here.
