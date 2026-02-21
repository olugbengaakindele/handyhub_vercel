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


# this adds services to a user
@login_required
def add_user_services(request):
    # 🔐 Security: users can only edit their own services
    # if request.user.id != userid:
    #     return redirect("users:profile", request.user.id)
    user = request.user

    user_services = (
        UserService.objects
        .select_related("category", "subcategory")
        .filter(user=user)
    )

    categories = ServiceCategory.objects.prefetch_related("subcategories")

    if request.method == "POST":
        category_id = request.POST.get("category")
        selected_services = request.POST.getlist("services")

        if not category_id or not selected_services:
            messages.error(request, "Please select a category and at least one service.")
            return redirect("users:profile", user.id)

        category = get_object_or_404(ServiceCategory, id=category_id)

        existing_count = user.services.count()
        remaining_slots = 5 - existing_count

        if remaining_slots <= 0:
            messages.error(
                request,
                "You have already added the maximum of 5 services."
            )
            return redirect("users:profile")

        # Only allow adding up to remaining slots
        services_to_add = selected_services[:remaining_slots]

        for sub_id in services_to_add:
            UserService.objects.get_or_create(
                user=user,
                category=category,
                subcategory_id=sub_id
            )

        if len(selected_services) > remaining_slots:
            messages.warning(
                request,
                f"Only {remaining_slots} service(s) were added. "
                "Free accounts can have a maximum of 5 services."
            )

        return redirect("users:profile")

    context = {
        "user_obj": user,
        "user_services": user_services,
        "categories": categories,
        "max_services": 5,
        "current_count": user.services.count(),
    }

    return render(request, "users/userservices.html", context)

@login_required
def edit_profile(request):
    profile = request.user.profile  # guaranteed by signal

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
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

    # Optional: if you want a confirmation page
    return render(request, "users/delete_user_service.html", {"service": service})


@login_required
def edit_profile_picture(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfilePictureForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect("users:profile" )
        else:
            messages.error(
                request,
                "There was an error updating your profile picture. Please try again."
            )

    else:
        form = ProfilePictureForm(instance=profile)

    return render( request,"users/edit_profile_picture.html",
        {
            "form": form,
            "profile": profile
        }
    )

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



def contactus(request):
    return render(request,"users/contactus.html")



@login_required
def edit_service_areas(request):
    user = request.user
    service_area_limit = get_service_area_limit(user)

    # All possible areas (for checkbox selection)
    all_areas = ServiceArea.objects.filter(is_active=True).order_by("metro_city", "city", "name")

    # User's currently selected areas (via reverse relation name in error choices: userservicearea)
    selected_area_objects = ServiceArea.objects.filter(userservicearea__user=user).order_by("metro_city", "city", "name")
    selected_ids_current = set(selected_area_objects.values_list("id", flat=True))

    if request.method == "POST":
        selected_ids_post = request.POST.getlist("service_areas")
        selected_ids_post = [int(x) for x in selected_ids_post if x.isdigit()]

        # ✅ Enforce free tier max
        if len(selected_ids_post) > service_area_limit:
            messages.error(
                request,
                f"Free tier users can only select up to {service_area_limit} service areas."
            )
            # Re-render page with current context (don’t save)
            return render(
                request,
                "users/edit_service_areas.html",
                {
                    "all_areas": all_areas,
                    "selected_areas": selected_ids_post,  # show what they tried
                    "selected_area_objects": selected_area_objects,
                    "service_area_limit": service_area_limit,
                },
            )

        # Save selections: wipe and recreate links
        with transaction.atomic():
            UserServiceArea.objects.filter(user=user).delete()

            links = [
                UserServiceArea(user=user, service_area_id=area_id, is_active=True)
                for area_id in selected_ids_post
            ]
            UserServiceArea.objects.bulk_create(links)

        messages.success(request, "Your service areas have been updated.")
        return redirect("users:edit_service_areas")

    # GET context
    context = {
        "all_areas": all_areas,
        "selected_areas": list(selected_ids_current),        # for checkbox checked state
        "selected_area_objects": selected_area_objects,      # for list below
        "service_area_limit": service_area_limit,
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

#  serach and find a service
def find_service(request):
    categories = ServiceCategory.objects.order_by("name")
    subcategories = SubCategory.objects.select_related("category").order_by("name")

    cities = (
        ServiceArea.objects.filter(is_active=True)
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")
    )

    selected_category = request.GET.get("category")
    selected_subcategory = request.GET.get("subcategory")
    selected_city = request.GET.get("city")

    context = {
        "categories": categories,
        "subcategories": subcategories,
        "cities": cities,
        "selected_category": selected_category,
        "selected_subcategory": selected_subcategory,
        "selected_city": selected_city,
    }
    return render(request, "users/find_service.html", context)


#  API view
def api_find_service(request):
    category_id = (request.GET.get("category") or "").strip()
    subcategory_id = (request.GET.get("subcategory") or "").strip()
    city = (request.GET.get("city") or "").strip()

    qs = (
        UserProfile.objects
        .select_related("user")
        .filter(account_type__iexact="tradesperson")
        .filter(user__services__isnull=False)  # ✅ must have at least one service
    )

    if category_id.isdigit():
        qs = qs.filter(user__services__category_id=int(category_id))

    if subcategory_id.isdigit():
        qs = qs.filter(user__services__subcategory_id=int(subcategory_id))

    # ✅ CITY FILTER — FIXED
    if city:
        qs = qs.filter(
            Q(user_city__iexact=city) |
            Q(user__user_service_areas__service_area__city__iexact=city)
        )

    qs = qs.distinct()
    total = qs.count()

    results = []
    for p in qs[:60]:
        img_url = p.user_profile_image.url if p.user_profile_image else ""

        results.append({
            "profile_id": p.user_id,
            "name": f"{p.user_firstname} {p.user_last_name}".strip(),
            "business_name": p.user_business_name or "",
            "city": p.user_city or "",
            "province": str(getattr(p, "user_province", "") or ""),
            "summary": getattr(p, "profile_summary", "") or "",
            "image": img_url,
        })

    return JsonResponse({"count": total, "results": results})

# user profile detail shown to public
def profile_detail(request, user_id):
    """
    Public tradesperson profile page.
    Read-only. Accessible by anyone.
    """

    user = get_object_or_404(
        User.objects.select_related("profile"),
        id=user_id,
        profile__account_type="tradesperson",
    )

    try:
        callout_settings = user.callout_settings
    except CallOutFeeSettings.DoesNotExist:
        callout_settings = None

    profile = user.profile

    # Services offered by this tradesperson
    services = (
        UserService.objects
        .select_related("category", "subcategory")
        .filter(user=user)
        .order_by("category__name", "subcategory__name")
    )

    # ✅ Service areas (robust way):
    # If you have a through table like UserServiceArea, the safest is to query via that model
    # BUT since we don't have it here, we can still make your existing query safer by:
    # - using distinct()
    # - not assuming ordering fields exist (metro_city/city/name)
    service_areas = (
        ServiceArea.objects
        .filter(userservicearea__user=user, is_active=True)  # keep, but see note below
        .distinct()
        .order_by("city")  # keep simple; change if your fields differ
    )

    # ✅ Gallery (add this)
    # Replace ProfileGalleryImage with your actual gallery model & field names.
    gallery = (
        TradeWorkPhoto.objects
        .filter(user=user)               # or filter(profile=profile) depending on your model
        .order_by("-created_at")[:18]    # cap to keep the page fast
    )

    context = {
        "user_obj": user,
        "profile": profile,
        "services": services,
        "service_areas": service_areas,
        "gallery": gallery,
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