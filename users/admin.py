from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(UserService)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(ServiceArea)
admin.site.register(License)

@admin.register(CallOutFeeSettings)
class CallOutFeeSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "enabled", "amount", "updated_at")
    search_fields = ("user__username", "user__email")