from toontown.strike.DistributedCorporateStrikeAI import DistributedCorporateStrikeAI
from toontown.strike.RoundManagerAI import RoundManagerAI
from toontown.strike import OperationSaveToontownGlobals


class OSTRoundManagerAI(RoundManagerAI):
    SPAWN_RANGES = (
        (6, 6),
        (6, 8),
        (7, 10),
        (8, 12)
    )

    SPAWN_SPHERES = OperationSaveToontownGlobals.SPAWN_SPHERES
    SPAWN_DELAY = (5, 12)
    MAX_ENEMIES = 14
    TIER_CHART = {1: [0], 3: [0, 1], 5: [1, 2], 7: [2, 3],
                  9: [3, 4], 13: [4, 5], 15: [5, 6, 7]}


class DistributedOperationSaveToontownAI(DistributedCorporateStrikeAI):
    DROP_POINTS = OperationSaveToontownGlobals.DROP_POINTS

    ROUND_MANAGER = OSTRoundManagerAI
    WALL_AMMO_STATIONS = OperationSaveToontownGlobals.WALL_AMMO_STATIONS
    HEALTH_TREASURES = OperationSaveToontownGlobals.HEALTH_TREASURES
    GYRO_AMMO_POS = OperationSaveToontownGlobals.GYRO_AMMO_POS
    BARRICADE_SPAWN_SPHERES = OperationSaveToontownGlobals.BARRICADE_SPAWN_SPHERES
