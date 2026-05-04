from django.shortcuts import render, redirect
from django.http import HttpResponse as hp, JsonResponse
from .forms import *
from django.contrib import messages
from django.contrib.auth import logout, get_user_model,authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from services.models import SubCategory, ServiceCategory
from .models import *
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from .utils import get_service_area_limit, get_gallery_photo_limit
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.templatetags.static import static
from django.contrib import messages
from .utils import send_verification_email
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from services.models import ServiceCategory, SubCategory
from analytics.utils import log_event
User = get_user_model()

# home page
def index(request):
    quick_categories = (
        ServiceCategory.objects
        .order_by("?")[:6]   # 👈 random 6 every load
    )

    context = {
        "quick_categories": quick_categories,
    }
    return render(request, "users/index.html", context)

# about us
def about(request):
    """
    Renders the About Us page for HandymenHub.
    """
    return render(request, "users/about.html")

# register 
def register(request):
    # ✅ Already logged in? Redirect home
    if request.user.is_authenticated:
        return redirect("users:index")

    form = UserRegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()

            user.is_active = False
            user.save(update_fields=["is_active"])

            send_verification_email(request, user)

            messages.success(
                request,
                "Account created! Please check your email and verify your account."
            )
            return redirect("users:verification_sent")

        messages.error(request, "Please fix the errors below.")

    return render(request, "users/register.html", {"form": form})


# user profile page
@login_required
def profile(request):
    user = request.user
    profile = getattr(user, "profile", None)
    user_services = (
        UserService.objects
        .select_related("category", "subcategory")
        .filter(user=user)
    )

    user_service_areas = ServiceArea.objects.filter(userservicearea__user=user)

    context = {
        "user_obj": user,
        "profile": profile,
        "user_services": user_services,
        "user_has_services": user_services.exists(),
        "user_service_areas": user_service_areas,
    }
    return render(request, "users/profile.html", context)


@login_required
def logmeout(request):
    logout(request)
    messages.success(request,f"You have been logout of of this app")
    return redirect("users:index")

# this adds user services
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from analytics.utils import log_event
from .models import UserService, ServiceCategory


@login_required
def add_user_services(request):
    user = request.user
    max_services = 10

    user_services = (
        UserService.objects
        .select_related("category", "subcategory")
        .filter(user=user)
    )

    categories = ServiceCategory.objects.prefetch_related("subcategories")

    if request.method == "POST":
        category_id = request.POST.get("category")
        selected_services = request.POST.getlist("services")

        if not category_id:
            messages.error(request, "Please select a category.")
            return redirect("users:add_user_services")

        if not selected_services:
            messages.error(request, "Please select at least one service.")
            return redirect("users:add_user_services")

        category = get_object_or_404(ServiceCategory, id=category_id)

        existing_count = user.services.count()
        remaining_slots = max_services - existing_count

        if remaining_slots <= 0:
            messages.error(
                request,
                f"You have already added the maximum of {max_services} services."
            )
            return redirect("users:add_user_services")

        services_to_add = selected_services[:remaining_slots]

        added_count = 0
        skipped_count = 0

        for sub_id in services_to_add:
            service, created = UserService.objects.get_or_create(
                user=user,
                category=category,
                subcategory_id=sub_id
            )

            if created:
                added_count += 1

                log_event(
                    user=request.user,
                    event_type="service.added",
                    instance=service,
                    description=f"Added service {service.subcategory.name}",
                    new_data={
                        "category": service.category.name,
                        "subcategory": service.subcategory.name,
                    },
                    request=request
                )
            else:
                skipped_count += 1

        if added_count > 0:
            messages.success(
                request,
                f"{added_count} service(s) added successfully."
            )

        if skipped_count > 0:
            messages.warning(
                request,
                f"{skipped_count} selected service(s) were already on your profile and were skipped."
            )

        if len(selected_services) > remaining_slots:
            messages.warning(
                request,
                f"Only {remaining_slots} service(s) were added. "
                f"Free accounts can have a maximum of {max_services} services."
            )

        if added_count == 0 and skipped_count == 0:
            messages.error(request, "No services were added.")

        return redirect("users:profile")

    context = {
        "user_obj": user,
        "user_services": user_services,
        "categories": categories,
        "max_services": max_services,
        "current_count": user.services.count(),
    }

    return render(request, "users/userservices.html", context)


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        # get original DB values BEFORE binding form changes
        original_profile = type(profile).objects.get(pk=profile.pk)

        old_data = {
            "business_name": original_profile.user_business_name,
            "bio": original_profile.profile_summary,
        }

        form = EditProfileForm(request.POST, instance=profile)

        if form.is_valid():
            updated_profile = form.save()

            new_data = {
                "business_name": updated_profile.user_business_name,
                "bio": updated_profile.profile_summary,
            }

            if old_data != new_data:
                log_event(
                    user=request.user,
                    event_type="profile.updated",
                    instance=updated_profile,
                    description="Profile updated",
                    old_data=old_data,
                    new_data=new_data,
                    request=request
                )

            messages.success(request, "Profile updated successfully.")
            return redirect("users:profile")
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = EditProfileForm(instance=profile)

    return render(request, "users/edit_profile.html", {
        "form": form
    })

#  this is the delete confirmation view

@login_required
def delete_user_service(request, service_id):
    try:
        # Try to get the service belonging to the current user
        service = UserService.objects.get(id=service_id, user=request.user)
    except UserService.DoesNotExist:
        messages.error(request, "You do not have permission to delete this service.")
        # Redirect safely to their service list
        return redirect("users:userservice")

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service removed successfully.")
        return redirect("users:userservice")


    log_event(
    user=request.user,
    event_type="service.deleted",
    instance=service,
    description="Service deleted",
    old_data={
        "category": service.category.name,
        "subcategory": service.subcategory.name,
    },
    request=request
)
    # Optional: if you want a confirmation page
    return render(request, "users/delete_user_service.html", {"service": service})


@login_required
def edit_profile_picture(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated.")
            return redirect("users:profile")
        messages.error(request, "There was an error updating your profile picture. Please try again.")
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, "users/edit_profile_picture.html", {"form": form, "profile": profile})


# this edits the contact information
@login_required
def edit_contact_info(request):
    profile = request.user.profile  # existing DB record

    if request.method == "POST":
        form = EditContactForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact information updated successfully.")
            return redirect("users:profile")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # ✅ THIS is what prefills the form
        form = EditContactForm(instance=profile)

    return render(
        request,
        "users/edit_contact_info.html",
        {"form": form},
    )
        


@login_required
def edit_address_info(request):
    profile = request.user.profile  # OneToOneField ensures this exists
    
    if request.method == 'POST':
        form = EditAddressForm(request.POST, instance=profile)
        # form = EditContactAddressForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your address information has been updated successfully!")
            return redirect('users:profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else :
        form = EditAddressForm( instance=profile)  

    return render(request, 'users/edit_address_info.html', {'form': form})


# contact us page
def contactus(request):
    return render(request,"users/contactus.html")


@login_required
def edit_service_areas(request):
    user = request.user
    service_area_limit = get_service_area_limit(user)

    # ✅ Handle POST: Save selected service areas
    if request.method == "POST":
        selected_ids = request.POST.getlist("service_areas")  # ✅ MUST be getlist for checkboxes

        # Server-side limit enforcement
        if len(selected_ids) > service_area_limit:
            messages.error(request, f"You can only select up to {service_area_limit} service areas.")
            return redirect("users:edit_service_areas")

        # Replace selections (simple + reliable)
        UserServiceArea.objects.filter(user=user).delete()
        UserServiceArea.objects.bulk_create([
            UserServiceArea(user=user, service_area_id=int(area_id))
            for area_id in selected_ids
        ])

        messages.success(request, "Service areas saved successfully.")
        return redirect("users:edit_service_areas")  # or redirect("users:profile")

    # ✅ GET: render page
    all_areas = ServiceArea.objects.filter(is_active=True).order_by("metro_city", "city", "name")

    distinct_provinces = (
        ServiceArea.objects
        .filter(is_active=True)
        .values_list("province", flat=True)
        .distinct()
        .order_by("province")
    )

    selected_area_objects = ServiceArea.objects.filter(
        userservicearea__user=user
    ).order_by("metro_city", "city", "name")

    selected_ids_current = set(selected_area_objects.values_list("id", flat=True))

    context = {
        "all_areas": all_areas,
        "selected_areas": list(selected_ids_current),  # used by template checked logic
        "selected_area_objects": selected_area_objects,
        "service_area_limit": service_area_limit,
        "distinct_provinces": distinct_provinces,
    }

    return render(request, "users/edit_service_areas.html", context)

@login_required
def delete_service_area_confirm(request, area_id):
    """
    Confirm + remove a service area from THIS user only.
    """
    link = get_object_or_404(UserServiceArea, user=request.user, service_area_id=area_id)

    if request.method == "POST":
        link.delete()
        messages.success(request, "Service area removed.")
        return redirect("users:edit_service_areas")

    return render(request, "users/confirm_delete_service_area.html", {"area": link})

# search and find a service
def find_service(request):
    categories = ServiceCategory.objects.order_by("name")
    subcategories = SubCategory.objects.select_related("category").order_by("name")

    service_areas = ServiceArea.objects.filter(is_active=True).order_by("province", "city")

    provinces = (
        service_areas
        .values_list("province", flat=True)
        .distinct()
        .order_by("province")
    )

    cities = (
        service_areas
        .values("city", "province")
        .distinct()
        .order_by("city")
    )

    selected_category = request.GET.get("category")
    selected_subcategory = request.GET.get("subcategory")
    selected_province = request.GET.get("province")
    selected_city = request.GET.get("city")

    context = {
        "categories": categories,
        "subcategories": subcategories,
        "provinces": provinces,
        "cities": cities,
        "selected_category": selected_category,
        "selected_subcategory": selected_subcategory,
        "selected_province": selected_province,
        "selected_city": selected_city,
    }
    return render(request, "users/find_service.html", context)


# API view

def api_find_service(request):
    category_id = (request.GET.get("category") or "").strip()
    subcategory_id = (request.GET.get("subcategory") or "").strip()
    province = (request.GET.get("province") or "").strip()
    city = (request.GET.get("city") or "").strip()

    qs = (
        UserProfile.objects
        .select_related("user")
        .filter(account_type__iexact="tradesperson")
        .filter(user__services__isnull=False)
    )

    if category_id.isdigit():
        qs = qs.filter(user__services__category_id=int(category_id))

    if subcategory_id.isdigit():
        qs = qs.filter(user__services__subcategory_id=int(subcategory_id))

    if province:
        qs = qs.filter(
            Q(user_province__iexact=province) |
            Q(user__user_service_areas__service_area__province__iexact=province)
        )

    if city:
        qs = qs.filter(
            Q(user_city__iexact=city) |
            Q(user__user_service_areas__service_area__city__iexact=city)
        )

    qs = qs.distinct()
    total = qs.count()

    category_obj = None
    subcategory_obj = None

    if category_id.isdigit():
        category_obj = ServiceCategory.objects.filter(id=int(category_id)).first()

    if subcategory_id.isdigit():
        subcategory_obj = SubCategory.objects.filter(id=int(subcategory_id)).first()

    SearchAnalytics.objects.create(
        category=category_obj,
        subcategory=subcategory_obj,
        province=province,
        city=city,
        results_count=total,
        user=request.user if request.user.is_authenticated else None,
    )

    results = []
    for p in qs[:60]:
        img_url = p.user_profile_image.url if p.user_profile_image else ""

        results.append({
            "profile_id": p.user_id,
            "name": f"{p.user_firstname} {p.user_last_name}".strip(),
            "business_name": p.user_business_name or "",
            "city": p.user_city or "",
            "province": p.get_user_province_display() if p.user_province else "",
            "summary": p.profile_summary or "",
            "image": img_url,
            "created_at": p.user.date_joined.isoformat(),
        })

    return JsonResponse({ "count": total, "results": results, })

# user profile detail shown to public
def profile_detail(request, user_id):
    from .utils import increment_profile_metric
    

    """
    Public tradesperson profile page.
    Read-only. Accessible by anyone.
    """

    user = get_object_or_404(
        User.objects.select_related("profile"),
        id=user_id,
        profile__account_type="tradesperson",
    )

    profile = user.profile
    increment_profile_metric(profile, "profile_views")
    try:
        callout_settings = user.callout_settings
    except CallOutFeeSettings.DoesNotExist:
        callout_settings = None

    # Services offered
    services = (
        UserService.objects
        .select_related("category", "subcategory")
        .filter(user=user)
        .order_by("category__name", "subcategory__name")
    )

    # Service areas
    service_areas = (
        ServiceArea.objects
        .filter(userservicearea__user=user, userservicearea__is_active=True, is_active=True)
        .distinct()
        .order_by("city", "name")
    )

    # Gallery
    gallery = (
        TradeWorkPhoto.objects
        .filter(user=user)
        .order_by("-created_at")[:18]
    )

    # Public licenses
    licenses = (
        License.objects
        .select_related("province")
        .filter(profile=profile, public_visibility=True)
        .order_by("-created_at")
    )

    # Public achievements
    achievements = (
        profile.achievements
        .filter(public_visibility=True)
        .order_by("-created_at")
    )

    context = {
        "user_obj": user,
        "profile": profile,
        "services": services,
        "service_areas": service_areas,
        "gallery": gallery,
        "licenses": licenses,
        "achievements": achievements,
        "callout_settings": callout_settings,
    }

    return render(request, "users/profile_detail.html", context)

# ###########Gallery views ####################

@login_required
def gallery_list(request):
    photos = TradeWorkPhoto.objects.filter(user=request.user)
    return render(request, "users/gallery_list.html", {"photos": photos})

@login_required
def gallery_add(request):
    limit = get_gallery_photo_limit(request.user)
    current = TradeWorkPhoto.objects.filter(user=request.user).count()

    # ✅ hard limit
    if current >= limit:
        messages.error(request, f"You’ve reached your gallery limit ({limit} photos).")
        return redirect("users:gallery_list")

    if request.method == "POST":
        form = TradeWorkPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            messages.success(request, "Photo added to your gallery.")
            return redirect("users:gallery_list")
        messages.error(request, "Please fix the errors below.")
    else:
        form = TradeWorkPhotoForm()

    return render(request, "users/gallery_form.html", {
        "form": form,
        "mode": "add",
        "limit": limit,
        "current": current,
        "remaining": max(limit - current, 0),
    })

@login_required
def gallery_edit(request, photo_id):
    photo = get_object_or_404(TradeWorkPhoto, id=photo_id, user=request.user)

    if request.method == "POST":
        form = TradeWorkPhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery photo updated.")
            return redirect("users:gallery_list")
        messages.error(request, "Please fix the errors below.")
    else:
        form = TradeWorkPhotoForm(instance=photo)

    return render(request, "users/gallery_form.html", {"form": form, "mode": "edit", "photo": photo})

@login_required
def gallery_delete(request, photo_id):
    photo = get_object_or_404(TradeWorkPhoto, id=photo_id, user=request.user)

    if request.method == "POST":
        photo.delete()
        messages.success(request, "Photo removed from your gallery.")
        return redirect("users:gallery_list")

    return render(request, "users/gallery_delete_confirm.html", {"photo": photo})


@login_required
def license_list_create(request):
    """
    List all licenses for the logged-in tradesperson
    + allow adding a new license
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    licenses = profile.licenses.all()

    if request.method == "POST" and profile.licenses.count() >= 5:
        messages.error(request, "You can add a maximum of 5 licenses.")
        return redirect("users:licenses")
    
    elif request.method == "POST":
        form = LicenseForm(request.POST, request.FILES)
        if form.is_valid():
            license_obj = form.save(commit=False)
            license_obj.profile = profile
            license_obj.save()

            messages.success(request, "License added successfully.")
            return redirect("users:licenses")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LicenseForm()

    return render(
        request,
        "users/licenses.html",
        {
            "form": form,
            "licenses": licenses,
        },
    )


@login_required
def license_delete(request, license_id):
    """
    Delete a license owned by the logged-in user
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    license_obj = get_object_or_404(License, id=license_id, profile=profile)

    if request.method == "POST":
        license_obj.delete()
        messages.success(request, "License removed.")
        return redirect("users:licenses")

    return render(
        request,
        "users/license_confirm_delete.html",
        {"license": license_obj},
    )

# help F&Q page
def help_faq(request):
    return render(request, "users/help_faq.html")


def verification_sent(request):
    return render(request, "users/verification_sent.html")


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Optional if you have profile.email_verified
        if hasattr(user, "profile"):
            try:
                user.profile.email_verified = True
                user.profile.save()
            except Exception:
                pass

        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect("users:login")  # make sure this url name exists

    messages.error(request, "Verification link is invalid or expired. Please request a new one.")
    return redirect("users:resend_verification")


def resend_verification(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, "No account found with that email.")
            return redirect("users:resend_verification")

        if user.is_active:
            messages.info(request, "Your email is already verified. Please log in.")
            return redirect("users:login")

        send_verification_email(request, user)
        messages.success(request, "Verification email resent. Please check your inbox.")
        return redirect("users:verification_sent")

    return render(request, "users/resend_verification.html")




@login_required
def edit_callout_fee(request):
    obj, _ = CallOutFeeSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = CallOutFeeSettingsForm(request.POST, instance=obj)
        if form.is_valid():
            saved = form.save(commit=False)

            # If disabled, ensure amount is cleared (clean() tries, but double safe)
            if not saved.enabled:
                saved.amount = None

            saved.save()
            messages.success(request, "Call-out fee settings updated.")
            return redirect(reverse("users:profile"))  # change to your profile url name
    else:
        form = CallOutFeeSettingsForm(instance=obj)

    return render(request, "users/edit_callout_fee.html", {"form": form})



@login_required
def delete_account(request):
    user = request.user

    if request.method == "POST":
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]

            # Confirm password before deleting
            if not check_password(password, user.password):
                messages.error(request, "Incorrect password. Please try again.")
                return render(request, "users/account_delete_confirm.html", {"form": form})

            # Log out first (good practice)
            logout(request)

            # Delete user
            user.delete()

            messages.success(request, "Your account has been deleted successfully.")
            return redirect("users:index")  # or your home page name

    else:
        form = DeleteAccountForm()

    return render(request, "users/account_delete_confirm.html", {"form": form})


# this redirect a newly created profile to complete profile info
@login_required
def post_login(request):
    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Only guide tradespeople
    if profile.account_type != UserProfile.TYPE_TRADESPERSON:
        return redirect("users:index")

    # Determine what’s missing (basic)
    missing = []

    # photo: detect default
    if not profile.user_profile_image or str(profile.user_profile_image).endswith("no_profile_picture.jpg"):
        missing.append("photo")

    if not (profile.profile_summary and profile.profile_summary.strip()):
        missing.append("summary")

    if not request.user.services.exists():
        missing.append("services")

    if not request.user.user_service_areas.filter(is_active=True).exists():
        missing.append("areas")

 
    if "summary" in missing:
        return redirect("users:edit_profile")  # if summary is edited there; otherwise change to edit_contact_info
    if "services" in missing:
        return redirect("users:userservice")
    if "areas" in missing:
        return redirect("users:edit_service_areas")

    return redirect("users:profile")

@login_required
def edit_achievements(request):
    profile = request.user.profile

    if request.method == "POST":
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.profile = profile
            achievement.save()
            messages.success(request, "Achievement added successfully.")
            return redirect("users:edit_achievements")
    else:
        form = AchievementForm()

    achievements = profile.achievements.all().order_by("-created_at")

    context = {
        "form": form,
        "achievements": achievements,
    }
    return render(request, "users/edit_achievements.html", context)


@login_required
def delete_achievement_confirm(request, achievement_id):
    achievement = get_object_or_404(
        Achievement,
        id=achievement_id,
        profile=request.user.profile
    )

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement deleted successfully.")
        return redirect("users:edit_achievements")

    return render(
        request,
        "users/confirm_delete_achievement.html",
        {"achievement": achievement}
    )


# #####Legal section ######
# this is the terms 
def terms_of_service(request):
    return render(request, "legal/terms.html")

def privacy_policy(request):
    return render(request, "legal/privacy.html")


CURRENT_TERMS_VERSION = "v1"
CURRENT_PRIVACY_VERSION = "v1"


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def register(request):
    # Already logged in? Redirect home
    if request.user.is_authenticated:
        return redirect("users:index")

    form = UserRegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()

            # keep user inactive until email verification
            user.is_active = False
            user.save(update_fields=["is_active"])

            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Save proof of legal acceptance
            LegalAcceptance.objects.create(
                user=user,
                document_type=LegalAcceptance.DOCUMENT_TERMS,
                document_version=CURRENT_TERMS_VERSION,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            LegalAcceptance.objects.create(
                user=user,
                document_type=LegalAcceptance.DOCUMENT_PRIVACY,
                document_version=CURRENT_PRIVACY_VERSION,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            send_verification_email(request, user)

            messages.success(
                request,
                "Account created! Please check your email and verify your account."
            )
            return redirect("users:verification_sent")

        messages.error(request, "Please fix the errors below.")

    return render(request, "users/register.html", {"form": form})