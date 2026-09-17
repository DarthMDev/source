SUIT_RADII = {'ac': 3.6144388914108276, 'cc': 3.7141129970550537, 'cr': 5.305789232254028, 'dt': 3.8733880519866943,
              'gh': 4.326296091079712, 'pp': 3.5648300647735596, 'le': 5.1406800746917725, 'tw': 4.203859329223633,
              'nc': 4.314185380935669, 'nd': 3.9174678325653076, 'tm': 3.3917577266693115, 'ls': 4.41237998008728,
              'rb': 5.085580348968506, 'tf': 4.314185380935669, 'bf': 3.958986282348633, 'ym': 3.8182884454727173,
              'bc': 3.6329957246780396, 'hh': 4.865181922912598, 'bw': 5.085580348968506, 'bs': 3.9835875034332275,
              'tbc': 5.085580348968506, 'ds': 3.670109272003174, 'b': 3.6237173080444336, 'f': 3.958986282348633,
              'mm': 3.224366307258606, 'mb': 4.595656633377075, 'm': 4.534584045410156, 'mh': 5.085580348968506,
              'p': 3.2433035373687744, 'ms': 3.7628930807113647, 'sc': 3.763087511062622, 'sd': 4.096914768218994}

SUIT_TIERS = (
    ('f', 'bf', 'sc', 'cc'),
    ('p', 'b', 'pp', 'tm'),
    ('ym', 'dt', 'tw', 'nd'),
    ('mm', 'ac', 'bc', 'gh'),
    ('ds', 'bs', 'nc', 'ms'),
    ('hh', 'sd', 'mb', 'tf'),
    ('cr', 'le', 'ls', 'm'),
    ('tbc', 'bw', 'rb', 'mh')
)

GAG_THROW = 0
GAG_SQUIRT = 1
GAGS = {
    GAG_THROW: {'name': 'Whole Cream Pie', 'prop': 'Cream Pie', 'damage': 40,
                'range': 42.0, 'cooldown': 0.85, 'maxAmmo': 20},
    GAG_SQUIRT: {'name': 'Fire Hose', 'prop': 'Fire Hose', 'damage': 30,
                 'range': 28.0, 'cooldown': 0.65, 'maxAmmo': 20},
}


def getGagRange(gagType, power):
    gag = GAGS[gagType]
    power = max(0, min(100, power)) / 100.0
    return 4.0 + (gag['range'] - 4.0) * power

def getCogHp(level):
    level = max(1, int(level))
    return (level + 1) * (level + 2)


ENEMY_ATTACK_RANGE = 6.0
ENEMY_ATTACK_DAMAGE = 5
ENEMY_ATTACK_COOLDOWN = 1.5
ENEMY_FLIGHT_DISTANCE = 80.0
ENEMY_STUCK_TIME = 3.5
ENEMY_FLIGHT_COOLDOWN = 8.0
ENEMY_FLIGHT_OFFSET = 18.0


def getCogAttackDamage(round):
    return ENEMY_ATTACK_DAMAGE
POINTS_PER_HIT = 10
POINTS_PER_KILL = 100

HEALTH_TREASURE_HEAL = 20
HEALTH_TREASURE_RESPAWN = 30.0
HEALTH_TREASURE_PICKUP_RANGE = 5.0

GYRO_AMMO_REFILL_COST = 500
GYRO_AMMO_INTERACT_RANGE = 7.0
WALL_AMMO_REFILL_COST = 250
WALL_AMMO_INTERACT_RANGE = 6.0
