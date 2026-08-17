# ==========================================
# constants.py (Team Baseline - Merged V2)
# ==========================================

# --- System & Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- Hex Map System (Member A) ---
HEX_SIZE = 38
MAP_COLS = 11
MAP_ROWS = 8
CAMP_POSITION = (5, 4)
START_POSITION = CAMP_POSITION

TERRAIN_GRASS = "grass"
TERRAIN_FOREST = "forest"
TERRAIN_ROCK = "rock"
TERRAIN_WATER = "water"

SPECIAL_REWARD = "reward"
SPECIAL_TRAP = "trap"

# --- Resource System (Shared) ---
RESOURCE_FOOD = "food"
RESOURCE_WOOD = "wood"
RESOURCE_STONE = "stone"
RESOURCE_HIDE = "hide"

# --- Day/Night & Action System (Member A) ---
MAX_DAY_ACTIONS = 6
STATE_DAY = "day"
STATE_NIGHT = "night"
STATE_GAME_OVER = "game_over"

ACTION_MOVE_COST = 1
ACTION_GATHER_COST = 1
ACTION_BUILD_COST = 2
ACTION_CRAFT_COST = 2
ACTION_EAT_COST = 1
ACTION_FIREWOOD_COST = 1

# --- Survival System (Member B) ---
MAX_HEALTH = 100
MAX_ARMOR = 50
MAX_HUNGER = 100
HIDE_ARMOR_BONUS = 25

# --- Building System (Member B) ---
BUILD_WALL = "wall"
BUILD_TRAP = "trap"
CAMPFIRE_MAX_FUEL = 12