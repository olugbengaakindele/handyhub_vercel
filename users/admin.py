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
    SearchAnalytics,
    ProfileDailyAnalytics,
    ProfileReport,

)

admin.site.register(UserProfile)
admin.site.register(UserService)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(ServiceArea)
admin.site.register(License)
admin.site.register(SearchAnalytics)
admin.site.register(ProfileDailyAnalytics)

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

@admin.register(ProfileReport)
class ProfileReportAdmin(admin.ModelAdmin):
    list_display = ("reported_user", "reporter", "reason", "status", "created_at")
    list_filter = ("reason", "status", "created_at")
    search_fields = (
        "reporter__username",
        "reporter__email",
        "reported_user__username",
        "reported_user__email",
        "description",
    )
    readonly_fields = ("reporter", "reported_user", "reason", "description", "created_at")