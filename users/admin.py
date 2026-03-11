from django.contrib import admin
from .models import (
    UserProfile,
    UserService,
    Province,
    City,
    ServiceArea,
    License,
    CallOutFeeSettings,
    Achievement,
)

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


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "issuer", "public_visibility", "created_at")
    list_filter = ("public_visibility", "created_at")
    search_fields = (
        "title",
        "issuer",
        "profile__user_firstname",
        "profile__user_last_name",
        "profile__user_business_name",
    )