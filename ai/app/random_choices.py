import random


DESCRIPTION_TONES = [
    "whimsical",
    "mysterious",
    "playful",
    "dramatic",
    "charming",
    "curious",
    "lighthearted",
    "adventurous",
]

DESCRIPTION_FOCUSES = [
    "its distinctive physical appearance",
    "its personality and temperament",
    "how it behaves in the wild",
    "its unusual habits",
    "how it interacts with other creatures",
    "its preferred habitat and lifestyle",
    "a distinctive physical feature",
    "a curious behavior it is known for",
]

NAME_STYLES = [
    "cute and playful",
    "mysterious and fantastical",
    "short and energetic",
    "whimsical and unusual",
    "ancient and mythical",
    "quirky and memorable",
    "a clever combination of concepts related to the creature",
    "soft and friendly",
    "wild and intimidating",
    "magical and easy to pronounce",
]

POKEMON_TYPE_BODY_PLANS: dict[str, list[str]] = {
    "any": [
        "A low-slung quadruped with a long horizontal body, four short powerful legs, and a tail close to the ground.",
        "A long-necked quadruped with exactly four legs, a compact head, and a high, arched back.",
        "A legless serpentine creature with a long, flexible body arranged in a broad S-curve.",
        "A rare upright creature with exactly two legs, unusual nonhuman proportions, and no human hands or clothing.",
        "A compact, broad-bodied quadruped with exactly four legs, a rounded head, and a thick balancing tail.",
        "A narrow-bodied quadruped with exactly four long legs, a small head, and a gently arched back.",
        "A small nonhuman biped with exactly two legs, two short forelimbs, and a large rounded body.",
        "A round-backed quadruped with exactly four short legs, a short neck, and a sweeping tail.",
    ],
    "bug": [
        "A six-legged insect creature with a segmented body, a broad shell, and all six legs visible beneath it.",
        "An eight-legged bug creature with a wide, low body and eight articulated legs; it does not stand upright.",
        "A soft, legless grub-like creature with a curved segmented body, a small rounded head, and tiny feelers.",
        "A moth-like creature with a plump body, exactly two legs, and broad patterned wings held open.",
        "A mantis-inspired biped with exactly two hind legs and two folded grasping forelimbs; no extra legs.",
        "A flattened ladybird-like crawler with exactly four short legs and a smooth rounded shell.",
    ],
    "normal": [
        "A natural four-legged mammal-like creature with a compact body, expressive ears, and a distinctive tail.",
        "A small two-legged creature with a rounded body, two short forelimbs, and proportions unlike a human.",
        "A four-legged runner with a deep chest, narrow waist, long ears, and a flexible tail.",
        "A broad-backed quadruped with exactly four short legs, a wide muzzle, and a curled tail.",
        "A round-bodied biped with exactly two legs, two small forelimbs, and a long tail for balance.",
    ],
    "fire": [
        "A lean four-legged creature with a flame-shaped crest and a tail ending in a bright ember tuft.",
        "A compact quadruped with exactly four legs and glowing heat vents along its flanks; keep its body low and horizontal.",
        "A long-bodied fire creature with exactly four legs, a streaming mane, and a bright flame at the end of its tail.",
        "A stout four-legged creature with ember-like plates along its shoulders and a low, powerful stance.",
        "A nonhuman biped with exactly two legs and two short forelimbs, a broad chest, and a flame-shaped head crest.",
    ],
    "water": [
        "A streamlined aquatic creature with a horizontal body, a broad tail, and paired fins instead of legs.",
        "An amphibious creature with exactly four webbed legs, a broad swimming tail, and gill frills along its neck.",
        "A flat-bodied swimmer with wide side fins, a long tail, and no legs.",
        "A seal-shaped aquatic creature with exactly four flippers, a tapered body, and no feet.",
        "A long-bodied swimmer with no legs, a narrow head, and a continuous dorsal fin from neck to tail.",
    ],
    "electric": [
        "A compact four-legged creature with oversized antenna-like ears and a long, sharply kinked tail.",
        "A spring-loaded hopper with exactly two hind legs, two small forelimbs, and a tightly coiled tail.",
        "A low four-legged runner with a narrow body, conductive cheek tufts, and a long whip-like tail.",
        "A small upright creature with exactly two legs, two short forelimbs, and tall lightning-rod ears.",
        "A four-legged creature with a rounded torso, a zigzag tail, and short bristling fur along its spine.",
    ],
    "grass": [
        "A plant-bodied creature with a broad rooted base and leaf fronds growing directly from its body; no legs.",
        "A low quadruped with exactly four legs, a leafy mane, and a vine-like tail.",
        "A two-legged seed-pod creature with exactly two short forelimbs and a crown of broad leaves.",
        "A creeping plant creature with a long flexible stem, root tendrils, and no legs.",
        "A four-legged creature with a flower-shaped head, a leafy back, and a trailing vine tail.",
    ],
    "ice": [
        "A stocky quadruped with exactly four broad feet, a thick coat, and a ridge of ice crystals along its back.",
        "A low horizontal swimmer with paired flippers, a broad tail, and a smooth frost-covered body; no legs.",
        "A sturdy four-legged creature with a crystalline brow, thick fur, and a compact body built close to the ground.",
        "An upright ice creature with exactly two legs, two short forelimbs, and a broad shaggy body.",
        "A legless ice serpent with a long body, a translucent dorsal crest, and a tapering tail.",
    ],
    "fighting": [
        "An upright fighter with exactly two legs and two powerful forelimbs, a springing stance, and clearly nonhuman proportions.",
        "A low, muscular quadruped with exactly four legs and a braced stance ready to charge; no upright humanoid torso.",
        "A sturdy biped with exactly two legs and two heavy forelimbs, a wide stance, and a compact nonhuman torso.",
        "A four-legged grappler with exactly four powerful legs, a low center of gravity, and a forward-braced posture.",
        "A lean two-legged fighter with two short forelimbs, long springy legs, and a forward-leaning silhouette.",
    ],
    "poison": [
        "A legless coiling creature with a long flexible body, a flared warning frill, and visible poison sacs.",
        "A crouched quadruped with exactly four legs, a toxic-looking dorsal frill, and poison sacs along its sides.",
        "A low two-legged creature with exactly two short forelimbs, a hooded neck frill, and swollen poison glands.",
        "A soft-bodied, legless creature with a broad underside, a ridged back, and small toxin sacs.",
        "A four-legged crawler with exactly four short legs, a narrow head, and a row of poisonous dorsal spines.",
    ],
    "ground": [
        "A compact burrowing quadruped with exactly four sturdy digging legs and a low body close to the ground.",
        "A bipedal burrower with exactly two hind legs and two short digging forelimbs, built close to the ground.",
        "A long, low quadruped with exactly four legs, a shovel-shaped snout, and broad digging paws.",
        "A legless tunneling creature with a blunt wedge-shaped head, a flexible body, and a thick tapered tail.",
        "A compact four-legged creature with oversized forepaws, a sturdy back, and a short balancing tail.",
    ],
    "flying": [
        "A horizontal glider with broad wings and exactly two small feet tucked beneath its body; it is not humanoid.",
        "A four-legged flying creature with exactly four legs and broad wings attached separately along its back.",
        "A wing-bodied glider with broad membrane wings and no legs, shaped to soar horizontally.",
        "A light two-legged flier with exactly two small feet, long wings, and a streamlined body held horizontally.",
        "A four-legged soaring creature with a long tail, broad wings, and a narrow aerodynamic torso.",
    ],
    "psychic": [
        "A floating creature with a compact central body, suspended markings, and trailing fins; no legs.",
        "A slender two-legged creature with exactly two short forelimbs, an enlarged head, and a balanced nonhuman silhouette.",
        "A hovering creature with a smooth core, a pair of orbiting fins, and no legs or arms.",
        "A four-legged, long-bodied creature with a high forehead, narrow muzzle, and a balanced nonhuman silhouette.",
        "A small biped with exactly two legs, two delicate forelimbs, and an oversized smooth head.",
    ],
    "rock": [
        "A heavy, low quadruped with exactly four short stone-like legs and a broad craggy body.",
        "A boulder-backed creature supported by exactly four sturdy legs, with layered mineral plates forming its silhouette.",
        "A two-legged stone creature with exactly two thick arms, a compact body, and a blocky nonhuman silhouette.",
        "A broad-shelled quadruped with exactly four sturdy legs and layered slabs of stone across its back.",
        "A low four-legged creature with a wedge-shaped mineral head, a heavy torso, and a short tail.",
    ],
    "ghost": [
        "A hovering draped creature with a tapering lower body and trailing wisps instead of legs.",
        "A legless, smoke-like serpent with a narrow head, a long curling body, and wisps trailing from its tail.",
        "A floating orb-bodied creature with no legs and two long, tapering veils trailing beneath it.",
        "A four-legged shadow creature with exactly four visible paws and wisps of mist streaming from its back.",
        "A legless, narrow-bodied apparition with a hollow-looking face and a tail that fades into vapor.",
    ],
    "dragon": [
        "A long-bodied four-legged drake with a horizontal spine, a long tail, and wings separate from its four legs.",
        "A legless serpentine dragon with a long coiling body, a horned head, and a continuous back crest.",
        "A two-legged wyvern with exactly two legs, a long tail, and wings that form its forelimbs.",
        "A broad four-legged dragon with exactly four legs, a deep chest, swept-back horns, and a separate pair of wings.",
        "A long, legless dragon with a narrow head, whisker-like feelers, and a continuous fin along its spine.",
    ],
    "dark": [
        "A low, four-legged prowler with exactly four legs, a broad shoulder line, and a long counterbalancing tail.",
        "A lean two-legged creature with exactly two short forelimbs, a narrow nonhuman head, and a crouched silhouette.",
        "A broad-chested quadruped with exactly four legs, a lowered head, and a heavy mane framing its shoulders.",
        "A legless shadow-serpent with a narrow head, a long coiling body, and a sharply tapered tail.",
        "A crouching four-legged creature with oversized forequarters, a low head, and a thick tail held close to the ground.",
    ],
    "steel": [
        "A mechanical quadruped with exactly four articulated legs and a low, armored silhouette.",
        "A bipedal mechanical creature with exactly two legs and two separate tool-like forelimbs; keep its proportions nonhuman.",
        "A compact four-legged machine with exactly four piston-like legs, a narrow head, and layered armor plates.",
        "A legless tracked creature with a low armored body and two short manipulator arms; no legs.",
        "A tall mechanical biped with exactly two legs, two jointed arms, and a clearly nonhuman silhouette.",
    ],
    "fairy": [
        "A small hovering creature with a rounded body, delicate wing-like fins, and no legs.",
        "A graceful four-legged creature with exactly four slender legs, a petal-shaped crest, and a light, curved silhouette.",
        "A small biped with exactly two legs, two delicate forelimbs, and a pair of translucent wings.",
        "A floating, petal-shaped creature with no legs and soft ribbon-like fins trailing from its body.",
        "A light-footed quadruped with exactly four legs, a rounded face, and a flowing petal-like mane.",
    ],
}

POKEMON_TYPE_COLORS: dict[str, list[str]] = {
    "normal": ["cream", "warm beige", "soft brown", "light gray"],
    "fire": ["scarlet red", "flame orange"],
    "water": ["ocean blue", "cyan", "deep teal"],
    "electric": ["bright yellow", "electric blue"],
    "grass": ["leaf green", "lime green", "olive"],
    "ice": ["ice blue", "white", "pale cyan"],
    "fighting": ["crimson", "warm brown", "orange"],
    "poison": ["violet", "magenta", "acid green"],
    "ground": ["ochre", "sand", "terracotta"],
    "flying": ["sky blue", "white", "silver", "black", "gray", "brown"],
    "psychic": ["hot pink", "violet", "indigo"],
    "bug": ["lime green", "amber", "dark brown"],
    "rock": ["slate gray", "stone beige", "rust brown"],
    "ghost": ["lavender", "indigo", "pale blue"],
    "dragon": ["royal purple", "teal", "gold"],
    "dark": ["black", "charcoal", "deep purple"],
    "steel": ["silver", "gunmetal gray", "blue gray"],
    "fairy": ["pastel pink", "lavender", "soft blue"],
}

def get_description_tone() -> str:
    return random.choice(DESCRIPTION_TONES)


def get_description_focus() -> str:
    return random.choice(DESCRIPTION_FOCUSES)


def get_name_style() -> str:
    return random.choice(NAME_STYLES)


def get_pokemon_type_body_plan(pokemon_types: list[str]) -> str:
    available_types = ["any"]
    available_types.extend(
        pokemon_type.lower()
        for pokemon_type in pokemon_types
        if pokemon_type.lower() in POKEMON_TYPE_BODY_PLANS
        and pokemon_type.lower() != "any"
    )
    selected_type = random.choice(available_types)
    return random.choice(POKEMON_TYPE_BODY_PLANS[selected_type])


def get_pokemon_type_colors(pokemon_type: str) -> list[str]:
    return POKEMON_TYPE_COLORS.get(
        pokemon_type.lower(),
        ["neutral gray", "cream"],
    )


def get_random_pokemon(pokemon_entries: list[dict]) -> dict:
    return random.choice(pokemon_entries)


