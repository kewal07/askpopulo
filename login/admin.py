from django.contrib import admin
from django.conf import settings
from login.models import RedemptionScheme, RedemptionCouponsSent, Company, ExtendedUser,ExtendedGroup,ExtendedGroupFuture

class ExtUserAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )

admin.site.register(RedemptionScheme)
admin.site.register(RedemptionCouponsSent)
admin.site.register(Company)
admin.site.register(ExtendedUser,ExtUserAdmin)
admin.site.register(ExtendedGroup)
admin.site.register(ExtendedGroupFuture)
# Register your models here.
