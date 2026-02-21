# services/signals.py
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

DEFAULT_CATEGORIES = [
    "Gardening",
    "Snow Plough",
    "Plumbing",
    "Electrical",
    "Painting",
    "Carpentry",
    "Cleaning",
    "Pest Control",
    "Roofing",
]

DEFAULT_SUBCATEGORIES = {
    "Gardening": [
        "Lawn Mowing",
        "Hedge Trimming",
        "Weeding",
        "Landscaping",
    ],
    "Snow Plough": [
        "Driveway Clearing",
        "Sidewalk Clearing",
        "Salting & De-icing",
    ],
    "Plumbing": [
        "Leak Repair",
        "Pipe Installation",
        "Drain Cleaning",
        "Water Heater Repair",
    ],
    "Electrical": [
        "Wiring",
        "Lighting Installation",
        "Panel Upgrade",
        "Outlet Repair",
    ],
    "Painting": [
        "Interior Painting",
        "Exterior Painting",
        "Fence Painting",
    ],
    "Carpentry": [
        "Framing",
        "Deck Building",
        "Cabinet Installation",
    ],
    "Cleaning": [
        "House Cleaning",
        "Move-out Cleaning",
        "Office Cleaning",
    ],
    "Pest Control": [
        "Rodent Control",
        "Insect Control",
        "Wildlife Removal",
    ],
    "Roofing": [
        "Roof Repair",
        "Roof Replacement",
        "Gutter Cleaning",
    ],
}


@receiver(post_migrate)
def seed_services(sender, **kwargs):
    if sender.name != "services":
        return

    from .models import ServiceCategory, SubCategory

    # --- seed categories ---
    categories = {}
    for name in DEFAULT_CATEGORIES:
        cat, _ = ServiceCategory.objects.get_or_create(name=name)
        categories[name] = cat

    # --- seed subcategories ---
    for category_name, subcats in DEFAULT_SUBCATEGORIES.items():
        category = categories.get(category_name)
        if not category:
            continue

        for sub_name in subcats:
            SubCategory.objects.get_or_create(
                category=category,
                name=sub_name
            )