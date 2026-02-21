from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CallOutFeeSettings, UserProfile
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate

User = get_user_model()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Create profile safely (avoid duplicates)
    profile, _ = UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            "user_firstname": instance.first_name or "",
            "user_last_name": instance.last_name or "",
            "user_preferred_name": instance.username or "",
            "tier": UserProfile.TIER_FREE,
            # ✅ default account type (you can change default later)
            "account_type": UserProfile.TYPE_TRADESPERSON,
        }
    )


@receiver(post_save, sender=User)
def create_callout_settings(sender, instance, created, **kwargs):
    if created:
        CallOutFeeSettings.objects.get_or_create(user=instance)

# #############user service area


SERVICE_AREAS = [
    # ---------- Alberta ----------
    ("AB", "Calgary", "Canada", True, "Calgary", "Calgary"),
    ("AB", "Airdrie", "Canada", True, "Calgary", "Airdrie"),
    ("AB", "Edmonton", "Canada", True, "Edmonton", "Edmonton"),
    ("AB", "Leduc", "Canada", True, "Edmonton", "Leduc"),
    ("AB", "Red Deer", "Canada", True, "Red Deer", "Red Deer"),
    ("AB", "Lethbridge", "Canada", True, "Lethbridge", "Lethbridge"),
    ("AB", "Grande Prairie", "Canada", True, "Grande Prairie", "Grande Prairie"),
    ("AB", "Medicine Hat", "Canada", True, "Medicine Hat", "Medicine Hat"),
    ("AB", "Fort McMurray", "Canada", True, "Fort McMurray", "Fort McMurray"),
    ("AB", "Spruce Grove", "Canada", True, "Edmonton", "Spruce Grove"),

    # ---------- British Columbia ----------
    ("BC", "Vancouver", "Canada", True, "Vancouver", "Vancouver"),
    ("BC", "Victoria", "Canada", True, "Victoria", "Victoria"),
    ("BC", "Surrey", "Canada", True, "Vancouver", "Surrey"),
    ("BC", "Burnaby", "Canada", True, "Vancouver", "Burnaby"),
    ("BC", "Richmond", "Canada", True, "Vancouver", "Richmond"),
    ("BC", "Kelowna", "Canada", True, "Kelowna", "Kelowna"),
    ("BC", "Abbotsford", "Canada", True, "Vancouver", "Abbotsford"),

    # ---------- Manitoba ----------
    ("MB", "Winnipeg", "Canada", True, "Winnipeg", "Winnipeg"),
    ("MB", "Brandon", "Canada", True, "Brandon", "Brandon"),

    # ---------- New Brunswick ----------
    ("NB", "Fredericton", "Canada", True, "Fredericton", "Fredericton"),
    ("NB", "Moncton", "Canada", True, "Moncton", "Moncton"),
    ("NB", "Saint John", "Canada", True, "Saint John", "Saint John"),

    # ---------- Newfoundland & Labrador ----------
    ("NL", "St. John's", "Canada", True, "St. John's", "St. John's"),

    # ---------- Nova Scotia ----------
    ("NS", "Halifax", "Canada", True, "Halifax", "Halifax"),

    # ---------- Ontario ----------
    ("ON", "Toronto", "Canada", True, "Toronto", "Toronto"),
    ("ON", "Ottawa", "Canada", True, "Ottawa", "Ottawa"),
    ("ON", "Mississauga", "Canada", True, "Toronto", "Mississauga"),
    ("ON", "Brampton", "Canada", True, "Toronto", "Brampton"),
    ("ON", "Hamilton", "Canada", True, "Hamilton", "Hamilton"),
    ("ON", "London", "Canada", True, "London", "London"),
    ("ON", "Kitchener", "Canada", True, "Kitchener", "Kitchener"),
    

    # ---------- PEI ----------
    ("PE", "Charlottetown", "Canada", True, "Charlottetown", "Charlottetown"),

    # ---------- Quebec ----------
    ("QC", "Montreal", "Canada", True, "Montreal", "Montreal"),
    ("QC", "Quebec City", "Canada", True, "Quebec City", "Quebec City"),
    ("QC", "Laval", "Canada", True, "Montreal", "Laval"),
    ("QC", "Gatineau", "Canada", True, "Ottawa", "Gatineau"),

    # ---------- Saskatchewan ----------
    ("SK", "Regina", "Canada", True, "Regina", "Regina"),
    ("SK", "Saskatoon", "Canada", True, "Saskatoon", "Saskatoon"),

    # ---------- Territories ----------
    ("NT", "Yellowknife", "Canada", True, "Yellowknife", "Yellowknife"),
    ("NU", "Iqaluit", "Canada", True, "Iqaluit", "Iqaluit"),
    ("YT", "Whitehorse", "Canada", True, "Whitehorse", "Whitehorse"),
]


@receiver(post_migrate)
def seed_service_areas(sender, **kwargs):
    if sender.name != "users":
        return

    from .models import ServiceArea

    for province, city, country, is_active, metro_city, name in SERVICE_AREAS:
        ServiceArea.objects.get_or_create(
            province=province,
            city=city,
            country=country,
            defaults={
                "is_active": is_active,
                "metro_city": metro_city,
                "name": name,
            },
        )
