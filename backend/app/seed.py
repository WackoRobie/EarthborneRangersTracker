"""Seed reference data: card library and storylines.

This runs once at startup. If the data is already present it does nothing,
so it is safe to call on every boot.
"""

from sqlalchemy.orm import Session

from app.models.card import Card
from app.models.storyline import Storyline, StorylineDayPreset


# ---------------------------------------------------------------------------
# Card definitions
# ---------------------------------------------------------------------------

def _card(name, card_type, source_set, aspect, cost, tags, is_expert=False):
    return dict(
        name=name,
        card_type=card_type,
        source_set=source_set,
        aspect=aspect,
        cost=cost,
        tags=tags,
        is_expert=is_expert,
    )


PERSONALITY_CARDS = [
    # AWA
    _card("Insightful",    "personality", "AWA", "AWA", 1, ["Attribute", "Innate"]),
    _card("Vigilant",      "personality", "AWA", "AWA", 1, ["Attribute", "Innate"]),
    _card("Perceptive",    "personality", "AWA", "AWA", 1, ["Attribute", "Innate"]),
    _card("Thorough",      "personality", "AWA", "AWA", 2, ["Attribute", "Innate"]),
    # FIT
    _card("Passionate",    "personality", "FIT", "FIT", 1, ["Attribute", "Innate"]),
    _card("Balanced",      "personality", "FIT", "FIT", 1, ["Attribute", "Innate"]),
    _card("Determined",    "personality", "FIT", "FIT", 1, ["Attribute", "Innate"]),
    _card("Bold",          "personality", "FIT", "FIT", 2, ["Attribute", "Innate"]),
    # FOC
    _card("Meticulous",    "personality", "FOC", "FOC", 1, ["Attribute", "Innate"]),
    _card("Versatile",     "personality", "FOC", "FOC", 1, ["Attribute", "Innate"]),
    _card("Inventive",     "personality", "FOC", "FOC", 1, ["Attribute", "Innate"]),
    _card("Astute",        "personality", "FOC", "FOC", 2, ["Attribute", "Innate"]),
    # SPI
    _card("Persuasive",    "personality", "SPI", "SPI", 1, ["Attribute", "Innate"]),
    _card("Thoughtful",    "personality", "SPI", "SPI", 1, ["Attribute", "Innate"]),
    _card("Engaging",      "personality", "SPI", "SPI", 1, ["Attribute", "Innate"]),
    _card("Compassionate", "personality", "SPI", "SPI", 2, ["Attribute", "Innate"]),
]

BACKGROUND_CARDS = [
    # --- Artisan ---
    _card("Universal Power Cells",    "background", "Artisan", "FOC", 1, ["Attachment", "Mod", "Tech"]),
    _card("Functional Replica",       "background", "Artisan", "FOC", 2, ["Gear", "Tool", "Tech"]),
    _card("The Right Tool",           "background", "Artisan", "FOC", 3, ["Moment", "Wisdom"]),
    _card("Pocketed Belt Pouch",      "background", "Artisan", "AWA", 1, ["Gear", "Clothing"]),
    _card("The Mother of Invention",  "background", "Artisan", "AWA", 2, ["Moment", "Wisdom"]),
    _card("Moment of Desperation",    "background", "Artisan", "FIT", 1, ["Moment", "Experience", "Weapon"]),
    _card("Masterwork",               "background", "Artisan", "FIT", 2, ["Attachment", "Mod", "Expert"], is_expert=True),
    _card("Favorite Gear",            "background", "Artisan", "SPI", 1, ["Attachment", "Mod"]),
    _card("Energized Hiking Greaves", "background", "Artisan", "SPI", 2, ["Gear", "Tech", "Aid"]),
    # --- Forager ---
    _card("Secret Garden",            "background", "Forager", "FOC", 1, ["Attachment", "Nature"]),
    _card("Loose-leaf Tea Kit",       "background", "Forager", "FOC", 2, ["Gear", "Food"]),
    _card("Familiar Ground",          "background", "Forager", "FIT", 1, ["Moment", "Experience"]),
    _card("Carbonforged Trowel",      "background", "Forager", "FIT", 2, ["Gear", "Tool", "Weapon"]),
    _card("Green Thumb",              "background", "Forager", "AWA", 3, ["Attachment", "Skill", "Expert"], is_expert=True),
    _card("Local Fare",               "background", "Forager", "AWA", 1, ["Moment", "Experience", "Nature"]),
    _card("Puffercrawler Spores",     "background", "Forager", "AWA", 2, ["Attachment", "Nature"]),
    _card("Nature's Abundance",       "background", "Forager", "SPI", 1, ["Moment", "Experience", "Nature"]),
    _card("Static Sifter",            "background", "Forager", "SPI", 2, ["Gear", "Tool", "Food"]),
    # --- Shepherd ---
    _card("One Eye Open",             "background", "Shepherd", "AWA", 0, ["Moment", "Wisdom"]),
    _card("Riri the Sparrow Hawk",    "background", "Shepherd", "AWA", 2, ["Being", "Companion", "Avian"]),
    _card("A Gentle Nudge",           "background", "Shepherd", "FIT", 1, ["Moment", "Experience"]),
    _card("Homeward Bound",           "background", "Shepherd", "FIT", 2, ["Moment", "Experience"]),
    _card("Paratrepsis Whistle",      "background", "Shepherd", "FOC", 1, ["Gear", "Tool", "Aid"]),
    _card("A Deeper Understanding",   "background", "Shepherd", "FOC", 2, ["Moment", "Wisdom"]),
    _card("Healing Touch",            "background", "Shepherd", "SPI", 1, ["Moment", "Skill", "Aid"]),
    _card("Calming Presence",         "background", "Shepherd", "SPI", 1, ["Attachment", "Skill"]),
    _card("Oru the Sheep Dog",        "background", "Shepherd", "SPI", 2, ["Being", "Companion", "Mammal", "Expert"], is_expert=True),
    # --- Traveler ---
    _card("Eagle Eye",                "background", "Traveler", "AWA", 1, ["Moment", "Skill"]),
    _card("Paths We've Roamed Before","background", "Traveler", "AWA", 2, ["Moment", "Experience"]),
    _card("Strider",                  "background", "Traveler", "FIT", 1, ["Attribute", "Innate"]),
    _card("Trail Mix",                "background", "Traveler", "FIT", 2, ["Gear", "Food", "Aid"]),
    _card("Perfect Recall",           "background", "Traveler", "FOC", None, ["Moment", "Skill"]),   # X cost
    _card("Reverb Locket",            "background", "Traveler", "FOC", 1, ["Gear", "Tech", "Expert"], is_expert=True),
    _card("Adaptable Multitool",      "background", "Traveler", "FOC", 2, ["Gear", "Tool", "Tech"]),
    _card("Ironwool Boots",           "background", "Traveler", "SPI", 1, ["Gear", "Clothing"]),
    _card("Meditation Pillow",        "background", "Traveler", "SPI", 2, ["Gear", "Aid"]),
]

SPECIALTY_CARDS = [
    # --- Artificer roles ---
    _card("Masterful Engineer",            "role", "Artificer", None, None, []),
    _card("Exceptional Tinkerer",          "role", "Artificer", None, None, []),
    # --- Artificer cards ---
    _card("Ferinodex",                     "specialty", "Artificer", "AWA", 1, ["Gear", "Book", "Tech"]),
    _card("Carbonforged Cable",            "specialty", "Artificer", "AWA", 2, ["Attachment", "Tool", "Tech"]),
    _card("Dayhowler",                     "specialty", "Artificer", "AWA", 3, ["Gear", "Tech"]),
    _card("Trail Markers",                 "specialty", "Artificer", "FIT", 1, ["Attachment", "Tool"]),
    _card("Spiderpad Gloves",              "specialty", "Artificer", "FIT", 2, ["Gear", "Clothing", "Tech"]),
    _card("Wrist-mounted Darter",          "specialty", "Artificer", "FIT", 3, ["Gear", "Tech", "Weapon"]),
    _card("Infusion Canteen",              "specialty", "Artificer", "FOC", 1, ["Gear", "Tool", "Tech"]),
    _card("Memorill Sketchpad",            "specialty", "Artificer", "FOC", 2, ["Gear", "Book", "Tech"]),
    _card("Memlev Trekking Poles",         "specialty", "Artificer", "FOC", 3, ["Gear", "Tool", "Tech"]),
    _card("A Stone in the River",          "specialty", "Artificer", "SPI", 1, ["Moment", "Wisdom"]),
    _card("Camoweave Cloak",               "specialty", "Artificer", "SPI", 2, ["Gear", "Clothing", "Tech"]),
    _card("Thoroughly Prepared",           "specialty", "Artificer", "SPI", 3, ["Moment", "Experience"]),
    # --- Conciliator roles ---
    _card("Voice of the Elders",           "role", "Conciliator", None, None, []),
    _card("Guardian",                      "role", "Conciliator", None, None, []),
    # --- Conciliator cards ---
    _card("Surveyed Land",                 "specialty", "Conciliator", "AWA", 1, ["Attachment", "Experience", "Aid"]),
    _card("Tranquilisnare",                "specialty", "Conciliator", "AWA", 2, ["Attachment", "Aid"]),
    _card("One With Nature",               "specialty", "Conciliator", "AWA", 3, ["Moment", "Wisdom"]),
    _card("Follow in Footsteps",           "specialty", "Conciliator", "FIT", 1, ["Moment", "Skill"]),
    _card("Orlin Thumper",                 "specialty", "Conciliator", "FIT", 1, ["Gear", "Tech", "Weapon"]),
    _card("Tracked",                       "specialty", "Conciliator", "FIT", 3, ["Attachment", "Skill", "Aid"]),
    _card("Intention Translator",          "specialty", "Conciliator", "FOC", 1, ["Gear", "Tech", "Aid"]),
    _card("Safeguard",                     "specialty", "Conciliator", "FOC", 0, ["Moment", "Experience"]),
    _card("Nidocyte Sentinel",             "specialty", "Conciliator", "FOC", 3, ["Attachment", "Tech", "Aid"]),
    _card("Ancestral Teachings",           "specialty", "Conciliator", "SPI", 1, ["Moment", "Wisdom"]),
    _card("Pokodo the Ferret",             "specialty", "Conciliator", "SPI", 2, ["Being", "Companion", "Mammal"]),
    _card("A Dear Friend",                 "specialty", "Conciliator", "SPI", 3, ["Attachment", "Experience", "Expert"], is_expert=True),
    # --- Explorer roles ---
    _card("Undaunted Seeker",              "role", "Explorer", None, None, []),
    _card("Peerless Pathfinder",           "role", "Explorer", None, None, []),
    # --- Explorer cards ---
    _card("A Leaf in the Breeze",          "specialty", "Explorer", "AWA", 1, ["Moment", "Skill"]),
    _card("Hydrolens Goggles",             "specialty", "Explorer", "AWA", 2, ["Gear", "Clothing", "Tech"]),
    _card("Share in the Valley's Secrets", "specialty", "Explorer", "AWA", 3, ["Moment", "Wisdom"]),
    _card("Boundary Sensor",               "specialty", "Explorer", "FIT", 1, ["Gear", "Tech"]),
    _card("Orlin Hiking Stave",            "specialty", "Explorer", "FIT", 2, ["Gear", "Tool", "Tech", "Weapon"]),
    _card("Afforded by Nature",            "specialty", "Explorer", "FIT", 3, ["Moment", "Experience", "Weapon"]),
    _card("Phonoscopic Headset",           "specialty", "Explorer", "FOC", 1, ["Gear", "Clothing", "Tech"]),
    _card("Field Journal",                 "specialty", "Explorer", "FOC", 1, ["Gear", "Book"]),
    _card("Hidden Trail",                  "specialty", "Explorer", "FOC", 3, ["Feature", "Trail"]),
    _card("Walk With Me",                  "specialty", "Explorer", "SPI", 1, ["Moment", "Experience"]),
    _card("Breathe Into It",               "specialty", "Explorer", "SPI", 2, ["Moment", "Skill"]),
    _card("Cradled by the Earth",          "specialty", "Explorer", "SPI", 3, ["Moment", "Wisdom"]),
    # --- Shaper roles ---
    _card("Prodigy of the Floating Tower", "role", "Shaper", None, None, []),
    _card("Adherent of the First Ideal",   "role", "Shaper", None, None, []),
    # --- Shaper cards ---
    _card("Root Snare",                    "specialty", "Shaper", "AWA", 1, ["Attachment", "Manifestation", "Nature"]),
    _card("Sky Whip",                      "specialty", "Shaper", "AWA", 0, ["Moment", "Manifestation", "Weapon"]),
    _card("Stave of the Sun",              "specialty", "Shaper", "AWA", 3, ["Gear", "Conduit", "Expert"], is_expert=True),
    _card("What Should Never Be",          "specialty", "Shaper", "FIT", 1, ["Moment", "Manifestation"]),
    _card("Shape the Earth",               "specialty", "Shaper", "FIT", 2, ["Moment", "Manifestation"]),
    _card("Staff of the Wanderer",         "specialty", "Shaper", "FIT", 3, ["Gear", "Conduit", "Expert"], is_expert=True),
    _card("Throng of Life",                "specialty", "Shaper", "FOC", 1, ["Moment", "Manifestation"]),
    _card("Novice Lens",                   "specialty", "Shaper", "FOC", 2, ["Gear", "Tech"]),
    _card("Rod of the Clouds",             "specialty", "Shaper", "FOC", 3, ["Gear", "Conduit", "Expert"], is_expert=True),
    _card("Harmonize",                     "specialty", "Shaper", "SPI", 1, ["Attachment", "Manifestation"]),
    _card("Seen Through Cycles",           "specialty", "Shaper", "SPI", 2, ["Moment", "Manifestation"]),
    _card("Scepter of Harmony",            "specialty", "Shaper", "SPI", 3, ["Gear", "Conduit", "Expert"], is_expert=True),
]

ALL_CARDS = PERSONALITY_CARDS + BACKGROUND_CARDS + SPECIALTY_CARDS


# ---------------------------------------------------------------------------
# Lore of the Valley — day weather presets
# ---------------------------------------------------------------------------
# Weather types: "A Perfect Day", "Downpour", "Howling Winds"

_LOTV_WEATHER = (
    # (day_number, weather)
    (1,  "A Perfect Day"),
    (2,  "A Perfect Day"),
    (3,  "A Perfect Day"),
    (4,  "Downpour"),
    (5,  "Downpour"),
    (6,  "Downpour"),
    (7,  "Downpour"),
    (8,  "A Perfect Day"),
    (9,  "A Perfect Day"),
    (10, "Downpour"),
    (11, "Downpour"),
    (12, "Downpour"),
    (13, "Howling Winds"),
    (14, "Howling Winds"),
    (15, "Downpour"),
    (16, "Downpour"),
    (17, "Downpour"),
    (18, "Howling Winds"),
    (19, "Howling Winds"),
    (20, "Howling Winds"),
    (21, "A Perfect Day"),
    (22, "A Perfect Day"),
    (23, "Downpour"),
    (24, "Downpour"),
    (25, "Downpour"),
    (26, "Howling Winds"),
    (27, "Howling Winds"),
    (28, "Howling Winds"),
    (29, "A Perfect Day"),
    (30, "A Perfect Day"),
)


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------

def seed_reference_data(db: Session) -> None:
    """Insert cards and storylines if they don't already exist."""

    # --- Cards ---
    if db.query(Card).count() == 0:
        db.bulk_insert_mappings(Card, ALL_CARDS)
        db.flush()
        print(f"[seed] Inserted {len(ALL_CARDS)} cards.")
    else:
        print("[seed] Cards already present, skipping.")

    # --- Lore of the Valley storyline ---
    if not db.query(Storyline).filter_by(name="Lore of the Valley").first():
        storyline = Storyline(
            name="Lore of the Valley",
            min_rangers=1,
            max_rangers=4,
        )
        db.add(storyline)
        db.flush()

        presets = [
            StorylineDayPreset(
                storyline_id=storyline.id,
                day_number=day_num,
                weather=weather,
            )
            for day_num, weather in _LOTV_WEATHER
        ]
        db.bulk_save_objects(presets)
        db.flush()
        print(f"[seed] Inserted storyline 'Lore of the Valley' with {len(presets)} day presets.")
    else:
        print("[seed] Storyline 'Lore of the Valley' already present, skipping.")

    db.commit()
