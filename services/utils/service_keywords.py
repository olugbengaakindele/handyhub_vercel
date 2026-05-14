import re
from services.models import SubCategory


SERVICE_KEYWORDS = {
    "Lawn Mowing": [
        "lawn", "mow", "mowing", "grass", "cut grass", "grass cutting", "lawn care",
        "lawn service", "yard maintenance", "yard work", "trim grass", "overgrown grass",
        "front yard", "back yard", "backyard", "front lawn", "garden lawn", "weekly mowing",
        "biweekly mowing", "summer lawn", "maintain lawn", "lawn maintenance", "grass too long",
        "cut my lawn", "mow my lawn", "mower", "lawn mower", "turf", "yard cleanup",
        "lawn cleanup", "edging", "edge lawn", "grass trim", "property grass"
    ],

    "Hedge Trimming": [
        "hedge", "hedges", "trim hedge", "hedge trimming", "bush", "bushes", "shrubs",
        "shrub trimming", "trim shrubs", "trim bushes", "overgrown hedge", "overgrown shrubs",
        "shape hedge", "shape bushes", "garden hedge", "tree trimming", "small tree trimming",
        "prune", "pruning", "prune bushes", "prune shrubs", "branch trimming", "branches",
        "yard trimming", "landscape trimming", "hedge cutting", "bush cutting", "shrub cutting",
        "front hedge", "backyard hedge", "trim plants", "plant trimming"
    ],

    "Weeding": [
        "weed", "weeds", "weeding", "remove weeds", "pull weeds", "garden weeds",
        "weed removal", "yard weeds", "lawn weeds", "flower bed weeds", "overgrown weeds",
        "weed control", "kill weeds", "clear weeds", "clean weeds", "backyard weeds",
        "front yard weeds", "driveway weeds", "sidewalk weeds", "patio weeds",
        "weeds between stones", "weeds in gravel", "garden cleanup", "yard cleanup",
        "remove unwanted plants", "dandelions", "thistle", "crabgrass", "weed spraying",
        "weed treatment"
    ],

    "Landscaping": [
        "landscape", "landscaping", "garden design", "yard design", "yard work",
        "soil", "mulch", "mulching", "garden bed", "flower bed", "planting",
        "plant flowers", "plant shrubs", "sod", "lay sod", "new lawn", "rock garden",
        "gravel", "decorative rock", "retaining wall", "patio stones", "paving stones",
        "yard makeover", "backyard makeover", "front yard design", "outdoor design",
        "garden renovation", "lawn renovation", "landscape repair", "landscape maintenance",
        "topsoil", "garden edging", "stone edging", "tree planting", "shrub planting"
    ],

    "Driveway Clearing": [
        "driveway snow", "clear driveway", "snow on driveway", "driveway clearing",
        "snow removal driveway", "shovel driveway", "plow driveway", "plough driveway",
        "driveway plowing", "driveway ploughing", "snow plow", "snow plough",
        "snow clearing", "heavy snow", "snow blocked driveway", "blocked driveway",
        "car stuck snow", "remove snow", "winter driveway", "driveway ice",
        "clear snow", "snow service", "residential snow removal", "home snow removal",
        "parking pad snow", "garage entrance snow", "snow after storm", "snow cleanup"
    ],

    "Sidewalk Clearing": [
        "sidewalk snow", "clear sidewalk", "walkway snow", "sidewalk clearing",
        "snow on walkway", "clear walkway", "shovel sidewalk", "shovel walkway",
        "icy sidewalk", "front walk", "front walkway", "pathway snow", "clear path",
        "clear steps", "snow on steps", "stairs snow", "porch snow", "entryway snow",
        "public sidewalk", "city sidewalk", "snow removal sidewalk", "winter walkway",
        "walkway clearing", "snow path", "remove snow from sidewalk"
    ],

    "Salting & De-icing": [
        "ice", "icy", "salt", "salting", "deicing", "de-icing", "slippery",
        "frozen driveway", "frozen sidewalk", "ice melt", "apply salt", "spread salt",
        "black ice", "ice control", "deice driveway", "deice sidewalk", "slippery steps",
        "icy steps", "icy walkway", "icy path", "winter ice", "salt driveway",
        "salt sidewalk", "salt walkway", "remove ice", "melt ice", "ice buildup",
        "frozen walkway", "dangerous ice", "anti slip", "anti-ice"
    ],

    "Leak Repair": [
        "leak", "leaks", "leaking", "water leak", "pipe leak", "dripping", "burst pipe",
        "water dripping", "water damage", "water under sink", "sink leaking", "toilet leaking",
        "faucet leaking", "tap leaking", "pipe burst", "broken pipe", "water coming out",
        "water on floor", "ceiling leak", "basement leak", "leaky pipe", "leaky faucet",
        "leaky tap", "drip", "dripping tap", "dripping faucet", "plumbing leak",
        "emergency leak", "water line leak", "hidden leak", "shower leak", "bath leak",
        "leak under cabinet"
    ],

    "Pipe Installation": [
        "install pipe", "pipe installation", "new pipe", "replace pipe", "water line",
        "install water line", "replace water line", "pipe replacement", "plumbing pipe",
        "new plumbing", "rough in plumbing", "rough-in plumbing", "add pipe",
        "move pipe", "relocate pipe", "copper pipe", "pex pipe", "pvc pipe",
        "drain pipe install", "supply line", "water supply line", "pipe upgrade",
        "pipe fitting", "pipe connection", "install plumbing", "basement plumbing",
        "kitchen plumbing", "bathroom plumbing", "new bathroom pipe", "new kitchen pipe"
    ],

    "Drain Cleaning": [
        "drain", "drains", "clog", "clogs", "clogged", "blocked drain", "slow drain",
        "sink blocked", "toilet blocked", "drain cleaning", "unclog", "unclog drain",
        "unblock drain", "plugged drain", "plugged sink", "blocked sink", "sink not draining",
        "tub not draining", "bathtub drain", "shower drain", "floor drain", "kitchen drain",
        "bathroom drain", "sewer backup", "backup", "water backing up", "standing water",
        "drain smell", "bad smell drain", "snake drain", "drain snake", "main drain",
        "toilet clog", "clogged toilet"
    ],

    "Water Heater Repair": [
        "water heater", "hot water", "no hot water", "heater leaking", "tankless",
        "hot water tank", "water tank", "tank leaking", "cold water only", "pilot light",
        "water not heating", "replace water heater", "repair water heater", "tankless heater",
        "boiler", "hot water issue", "hot water problem", "water heater noise",
        "heater making noise", "rusty hot water", "low hot water", "not enough hot water",
        "gas water heater", "electric water heater", "water heater install",
        "hot water stopped", "water heater broken"
    ],

    "Wiring": [
        "wiring", "rewire", "electrical wire", "wire problem", "power issue", "electrical issue",
        "electrical problem", "short circuit", "sparking", "burning smell", "electrical smell",
        "new wiring", "old wiring", "install wire", "replace wiring", "loose wire",
        "faulty wiring", "basement wiring", "garage wiring", "kitchen wiring", "bathroom wiring",
        "wire repair", "electrical repair", "power not working", "room has no power",
        "lights flicker", "flickering power", "breaker trips", "tripping breaker"
    ],

    "Lighting Installation": [
        "light", "lights", "lighting", "install light", "ceiling light", "fixture", "bulb",
        "switch", "light fixture", "replace light", "new light", "pot light", "recessed light",
        "chandelier", "pendant light", "outdoor light", "security light", "motion light",
        "garage light", "kitchen light", "bathroom light", "vanity light", "led light",
        "light not working", "install fixture", "ceiling fixture", "change fixture",
        "light switch", "dimmer", "install dimmer", "flickering light", "broken light"
    ],

    "Panel Upgrade": [
        "panel", "breaker", "electrical panel", "fuse box", "panel upgrade", "upgrade panel",
        "breaker panel", "main panel", "service panel", "electrical service", "amp upgrade",
        "100 amp", "200 amp", "panel replacement", "replace panel", "old panel", "fuse panel",
        "breaker box", "circuit breaker", "breaker keeps tripping", "add breaker",
        "new breaker", "sub panel", "subpanel", "garage panel", "basement panel",
        "electrical capacity", "home panel", "power panel"
    ],

    "Outlet Repair": [
        "outlet", "outlets", "socket", "plug", "power outlet", "wall outlet", "receptacle",
        "outlet not working", "dead outlet", "broken outlet", "loose outlet", "replace outlet",
        "install outlet", "new outlet", "add outlet", "gfci", "gfi", "kitchen outlet",
        "bathroom outlet", "garage outlet", "outdoor outlet", "plug not working",
        "socket not working", "burnt outlet", "sparking outlet", "hot outlet",
        "usb outlet", "electrical socket"
    ],

    "Interior Painting": [
        "paint room", "interior paint", "inside painting", "wall painting", "paint bedroom",
        "paint living room", "paint kitchen", "paint basement", "paint walls", "paint ceiling",
        "ceiling painting", "indoor painting", "interior painter", "wall paint",
        "repaint room", "touch up paint", "paint trim", "paint doors", "paint baseboards",
        "drywall paint", "condo painting", "apartment painting", "house interior",
        "inside walls", "paint hallway", "paint office room", "fresh paint inside"
    ],

    "Exterior Painting": [
        "outside painting", "exterior paint", "paint house outside", "siding paint",
        "paint siding", "outdoor painting", "exterior painter", "paint exterior",
        "paint garage", "paint stucco", "paint brick", "paint front door", "paint porch",
        "paint deck outside", "paint trim outside", "house painting", "repaint exterior",
        "outside wall", "paint fence outside", "weatherproof paint", "exterior staining",
        "paint shed", "paint balcony", "paint railing", "outdoor wall paint"
    ],

    "Fence Painting": [
        "paint fence", "fence painting", "stain fence", "fence stain", "fence staining",
        "paint wooden fence", "wood fence paint", "spray fence", "repaint fence",
        "old fence paint", "fence color", "seal fence", "fence sealing", "deck and fence",
        "outdoor fence", "backyard fence", "front fence", "privacy fence stain",
        "wood staining", "fence refinishing", "fence maintenance"
    ],

    "Framing": [
        "framing", "frame wall", "wood frame", "basement frame", "wall framing",
        "interior framing", "rough framing", "build wall", "partition wall", "stud wall",
        "wood studs", "frame basement", "frame room", "carpentry framing", "structural framing",
        "frame closet", "frame door", "frame opening", "new wall", "renovation framing",
        "construction framing", "garage framing", "addition framing"
    ],

    "Deck Building": [
        "deck", "decks", "build deck", "repair deck", "decking", "patio deck",
        "new deck", "replace deck", "deck boards", "deck stairs", "deck railing",
        "wood deck", "composite deck", "backyard deck", "front deck", "deck builder",
        "deck repair", "deck installation", "deck extension", "deck renovation",
        "porch deck", "patio repair", "outdoor deck", "deck maintenance", "deck frame",
        "deck surface", "deck floor"
    ],

    "Cabinet Installation": [
        "cabinet", "cabinets", "install cabinet", "kitchen cabinet", "cabinet repair",
        "cabinet installation", "bathroom cabinet", "vanity cabinet", "new cabinet",
        "replace cabinet", "cabinet door", "cabinet hinge", "cabinet handle",
        "cupboard", "cupboards", "install cupboards", "kitchen cupboards",
        "cabinet mounting", "wall cabinet", "base cabinet", "pantry cabinet",
        "custom cabinet", "cabinet carpenter", "cabinet refacing", "cabinet adjustment"
    ],

    "House Cleaning": [
        "clean house", "house cleaning", "home cleaning", "regular cleaning", "deep clean",
        "deep cleaning", "maid service", "cleaner", "residential cleaning", "apartment cleaning",
        "condo cleaning", "kitchen cleaning", "bathroom cleaning", "dusting", "vacuuming",
        "mopping", "weekly cleaning", "biweekly cleaning", "monthly cleaning",
        "spring cleaning", "general cleaning", "home cleaner", "clean my home",
        "clean my apartment", "tidy house", "sanitize home", "clean floors"
    ],

    "Move-out Cleaning": [
        "move out", "move-out", "moving cleaning", "end of tenancy", "vacate cleaning",
        "move in cleaning", "move-in cleaning", "rental cleaning", "clean before moving",
        "clean after moving", "tenant cleaning", "landlord cleaning", "empty house cleaning",
        "empty apartment cleaning", "post move cleaning", "pre move cleaning",
        "lease cleaning", "bond cleaning", "deposit cleaning", "rental move out",
        "final cleaning", "moving day clean", "apartment turnover", "house turnover"
    ],

    "Office Cleaning": [
        "office cleaning", "clean office", "commercial cleaning", "workplace cleaning",
        "business cleaning", "janitorial", "janitor", "desk cleaning", "office floors",
        "office washroom", "boardroom cleaning", "building cleaning", "shop cleaning",
        "retail cleaning", "clinic cleaning", "warehouse cleaning", "commercial cleaner",
        "workplace cleaner", "after hours cleaning", "daily office cleaning",
        "weekly office cleaning", "staff kitchen cleaning", "office garbage"
    ],

    "Rodent Control": [
        "mouse", "mice", "rat", "rats", "rodent", "rodents", "mouse problem",
        "rat problem", "mice in house", "rats in house", "mouse droppings", "rat droppings",
        "rodent droppings", "scratching in walls", "scratching ceiling", "animal in wall",
        "trap mice", "mouse trap", "rat trap", "rodent removal", "pest mice",
        "pest rats", "mouse infestation", "rat infestation", "garage mice", "basement mice",
        "kitchen mice", "rodent control"
    ],

    "Insect Control": [
        "bug", "bugs", "insect", "insects", "ants", "cockroach", "cockroaches", "wasp",
        "wasps", "bed bug", "bed bugs", "spider", "spiders", "flies", "mosquito",
        "mosquitoes", "beetles", "silverfish", "earwigs", "carpenter ants",
        "ant problem", "roach problem", "bug infestation", "insect infestation",
        "wasp nest", "hornet nest", "bee nest", "pest control", "spray bugs",
        "remove insects", "bedbug treatment"
    ],

    "Wildlife Removal": [
        "wildlife", "raccoon", "raccoons", "skunk", "skunks", "squirrel", "squirrels",
        "bird nest", "animal removal", "animal in attic", "animal in roof",
        "animal in chimney", "raccoon in attic", "squirrel in attic", "skunk under deck",
        "birds in vent", "bat", "bats", "possum", "porcupine", "wild animal",
        "remove animal", "humane removal", "nest removal", "attic animal",
        "chimney animal", "deck animal", "wildlife control"
    ],

    "Roof Repair": [
        "roof leak", "leaking roof", "roof repair", "missing shingles", "roof damage",
        "damaged roof", "shingle repair", "replace shingles", "roof patch",
        "roof leaking", "water from roof", "ceiling water roof", "storm damage roof",
        "hail damage roof", "wind damage roof", "roof hole", "roof flashing",
        "flashing repair", "chimney flashing", "roof vent leak", "roof maintenance",
        "minor roof repair", "emergency roof repair", "roof problem", "roof inspection"
    ],

    "Roof Replacement": [
        "replace roof", "new roof", "roof replacement", "old roof", "reroof", "re-roof",
        "roof install", "roof installation", "full roof", "complete roof", "roof shingles",
        "new shingles", "asphalt shingles", "metal roof", "flat roof replacement",
        "garage roof replacement", "house roof replacement", "roof estimate",
        "roof quote", "old shingles", "worn roof", "roof upgrade", "install new roof"
    ],

    "Gutter Cleaning": [
        "gutter", "gutters", "clean gutter", "blocked gutter", "eavestrough",
        "eavestrough cleaning", "gutter cleaning", "clogged gutter", "leaking gutter",
        "overflowing gutter", "gutter overflow", "leaves in gutter", "downspout",
        "blocked downspout", "clean downspout", "rain gutter", "gutter debris",
        "gutter leaves", "gutter maintenance", "roof gutter", "drainage gutter",
        "water spilling gutter", "gutter repair", "gutter blockage"
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