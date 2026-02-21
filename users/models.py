from django.db import models
from django.contrib.auth import get_user_model
from services.models import SubCategory, ServiceCategory
import uuid
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from .utils import get_gallery_max_upload_bytes
from django.utils import timezone


User = get_user_model()

def profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pictures', filename)


# this creates a user profile 
class UserProfile(models.Model):
    profile_summary = models.TextField(
        blank=True,
        null=True,
        max_length=1000,
        help_text="Short bio about your business, experience, and what you specialize in."
    )


    TYPE_TRADESPERSON = "tradesperson"
    TYPE_VISITOR = "visitor"

    ACCOUNT_TYPE_CHOICES = [
        (TYPE_TRADESPERSON, "Tradesperson"),
        (TYPE_VISITOR, "Visitor"),
    ]

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default=TYPE_TRADESPERSON,  # choose default you want
        db_index=True,
    )
    # 🔐 Subscription tiers
    TIER_FREE = "free"
    TIER_PRO = "pro"
    TIER_PREMIUM = "premium"

    TIER_CHOICES = [
        (TIER_FREE, "Free"),
        (TIER_PRO, "Pro"),
        (TIER_PREMIUM, "Premium"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # 🧾 Subscription / Plan
    tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        default=TIER_FREE
    )

    
    user_firstname = models.CharField(max_length=150)
    user_last_name = models.CharField(max_length=150)
    user_preferred_name = models.CharField(max_length=150)
    user_business_name = models.CharField(max_length=200, blank=True, null=True)
    user_profile_image = models.ImageField(
        default="no_profile_picture.jpg",
        upload_to=profile_image_path
    )

    # 📞 Contact phone numbers
    user_primary_phone = models.CharField(max_length=20, blank=True, null=True)
    user_secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    user_business_phone = models.CharField(max_length=20, blank=True, null=True)

    # 🏠 Address
    user_address_line1 = models.CharField("Address Line 1", max_length=255)
    user_address_line2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    user_city = models.CharField(max_length=100)
    user_province = models.CharField(
        max_length=50,
        choices=[
            ("AB", "Alberta"),
            ("BC", "British Columbia"),
            ("MB", "Manitoba"),
            ("NB", "New Brunswick"),
            ("NL", "Newfoundland and Labrador"),
            ("NS", "Nova Scotia"),
            ("NT", "Northwest Territories"),
            ("NU", "Nunavut"),
            ("ON", "Ontario"),
            ("PE", "Prince Edward Island"),
            ("QC", "Quebec"),
            ("SK", "Saskatchewan"),
            ("YT", "Yukon"),
        ]
    )
    user_postal_code = models.CharField(max_length=10)

    # 🌐 Website
    user_website = models.URLField(blank=True, null=True)

    # ⏱ Timestamps
    user_created_at = models.DateTimeField(auto_now_add=True)
    user_updated_at = models.DateTimeField(auto_now=True)
    last_seen_at = models.DateTimeField(null=True, blank=True, default=timezone.now)

    def __str__(self):
        return f"{self.user_preferred_name or self.user_firstname}"
    


class UserService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "services")
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "subcategory")  # prevents duplicates

    def __str__(self):
        return f"{self.user} - {self.subcategory.name}"
    


#  this houses all the provicne in canada

class Province(models.Model):
    code = models.CharField(max_length=2, unique=True)  # AB, ON, BC
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


#  this stores cities in canada
class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("province", "name")

    def __str__(self):
        return f"{self.name}, {self.province.code}"
    
#  user service areas
# class ServiceArea(models.Model):
#     COVERAGE_CHOICES = (
#         ("province", "Entire Province"),
#         ("cities", "Selected Cities"),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     province = models.ForeignKey(Province, on_delete=models.CASCADE)
#     coverage_type = models.CharField(max_length=10, choices=COVERAGE_CHOICES)

#     cities = models.ManyToManyField(City, blank=True)

#     def __str__(self):
#         return f"{self.user} - {self.province} ({self.coverage_type})"

class ServiceArea(models.Model):
    name = models.CharField(max_length=100)        # Calgary NW, Airdrie
    city = models.CharField(max_length=100)        # Airdrie, Calgary
    metro_city = models.CharField(max_length=100)  # Calgary, Edmonton
    province = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="Canada")
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["metro_city", "name"]

    def __str__(self):
        return f"{self.name} ({self.metro_city})"
    


class UserServiceArea(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_service_areas"
    )
    service_area = models.ForeignKey(
        ServiceArea,
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "service_area")

    def __str__(self):
        return f"{self.user} → {self.service_area}"


#  this begings the gallery model
def work_photo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # /media/work_gallery/user_12/<uuid>.jpg
    return os.path.join("work_gallery", f"user_{instance.user_id}", filename)

def validate_100_words(value):
    # "100 word" → enforce <= 100 words (simple + reliable)
    words = [w for w in (value or "").split() if w.strip()]
    if len(words) > 100:
        raise ValidationError("Description must be 100 words or less.")

MAX_GALLERY_IMAGE_BYTES = 1000 * 1024  # 500KB

def validate_gallery_image_size(file):
    if file and file.size > MAX_GALLERY_IMAGE_BYTES:
        raise ValidationError("Image must be 1MB or less.")


class TradeWorkPhoto(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_photos",
    )
    image = models.ImageField(upload_to=work_photo_upload_path, validators=[validate_gallery_image_size])
    description = models.TextField(
        blank=True,
        validators=[validate_100_words],
        help_text="Max 100 words."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Work photo {self.id} - user {self.user_id}"

# for license document
def license_upload_path(instance, filename):
    """
    Upload path:
    licenses/<user_id>/<uuid>.<ext>
    """
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(
        "licenses",
        str(instance.profile.user.id),
        filename
    )


class License(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_PENDING = "pending"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_PENDING, "Pending"),
    ]

    profile = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="licenses"
    )

    license_name = models.CharField(max_length=200)
    issuing_authority = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)

    province = models.ForeignKey(
        "users.Province",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    document = models.FileField(
        upload_to=license_upload_path,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    # Nice-to-have (added now)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    public_visibility = models.BooleanField(
        default=True,
        help_text="Show this license on your public profile"
    )

    # Still not verified (platform rule)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.license_name} ({self.get_status_display()})"
    

# Call out fee
class CallOutFeeSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="callout_settings"
    )

    enabled = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    note = models.CharField(
        max_length=200,
        blank=True,
        help_text="E.g. 'Applies to diagnosis/assessment. Waived if job is accepted.'"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Call-out fee ({self.user})"
    

