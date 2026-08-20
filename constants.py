"""Shared constants for Stone Age Survival.

This file is part of the team baseline.
Feature branches should import these constants instead of redefining them.
"""

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60


# ---------------------------------------------------------------------------
# Hex map
# ---------------------------------------------------------------------------

HEX_SIZE = 38
MAP_COLS = 22
MAP_ROWS = 16

CAMP_POSITION = (5, 4)
START_POSITION = CAMP_POSITION


# ---------------------------------------------------------------------------
# Day / game state
# ---------------------------------------------------------------------------

MAX_DAY_ACTIONS = 6

STATE_DAY = "day"
STATE_NIGHT = "night"
STATE_GAME_OVER = "game_over"


# ---------------------------------------------------------------------------
# Day action costs
# ---------------------------------------------------------------------------

ACTION_MOVE_COST = 1
ACTION_GATHER_COST = 1
ACTION_BUILD_COST = 2
ACTION_CRAFT_COST = 2
ACTION_EAT_COST = 1
ACTION_FIREWOOD_COST = 1


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

RESOURCE_FOOD = "food"
RESOURCE_WOOD = "wood"
RESOURCE_STONE = "stone"
RESOURCE_HIDE = "hide"
TOOL_MAX_DURABILITY = 30
VALID_RESOURCES = (
    RESOURCE_FOOD,
    RESOURCE_WOOD,
    RESOURCE_STONE,
    RESOURCE_HIDE,
)


# ---------------------------------------------------------------------------
# Terrain
# ---------------------------------------------------------------------------

TERRAIN_GRASS = "grass"
TERRAIN_FOREST = "forest"
TERRAIN_ROCK = "rock"
TERRAIN_WATER = "water"

VALID_TERRAINS = (
    TERRAIN_GRASS,
    TERRAIN_FOREST,
    TERRAIN_ROCK,
    TERRAIN_WATER,
)


# ---------------------------------------------------------------------------
# Hidden map tiles
# ---------------------------------------------------------------------------

SPECIAL_REWARD = "reward"
SPECIAL_TRAP = "trap"


# ---------------------------------------------------------------------------
# Survival
# ---------------------------------------------------------------------------

MAX_HEALTH = 100
MAX_ARMOR = 50
MAX_HUNGER = 100

HIDE_ARMOR_BONUS = 25


# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------

BUILD_WALL = "wall"
BUILD_TRAP = "trap"

WALL_MAX_HP = 60
TRAP_MAX_HP = 1


# ---------------------------------------------------------------------------
# Campfire
# ---------------------------------------------------------------------------

CAMPFIRE_MAX_FUEL = 12


# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------

ENEMY_WOLF = "wolf"
ENEMY_BOAR = "boar"
ENEMY_HYENA = "hyena"
ENEMY_BEAR = "bear"
ENEMY_SABERTOOTH = "sabertooth"

PLAYER_BASE_DAMAGE = 10
PLAYER_SPEAR_DAMAGE = 20

TRAP_DAMAGE = 25


# ---------------------------------------------------------------------------
# Daily events
# ---------------------------------------------------------------------------

EVENT_NONE = "none"
EVENT_STORM = "storm"
EVENT_WOLF_TRACKS = "wolf_tracks"
EVENT_MIGRATION = "migration"
EVENT_CAVE = "cave"
