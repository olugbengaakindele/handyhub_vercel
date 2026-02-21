from services.models import ServiceCategory, SubCategory

DATA = {

    # ⚡ ELECTRICAL
    "Electrical": [
        "Circuit Repair",
        "Lighting Installation",
        "Outlet Installation",
        "Switch Replacement",
        "Panel Upgrade",
        "Ceiling Fan Installation",
        "Smoke Detector Installation",
        "EV Charger Installation",
        "Outdoor Lighting",
        "Electrical Troubleshooting",
    ],

    # 🚰 PLUMBING
    "Plumbing": [
        "Leak Repair",
        "Drain Cleaning",
        "Toilet Installation",
        "Faucet Installation",
        "Water Heater Installation",
        "Sump Pump Installation",
        "Pipe Replacement",
        "Bathroom Plumbing",
        "Kitchen Plumbing",
        "Emergency Plumbing",
    ],

    # 🎨 PAINTING
    "Painting": [
        "Interior Painting",
        "Exterior Painting",
        "Drywall Repair",
        "Wallpaper Removal",
        "Trim & Baseboard Painting",
        "Fence Painting",
        "Deck Painting & Staining",
    ],

    # 🔨 HANDYMAN / GENERAL REPAIRS
    "Handyman": [
        "Furniture Assembly",
        "TV Mounting",
        "Door Repair",
        "Window Repair",
        "Drywall Patching",
        "Shelf Installation",
        "Picture Hanging",
        "Minor Home Repairs",
    ],

    # 🧹 CLEANING
    "Cleaning": [
        "Home Cleaning",
        "Deep Cleaning",
        "Move-out Cleaning",
        "Post-Construction Cleaning",
        "Office Cleaning",
        "Airbnb Cleaning",
        "Carpet Cleaning",
        "Window Cleaning",
    ],

    # 🚚 MOVING & LABOUR
    "Moving": [
        "Loading Help",
        "Unloading Help",
        "Heavy Lifting",
        "Apartment Moving",
        "Furniture Moving",
        "Packing Assistance",
    ],

    # 🌱 LAWN & YARD CARE
    "Lawn & Yard Care": [
        "Lawn Mowing",
        "Grass Cutting",
        "Hedge Trimming",
        "Weed Removal",
        "Leaf Removal",
        "Spring Cleanup",
        "Fall Cleanup",
        "Garden Maintenance",
    ],

    # ❄️ SNOW & WINTER SERVICES (VERY IMPORTANT FOR CANADA)
    "Snow & Ice Removal": [
        "Snow Plowing",
        "Snow Shoveling",
        "Driveway Clearing",
        "Sidewalk Clearing",
        "Ice Salting",
        "Commercial Snow Removal",
    ],

    # 🪚 CARPENTRY
    "Carpentry": [
        "Custom Shelving",
        "Deck Repair",
        "Fence Installation",
        "Framing",
        "Cabinet Installation",
        "Trim Carpentry",
    ],

    # 🧱 RENOVATION & REMODELING
    "Renovation": [
        "Kitchen Renovation",
        "Bathroom Renovation",
        "Basement Finishing",
        "Home Remodeling",
        "Tile Installation",
        "Flooring Installation",
    ],

    # 🪟 WINDOWS & DOORS
    "Windows & Doors": [
        "Window Installation",
        "Window Replacement",
        "Door Installation",
        "Door Replacement",
        "Sliding Door Repair",
    ],

    # 🏠 ROOFING & EXTERIOR
    "Roofing & Exterior": [
        "Roof Repair",
        "Shingle Replacement",
        "Gutter Cleaning",
        "Gutter Installation",
        "Siding Repair",
        "Soffit & Fascia Repair",
    ],

}


def seed_services():
    for cat_name, subs in DATA.items():
        cat, _ = ServiceCategory.objects.get_or_create(name=cat_name)
        for sub_name in subs:
            SubCategory.objects.get_or_create(category=cat, name=sub_name)

    print("✅ Seed complete")
