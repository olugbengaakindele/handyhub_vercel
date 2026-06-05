# services/signals.py
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

DEFAULT_CATEGORIES = [
    "Basement Development",
    "Renovation & Remodeling",
    "Carpentry",
    "Plumbing",
    "Electrical",
    "HVAC & Refrigeration",
    "Drywall & Insulation",
    "Painting",
    "Flooring & Tile",
    "Roofing",
    "Concrete & Masonry",
    "Landscaping & Gardening",
    "Snow Removal",
    "Cleaning",
    "Pest Control",
    "Windows, Doors & Glass",
    "Fencing & Decks",
    "Appliance Repair",
    "Security & Smart Home",
    "Handyman Services",
]

DEFAULT_SUBCATEGORIES = {
    "Basement Development": [
        "Full Basement Development",
        "Basement Framing",
        "Basement Drywall",
        "Basement Bathroom Installation",
        "Basement Flooring",
        "Basement Electrical",
        "Basement Plumbing",
        "Basement Insulation",
        "Basement Legal Suite Preparation",
        "Basement Renovation",
    ],

    "Renovation & Remodeling": [
        "Kitchen Renovation",
        "Bathroom Renovation",
        "Home Remodeling",
        "Interior Renovation",
        "Garage Renovation",
        "Laundry Room Renovation",
        "Permit-Ready Renovation Support",
    ],

    "Carpentry": [
        "Framing",
        "Trim & Baseboards",
        "Cabinet Installation",
        "Custom Shelving",
        "Door Installation",
        "Stair Repair",
        "Finish Carpentry",
    ],

    "Plumbing": [
        "Leak Repair",
        "Drain Cleaning",
        "Toilet Installation",
        "Faucet Installation",
        "Pipe Installation",
        "Water Heater Repair",
        "Sump Pump Installation",
        "Bathroom Plumbing",
        "Kitchen Plumbing",
    ],

    "Electrical": [
        "Light Fixture Installation",
        "Outlet Repair",
        "Switch Installation",
        "Panel Upgrade",
        "Basement Wiring",
        "EV Charger Installation",
        "Smoke Detector Installation",
        "Electrical Troubleshooting",
    ],

    "HVAC & Refrigeration": [
        "Furnace Repair",
        "Furnace Installation",
        "Air Conditioning Repair",
        "Air Conditioning Installation",
        "Duct Cleaning",
        "Thermostat Installation",
        "Humidifier Installation",
        "Refrigeration Repair",
    ],

    "Drywall & Insulation": [
        "Drywall Installation",
        "Drywall Repair",
        "Taping & Mudding",
        "Ceiling Repair",
        "Soundproofing",
        "Basement Insulation",
        "Attic Insulation",
    ],

    "Painting": [
        "Interior Painting",
        "Exterior Painting",
        "Fence Painting",
        "Deck Staining",
        "Cabinet Painting",
        "Wall Patching Before Painting",
    ],

    "Flooring & Tile": [
        "Vinyl Flooring",
        "Laminate Flooring",
        "Hardwood Flooring",
        "Carpet Installation",
        "Tile Installation",
        "Bathroom Tile",
        "Kitchen Backsplash",
        "Floor Repair",
    ],

    "Roofing": [
        "Roof Repair",
        "Roof Replacement",
        "Shingle Repair",
        "Flat Roofing",
        "Gutter Cleaning",
        "Gutter Installation",
        "Soffit & Fascia",
    ],

    "Concrete & Masonry": [
        "Concrete Repair",
        "Concrete Finishing",
        "Driveway Concrete",
        "Sidewalk Repair",
        "Brick Repair",
        "Stonework",
        "Foundation Crack Repair",
    ],

    "Landscaping & Gardening": [
        "Lawn Mowing",
        "Hedge Trimming",
        "Weeding",
        "Sod Installation",
        "Garden Bed Installation",
        "Tree & Shrub Planting",
        "Yard Cleanup",
        "Landscaping",
    ],

    "Snow Removal": [
        "Driveway Snow Removal",
        "Sidewalk Snow Removal",
        "Salting & De-icing",
        "Commercial Snow Removal",
    ],

    "Cleaning": [
        "House Cleaning",
        "Move-out Cleaning",
        "Office Cleaning",
        "Post-Construction Cleaning",
        "Deep Cleaning",
        "Carpet Cleaning",
        "Window Cleaning",
    ],

    "Pest Control": [
        "Rodent Control",
        "Insect Control",
        "Ant Control",
        "Wasp Nest Removal",
        "Bed Bug Treatment",
        "Wildlife Removal",
    ],

    "Windows, Doors & Glass": [
        "Window Installation",
        "Window Repair",
        "Door Installation",
        "Patio Door Installation",
        "Glass Repair",
        "Weather Sealing",
    ],

    "Fencing & Decks": [
        "Fence Installation",
        "Fence Repair",
        "Deck Building",
        "Deck Repair",
        "Deck Staining",
        "Railing Installation",
    ],

    "Appliance Repair": [
        "Washer Repair",
        "Dryer Repair",
        "Dishwasher Repair",
        "Fridge Repair",
        "Stove Repair",
        "Microwave Installation",
    ],

    "Security & Smart Home": [
        "Camera Installation",
        "Smart Lock Installation",
        "Doorbell Camera Installation",
        "Alarm System Installation",
        "Smart Thermostat Setup",
    ],

    "Handyman Services": [
        "General Repairs",
        "Furniture Assembly",
        "TV Mounting",
        "Shelving Installation",
        "Minor Plumbing",
        "Minor Electrical",
        "Caulking",
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