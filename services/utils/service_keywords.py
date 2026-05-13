import re
from services.models import SubCategory


SERVICE_KEYWORDS = {
    "Lawn Mowing": [
        "lawn", "mow", "mowing", "grass", "cut grass", "yard maintenance"
    ],
    "Hedge Trimming": [
        "hedge", "trim hedge", "bush", "shrubs", "tree trimming"
    ],
    "Weeding": [
        "weed", "weeding", "remove weeds", "garden weeds"
    ],
    "Landscaping": [
        "landscape", "landscaping", "garden design", "yard work", "soil", "mulch"
    ],

    "Driveway Clearing": [
        "driveway snow", "clear driveway", "snow on driveway", "driveway clearing"
    ],
    "Sidewalk Clearing": [
        "sidewalk snow", "clear sidewalk", "walkway snow", "sidewalk clearing"
    ],
    "Salting & De-icing": [
        "ice", "icy", "salt", "deicing", "de-icing", "slippery", "frozen driveway"
    ],

    "Leak Repair": [
        "leak", "leaking", "water leak", "pipe leak", "dripping", "burst pipe", "water dripping"
    ],
    "Pipe Installation": [
        "install pipe", "pipe installation", "new pipe", "replace pipe", "water line"
    ],
    "Drain Cleaning": [
        "drain", "clog", "clogged", "blocked drain", "slow drain", "sink blocked", "toilet blocked"
    ],
    "Water Heater Repair": [
        "water heater", "hot water", "no hot water", "heater leaking", "tankless"
    ],

    "Wiring": [
        "wiring", "rewire", "electrical wire", "wire problem", "power issue"
    ],
    "Lighting Installation": [
        "light", "lighting", "install light", "ceiling light", "fixture", "bulb", "switch"
    ],
    "Panel Upgrade": [
        "panel", "breaker", "electrical panel", "fuse box", "panel upgrade"
    ],
    "Outlet Repair": [
        "outlet", "socket", "plug", "power outlet", "wall outlet"
    ],

    "Interior Painting": [
        "paint room", "interior paint", "inside painting", "wall painting", "paint bedroom"
    ],
    "Exterior Painting": [
        "outside painting", "exterior paint", "paint house outside", "siding paint"
    ],
    "Fence Painting": [
        "paint fence", "fence painting", "stain fence", "fence stain"
    ],

    "Framing": [
        "framing", "frame wall", "wood frame", "basement frame"
    ],
    "Deck Building": [
        "deck", "build deck", "repair deck", "decking", "patio deck"
    ],
    "Cabinet Installation": [
        "cabinet", "install cabinet", "kitchen cabinet", "cabinet repair"
    ],

    "House Cleaning": [
        "clean house", "house cleaning", "home cleaning", "regular cleaning"
    ],
    "Move-out Cleaning": [
        "move out", "move-out", "moving cleaning", "end of tenancy", "vacate cleaning"
    ],
    "Office Cleaning": [
        "office cleaning", "clean office", "commercial cleaning", "workplace cleaning"
    ],

    "Rodent Control": [
        "mouse", "mice", "rat", "rodent", "rodents"
    ],
    "Insect Control": [
        "bug", "bugs", "insect", "ants", "cockroach", "wasp", "bed bug", "spider"
    ],
    "Wildlife Removal": [
        "wildlife", "raccoon", "skunk", "squirrel", "bird nest", "animal removal"
    ],

    "Roof Repair": [
        "roof leak", "leaking roof", "roof repair", "missing shingles", "roof damage"
    ],
    "Roof Replacement": [
        "replace roof", "new roof", "roof replacement", "old roof"
    ],
    "Gutter Cleaning": [
        "gutter", "gutters", "clean gutter", "blocked gutter", "eavestrough"
    ],
}


def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\-&]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def suggest_service_from_text(problem_text):
    problem_text = normalize_text(problem_text)

    if not problem_text:
        return None

    best_match = None
    best_score = 0

    for subcategory_name, keywords in SERVICE_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            keyword = normalize_text(keyword)

            if keyword in problem_text:
                score += 5

            for word in keyword.split():
                if word in problem_text:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = subcategory_name

    if not best_match or best_score == 0:
        return None

    subcategory = (
        SubCategory.objects
        .select_related("category")
        .filter(name__iexact=best_match)
        .first()
    )

    if not subcategory:
        return None

    return {
        "category_id": subcategory.category.id,
        "category_name": subcategory.category.name,
        "subcategory_id": subcategory.id,
        "subcategory_name": subcategory.name,
        "score": best_score,
    }