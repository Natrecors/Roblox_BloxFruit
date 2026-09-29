import os

DATA_DIR = "data"

BOSS_RESPAWNS = {
    "Vice Admiral": 15, 
    "Magma Admiral": 20, 
    "Saber Expert": 30, 
    "Swan": 30
}

AWAKENING_COSTS = {
    "Light": 14500, 
    "Buddha": 14500, 
    "Dough": 18500, 
    "Magma": 14500
}

LEVELING_ROUTE = [
    (1, 14, "Starter Island", "Bandits"),
    (15, 29, "Jungle", "Monkeys / Gorillas"),
    (30, 59, "Pirate Village", "Pirates / Brutes"),
    (60, 89, "Desert", "Desert Bandits"),
    (90, 119, "Frozen Village", "Snow Bandits"),
    (120, 149, "Marine Fortress", "Chief Petty Officers"),
    (150, 189, "Skylands", "Sky Bandits"),
    (190, 274, "Prison", "Prisoners / Wardens"),
    (275, 300, "Colosseum", "Gladiators"),
    (301, 374, "Magma Village", "Military / Magma Admiral"),
    (375, 449, "Underwater City", "Fishman Warriors"),
    (450, 625, "Upper Skylands", "God's Guards"),
    (626, 700, "Fountain City", "Galley Pirates"),
    (700, 850, "Kingdom of Rose (Sea 2)", "Raiders / Mercenaries")
]