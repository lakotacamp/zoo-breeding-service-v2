import logging
from faker import Faker
from uuid import uuid4
from random import choice, randint, uniform, random
from datetime import datetime, timedelta

fake = Faker()
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Potential species set
animal_species = ["Lion", "Tiger", "Elephant", "Giraffe", "Zebra", "Bear"]

# Approximate gestation periods in months
gestation_periods = {
    "Lion": 3,
    "Tiger": 3,
    "Elephant": 22,
    "Giraffe": 15,
    "Zebra": 12,
    "Bear": 6,
}

# Acceptable breeding-age ranges (years)
breeding_age_ranges = {
    "Lion": (4, 12),
    "Tiger": (3, 15),
    "Elephant": (10, 50),
    "Giraffe": (5, 20),
    "Zebra": (3, 10),
    "Bear": (4, 20),
}

# We'll generate more animals here (e.g., 150).
NUM_ANIMALS = 150

def weighted_health_status():
    """
    Returns a health status string, with ~90% chance of Healthy,
    5% chance Slightly Ill, 5% chance Critical.
    """
    r = random()
    if r < 0.90:
        return "Healthy"
    elif r < 0.95:
        return "Slightly Ill"
    else:
        return "Critical"

def generate_age_for_species(sp: str) -> int:
    """
    Attempt to generate an age that falls within the breeding range ~70% of the time,
    and outside ~30% of the time, to increase the number of breed-ready animals.
    """
    min_age, max_age = breeding_age_ranges[sp]
    # 70% chance: pick an age in [min_age, max_age]
    if random() < 0.70:
        # Uniform in breeding range
        return randint(min_age, max_age)
    else:
        # Random in broader range 0-50 (or you can pick any range you like)
        return randint(0, 50)

animals = []
unique_ids = set()

# We'll use round-robin for species to ensure an even distribution
# Alternatively, you could randomize but enforce a near-even distribution.
species_count = len(animal_species)
sexes = ["male", "female"]  # 50/50

for i in range(NUM_ANIMALS):
    # Choose species in a cycle to guarantee roughly equal distribution
    species = animal_species[i % species_count]
    # 50/50 male/female
    sex = sexes[i % 2]  # Alternate: male, female, male, female, etc.
    # If you prefer random but truly 50/50 in total, you could do a separate approach.

    # Generate an age that is more likely to be in the breeding range
    age = generate_age_for_species(species)

    # Weighted health
    health_status = weighted_health_status()

    # ~2% chance pregnant if female:
    preg = "no"
    if sex == "female" and random() < 0.02:
        preg = "yes"

    exp_date = None
    if preg == "yes":
        # gestation_periods[species] * 30 is approximate days
        offset_days = gestation_periods[species] * 30
        exp_date = (datetime.now() + timedelta(days=offset_days)).isoformat()

    # Generate unique UUID
    a_id = str(uuid4())
    while a_id in unique_ids:
        a_id = str(uuid4())
    unique_ids.add(a_id)

    # 1 in 10 might have a previous breeding date
    last_breed_chance = randint(1, 10)
    last_breed_date = None
    if last_breed_chance == 10:
        # 50 to 300 days in the past
        offset_days = randint(50, 300)
        dt = datetime.now() - timedelta(days=offset_days)
        last_breed_date = dt.isoformat()

    # Potential milestone if they're age <= 1 and female.
    default_milestones = []
    if age <= 1 and sex == "female":
        default_milestones = [{
            "name": "Weaning",
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "completed_date": None,
            "notes": "Auto milestone"
        }]

    animals.append({
        "id": a_id,
        "name": fake.first_name(),
        "species": species,
        "sex": sex,
        "age": age,
        "health_status": health_status,
        "pregnant": preg,
        "expected_birth_date": exp_date,
        "last_breeding_date": last_breed_date,
        "birth_weight": None,
        "growth_rate": None,
        "physical_markings": None,
        "parent_ids": [],
        "mortality_status": "Alive",
        "mortality_reason": None,
        "date_of_death": None,
        "milestones": default_milestones
    })

logging.info(f"Generated {len(animals)} animals with a higher proportion of Healthy animals.")

# Predefined parents to ensure some guaranteed older, healthy parents:
p1 = {
    "id": str(uuid4()),
    "name": "Parent1",
    "species": "Lion",
    "sex": "male",
    "age": 5,
    "health_status": "Healthy",
    "pregnant": "no",
    "parent_ids": [],
    "last_breeding_date": (datetime.now() - timedelta(days=200)).isoformat(),
    "birth_weight": None,
    "growth_rate": None,
    "physical_markings": None,
    "mortality_status": "Alive",
    "mortality_reason": None,
    "date_of_death": None,
    "milestones": []
}
p2 = {
    "id": str(uuid4()),
    "name": "Parent2",
    "species": "Lion",
    "sex": "female",
    "age": 6,
    "health_status": "Healthy",
    "pregnant": "no",
    "parent_ids": [],
    "last_breeding_date": (datetime.now() - timedelta(days=200)).isoformat(),
    "birth_weight": None,
    "growth_rate": None,
    "physical_markings": None,
    "mortality_status": "Alive",
    "mortality_reason": None,
    "date_of_death": None,
    "milestones": []
}
animals.extend([p1, p2])

# Build valid breeding pairs
valid_breeding_pairs = []
for a1 in animals:
    for a2 in animals:
        if a1["id"] != a2["id"]:
            if a1["species"] == a2["species"] and a1["sex"] != a2["sex"]:
                rng = breeding_age_ranges[a1["species"]]
                if (rng[0] <= a1["age"] <= rng[1]
                    and rng[0] <= a2["age"] <= rng[1]
                    and a1["health_status"] == "Healthy"
                    and a2["health_status"] == "Healthy"
                    and a1["pregnant"] == "no"
                    and a2["pregnant"] == "no"):
                    valid_breeding_pairs.append((a1, a2))

logging.info(f"Generated {len(valid_breeding_pairs)} valid breeding pairs from the pool of {len(animals)} animals.")

breeding_events = []
used_animals = set()
for pair in valid_breeding_pairs[:20]:
    # Ensure we don't reuse the same animals in multiple events if you want a 1-to-1 scenario:
    if pair[0]["id"] in used_animals or pair[1]["id"] in used_animals:
        continue
    used_animals.update([pair[0]["id"], pair[1]["id"]])

    event_id = str(uuid4())
    occurred_at = fake.date_time_between(start_date="-2y", end_date="now").isoformat()
    
    # Determine if the breeding results in a pregnancy with a high probability
    breeding_success_chance = random()
    outcome = "Successful" if breeding_success_chance < 0.9 else "Failed"

    # If successful and the female is not already pregnant, update her status
    if outcome == "Successful":
        for animal in pair:
            if animal["sex"] == "female" and animal["pregnant"] == "no":
                animal["pregnant"] = "yes"
                # Assign an expected birth date based on species gestation period
                gestation_days = gestation_periods[animal["species"]] * 30
                animal["expected_birth_date"] = (
                    datetime.now() + timedelta(days=gestation_days)
                ).isoformat()
    
    breeding_events.append({
        "id": event_id,
        "parent_1_id": pair[0]["id"],
        "parent_2_id": pair[1]["id"],
        "parent_1_name": pair[0]["name"],
        "parent_2_name": pair[1]["name"],
        "occurred_at": occurred_at,
        "outcome": outcome,
    })

logging.info(f"Generated {len(breeding_events)} breeding events.")

# Generate litters for successful breeding events
litters = []
for evt in breeding_events:
    if evt["outcome"] != "Successful":
        continue  # Skip events that did not result in a pregnancy

    litter_id = str(uuid4())
    sp = next((a["species"] for a in animals if a["id"] == evt["parent_1_id"]), None)
    if not sp:
        continue

    size = randint(1, 5)
    lit_birth_date = fake.date_time_between(start_date="-1y", end_date="now")
    new_lit = {
        "id": litter_id,
        "breeding_id": evt["id"],
        "size": size,
        "birth_date": lit_birth_date,
        "description": f"Litter of {size} healthy offspring",
        "parent_1_id": evt["parent_1_id"],
        "parent_2_id": evt["parent_2_id"],
        "parent_1_name": evt["parent_1_name"],
        "parent_2_name": evt["parent_2_name"],
        "species": sp,
    }
    litters.append(new_lit)

    # Add baby animals to the animal list
    for _ in range(size):
        baby_id = str(uuid4())
        animals.append({
            "id": baby_id,
            "name": fake.first_name(),
            "species": sp,
            "sex": choice(["male", "female"]),
            "age": 0,
            "health_status": "Healthy",
            "pregnant": "no",
            "expected_birth_date": None,
            "last_breeding_date": None,
            "birth_weight": round(uniform(1.0, 5.0), 2),
            "growth_rate": round(uniform(0.5, 1.5), 2),
            "physical_markings": None,
            "parent_ids": [evt["parent_1_id"], evt["parent_2_id"]],
            "mortality_status": "Alive",
            "mortality_reason": None,
            "date_of_death": None,
            "milestones": []
        })

logging.info(f"Generated {len(litters)} litters.")