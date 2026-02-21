from django.urls import path
from . import views
from django.contrib.auth.views import LoginView 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path( "login/", LoginView.as_view(template_name="users/login.html",  authentication_form=AuthenticationForm  ), name="login"),
    path("logout/", views.logmeout, name="logout"),

    # ✅ profile is current logged-in user (no userid)
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # ✅ services (no userid)
    path("userservice/", views.add_user_services, name="userservice"),
    path("services/delete/<int:service_id>/", views.delete_user_service, name="delete_user_service"),

    # profile edits
    path("edit-profile-picture/", views.edit_profile_picture, name="edit_profile_picture"),
    path("edit-contact-info/", views.edit_contact_info, name="edit_contact_info"),
    path("edit-address-info/", views.edit_address_info, name="edit_address_info"),

    # service areas
    path("edit-service-areas/", views.edit_service_areas, name="edit_service_areas"),
    path("service-areas/delete/<int:area_id>/", views.delete_service_area_confirm, name="delete_service_area"),

    # static pages
    path("about/", views.about, name="about"),
    path("contactus/", views.contactus, name="contactus"),

    path("find-service/", views.find_service, name="find_service"),      # HTML page
    path("api/find-service/", views.api_find_service, name="api_find_service"),  # JSON endpoint
    path("profile/<int:user_id>/", views.profile_detail, name="profile_detail"),

    # Gallery urls
    path("gallery/", views.gallery_list, name="gallery_list"),
    path("gallery/add/", views.gallery_add, name="gallery_add"),
    path("gallery/<int:photo_id>/edit/", views.gallery_edit, name="gallery_edit"),
    path("gallery/<int:photo_id>/delete/", views.gallery_delete, name="gallery_delete"),
    path("gallery/<int:photo_id>/delete/", views.gallery_delete, name="gallery_delete"),

    # Licenses
    path("licenses/", views.license_list_create, name="licenses"),
    path("licenses/<int:license_id>/delete/", views.license_delete, name="license_delete"),
    path("help/", views.help_faq, name="help_faq"),


    # email verification
    path("verification-sent/", views.verification_sent, name="verification_sent"),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),

    # 🔐 Forgot password
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/emails/password_reset_email.txt",
            subject_template_name="users/emails/password_reset_subject.txt",
            success_url="/password-reset/done/"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/reset/done/"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # Call out fee
    path("account/callout-fee/", views.edit_callout_fee, name="edit_callout_fee"),
    
    #  delete accoutn
    path("account/delete/", views.delete_account, name="delete_account"),
]
