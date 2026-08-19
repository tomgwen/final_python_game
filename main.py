"""
石器時代：荒野求生 - 滑鼠回合制可玩版。
主要操作：
- 左鍵：選擇地圖格 / 點擊右側按鈕 / 點擊敵人攻擊
- 左鍵按住玩家拖曳：預覽最短路徑
- 右鍵：在地圖格開啟情境選單
- 白天 20 回合；成功操作消耗 1 回合，歸零立即入夜
- 夜晚 20 回合；每次玩家行動後敵人移動/攻擊
- 玩家攻擊/伐木會播放 Sprite Sheet 連續砍擊動畫
"""

from __future__ import annotations

import math
import os
import random

import intro
import game_over
import day_transition
from display_manager import DisplayManager
from floating_notifications import FloatingNotificationManager

import pygame
from camera import Camera
from hex_coordinates import (
    axial_to_world_pixel,
    world_to_axial_nearest,
)

from visuals import VisualManager
from audio_manager import audio
from building import BuildingManager
from campfire import Campfire
from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    CAMPFIRE_MAX_FUEL,
    CAMP_POSITION,
    ENEMY_BOAR,
    ENEMY_WOLF,
    FPS,
    MAP_COLS,
    MAP_ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from enemy import (
    calculate_player_damage,
    claim_loot,
    create_enemy,
    damage_enemy,
)
from inventory import Inventory
from pathfinding import find_hex_path
from recipe_catalog import RECIPE_CATALOG
from survival import SurvivalStats
from tutorial_controller import TutorialController
from ui_layout import get_game_viewport, get_right_hud_rect

# =========================================================
# 基本設定
# =========================================================
DAY_TURNS = 20
NIGHT_TURNS = 20
DEATH_REASON_WOLF = "你遭到狼群攻擊而死亡。"
DEATH_REASON_BOAR = "你遭到野豬攻擊而死亡。"
DEATH_REASON_HUNGER = "你因飢餓與傷勢倒下了。"
DEATH_REASON_COLD = "你遠離營火，在寒冷與黑暗中倒下了。"

HEX_SIZE = 30
MAP_ORIGIN_X = 62
MAP_ORIGIN_Y = 140

MAP_PANEL = pygame.Rect(20, 78, 790, 500)
HUD_PANEL = pygame.Rect(830, 78, 430, 622)
LOG_PANEL = pygame.Rect(20, 592, 790, 108)

HEX_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)

# 攻擊動畫設定
ATTACK_FRAME_WIDTH = 48
ATTACK_FRAME_HEIGHT = 48
ATTACK_FRAME_COUNT = 4
ATTACK_FRAME_DURATION = 120  # 每幀停留 120ms，總共約 0.48 秒

# =========================================================
# 文字
# =========================================================
TERRAIN_NAMES = {
    "grass": "草地",
    "forest": "森林",
    "rock": "岩地",
    "water": "水域",
}

RESOURCE_NAMES = {
    "food": "食物",
    "wood": "木材",
    "stone": "石頭",
    "hide": "獸皮",
}

# =========================================================
# 顏色
# =========================================================
BG = (17, 19, 22)
TOP = (23, 26, 29)
PANEL = (29, 32, 36)
PANEL_2 = (38, 42, 47)
BORDER = (66, 71, 76)

TEXT = (239, 235, 221)
MUTED = (168, 169, 165)
GOLD = (229, 157, 67)
GOLD_LIGHT = (255, 204, 108)

RED = (205, 75, 68)
GREEN = (89, 166, 99)
BLUE = (75, 127, 174)

GRASS = (86, 120, 71)
FOREST = (42, 80, 49)
ROCK = (103, 103, 99)
WATER = (49, 90, 128)
FOG = (31, 34, 37)
BLACK = (20, 20, 20)

# =========================================================
# 字型
# =========================================================
def create_fonts() -> dict[str, pygame.font.Font]:
    font_path = None

    for path in (
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msjhbd.ttc",
        r"C:\Windows\Fonts\mingliu.ttc",
    ):
        if os.path.exists(path):
            font_path = path
            break

    if font_path is None:
        for name in (
            "Microsoft JhengHei",
            "Microsoft JhengHei UI",
            "Noto Sans CJK TC",
        ):
            match = pygame.font.match_font(name)
            if match:
                font_path = match
                break

    def make(size: int, bold: bool = False) -> pygame.font.Font:
        font = (
            pygame.font.Font(font_path, size)
            if font_path
            else pygame.font.Font(None, size)
        )
        font.set_bold(bold)
        return font

    return {
        "title": make(38, True),
        "heading": make(23, True),
        "body": make(18),
        "small": make(15),
        "tiny": make(13),
    }

# =========================================================
# 六角地圖
# =========================================================
def valid_position(position: tuple[int, int]) -> bool:
    q, r = position
    return 0 <= q < MAP_COLS and 0 <= r < MAP_ROWS

def neighbors(position: tuple[int, int]) -> list[tuple[int, int]]:
    q, r = position
    result = []
    for dq, dr in HEX_DIRECTIONS:
        candidate = (q + dq, r + dr)
        if valid_position(candidate):
            result.append(candidate)
    return result

def hex_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    q1, r1 = a
    q2, r2 = b
    return (
        abs(q1 - q2)
        + abs(q1 + r1 - q2 - r2)
        + abs(r1 - r2)
    ) // 2

def axial_to_pixel(
    position: tuple[int, int],
    camera: Camera | None = None,
) -> tuple[int, int]:
    world_pos = axial_to_world_pixel(
        position,
        HEX_SIZE,
        (MAP_ORIGIN_X, MAP_ORIGIN_Y),
    )

    if camera is not None:
        world_pos = camera.world_to_screen(world_pos)

    return int(world_pos[0]), int(world_pos[1])

def hex_points(center: tuple[int, int]) -> list[tuple[int, int]]:
    cx, cy = center
    return [
        (
            int(cx + HEX_SIZE * math.cos(math.radians(30 + i * 60))),
            int(cy + HEX_SIZE * math.sin(math.radians(30 + i * 60))),
        )
        for i in range(6)
    ]

def tile_at_pixel(
    mouse_pos: tuple[int, int],
    camera: Camera | None = None,
    viewport_rect: pygame.Rect | None = None,
) -> tuple[int, int] | None:
    if viewport_rect is not None:
        active_viewport = viewport_rect
    else:
        surface = pygame.display.get_surface()
        active_viewport = (
            get_game_viewport(surface)
            if surface is not None
            else MAP_PANEL
        )

    if not active_viewport.collidepoint(mouse_pos):
        return None

    world_pos: tuple[float, float] = mouse_pos

    if camera is not None:
        world_pos = camera.screen_to_world(mouse_pos)

    return world_to_axial_nearest(
        world_pos,
        HEX_SIZE,
        MAP_COLS,
        MAP_ROWS,
        (MAP_ORIGIN_X, MAP_ORIGIN_Y),
    )
    return None

    world_pos: tuple[float, float] = mouse_pos

    if camera is not None:
        world_pos = camera.screen_to_world(mouse_pos)

    return world_to_axial_nearest(
        world_pos,
        HEX_SIZE,
        MAP_COLS,
        MAP_ROWS,
        (MAP_ORIGIN_X, MAP_ORIGIN_Y),
    )

# =========================================================
# 世界生成
# =========================================================
def create_world() -> tuple[dict, dict]:
    rng = random.Random(7)
    terrain: dict[tuple[int, int], str] = {}
    resources: dict[tuple[int, int], int] = {}
    
    for r in range(MAP_ROWS):
        for q in range(MAP_COLS):
            position = (q, r)
            roll = rng.random()
            if roll < 0.10:
                kind = "water"
            elif roll < 0.38:
                kind = "forest"
            elif roll < 0.58:
                kind = "rock"
            else:
                kind = "grass"
            
            if position == CAMP_POSITION:
                kind = "grass"
                
            terrain[position] = kind
            resources[position] = 0 if kind == "water" else 6
            
    return terrain, resources

# =========================================================
# Game 核心邏輯
# =========================================================
class Game:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.terrain, self.resources = create_world()

        # 記錄每一格資源在哪一天被採集殆盡。
        # key = tile, value = depleted day
        self.resource_depleted_day: dict[tuple[int, int], int] = {}

        self.inventory = Inventory()
        self.survival = SurvivalStats()
        self.buildings = BuildingManager()
        primary_campfire = Campfire(CAMP_POSITION)

        # 所有營火以位置為 key 儲存。
        self.campfires: dict[tuple[int, int], Campfire] = {
            CAMP_POSITION: primary_campfire
        }

        # 保留舊的 self.campfire，避免現有功能受到影響。
        self.campfire = primary_campfire
        self.discovered: set[tuple[int, int]] = set()

        self.player = CAMP_POSITION
        self.selected_tile = CAMP_POSITION
        self.reveal_around(CAMP_POSITION)

        self.day = 1
        self.phase = "day"
        self.day_turns_left = DAY_TURNS
        self.night_turns_left = 0
        self.death_reason: str | None = None
        self.completed_day: int | None = None

        self.has_spear = False
        self.has_axe = False
        self.has_pickaxe = False
        self.enemies = []

        # =====================================================
        # 攻擊動畫狀態 (明確加入 attack_frame)
        # =====================================================
        self.attack_animating = False
        self.attack_anim_start_time = 0
        self.attack_frame = 0
        self.attack_anim_row = 6
        self.attack_target = None
        self.attack_enemy = None

        self.floating_icon_type = None
        self.floating_icon_tile = None
        self.floating_icon_amount = 0
        self.floating_icon_start_time = 0

        self.logs = [
            "你在石器時代的荒野中醒來。",
            "白天共有 20 回合。右鍵點地圖格開始行動。",
        ]

    def campfire_at(self, tile: tuple[int, int]) -> Campfire | None:
        """Return the campfire at tile, if one exists."""
        return self.campfires.get(tile)
    def is_near_campfire(self, campfire: Campfire) -> bool:
        """Return True when the player is on or adjacent to the campfire."""
        return hex_distance(self.player, campfire.position) <= 1
    def is_in_lit_campfire_range(
        self,
        tile: tuple[int, int],
        radius: int = 4,
    ) -> bool:
        return any(
            hex_distance(tile, campfire.position) <= radius
            for campfire in self.lit_campfires()
        )
    def lit_campfires(self) -> list[Campfire]:
        """Return all currently lit campfires."""
        return [
            campfire
            for campfire in self.campfires.values()
            if campfire.lit
        ]
    def reveal_around(self, tile: tuple[int, int]) -> None:
        """探索目前格以及周圍相鄰的六角格。"""
        if tile in self.terrain:
            self.discovered.add(tile)

        for neighbor in neighbors(tile):
            if neighbor in self.terrain:
                self.discovered.add(neighbor)

    def log(self, message: str) -> None:
        self.logs.append(message)
        self.logs = self.logs[-7:]

    # =====================================================
    # 白天
    # =====================================================
    def apply_hunger_turn_effect(self) -> bool:
        """Apply hunger-based health change once for the current turn."""
        health_change = self.survival.apply_hunger_health_effect()

        if health_change > 0:
            self.log(f"飢餓度低，恢復 {health_change} HP。")

        elif health_change < 0:
            self.log(f"飢餓造成 {-health_change} 點生命損失。")

        if self.survival.is_dead():
            self.phase = "game_over"
            self.log("你因飢餓與虛弱倒下了。")
            self.death_reason = DEATH_REASON_HUNGER
            return False

        return True
    def spend_day_turn(self) -> None:
        if self.phase != "day":
            return

        self.day_turns_left = max(0, self.day_turns_left - 1)

        if not self.apply_hunger_turn_effect():
            return

        if self.day_turns_left == 0:
            self.log("白天 20 回合已結束，夜幕降臨！")
            self.start_night()

    def can_move_to(self, target: tuple[int, int]) -> bool:
        return (
            self.phase == "day"
            and target in neighbors(self.player)
            and self.terrain[target] != "water"
        )

    def move_to(self, target: tuple[int, int]) -> bool:
        if not self.can_move_to(target):
            self.log("只能移動到相鄰且可通行的六角格。")
            return False
        self.player = target
        self.selected_tile = target
        self.reveal_around(target)
        self.log(f"移動到 {target}。")
        self.spend_day_turn()
        return True

    def can_move_night_to(self, target: tuple[int, int]) -> bool:
        if self.phase != "night":
            return False
        if target not in neighbors(self.player):
            return False
        if self.terrain[target] == "water":
            return False
        if self.enemies_at(target):
            return False
        return True

    def move_night_to(self, target: tuple[int, int]) -> bool:
        if not self.can_move_night_to(target):
            self.log("夜晚只能移動到相鄰、可通行且沒有敵人的格子。")
            return False
        self.player = target
        self.selected_tile = target
        self.reveal_around(target)
        self.log(f"你在夜色中移動到 {target}。")
        self.advance_night_turn()
        return True

    def path_is_walkable(self, tile: tuple[int, int]) -> bool:
        return self.terrain[tile] != "water"

    def preview_drag_path(self, target: tuple[int, int]) -> list[tuple[int, int]] | None:
        if self.phase not in ("day", "night"):
            return None
        blocked: set[tuple[int, int]] = set()
        if self.phase == "night":
            blocked = {enemy.position for enemy in self.alive_enemies()}
            blocked.discard(self.player)
        return find_hex_path(
            self.player,
            target,
            is_walkable=self.path_is_walkable,
            blocked=blocked,
        )

    def execute_drag_path(self, path: list[tuple[int, int]] | None) -> bool:
        if not path:
            return False
        if path[0] != self.player:
            return False
        movement_cost = len(path) - 1
        if movement_cost <= 0:
            return False

        if self.phase == "day":
            if movement_cost > self.day_turns_left:
                self.log(f"路徑需要 {movement_cost} 回合，但目前只剩 {self.day_turns_left} 回合。")
                return False
            destination = path[-1]
            for step in path[1:]:
                if self.phase != "day":
                    break
                if not self.move_to(step):
                    return False
            if self.player == destination:
                self.log(f"快速移動完成，共消耗 {movement_cost} 回合。")
            return True

        if self.phase == "night":
            if movement_cost > self.night_turns_left:
                self.log(f"夜間路徑需要 {movement_cost} 回合，但目前只剩 {self.night_turns_left} 回合。")
                return False
            moved = False
            for step in path[1:]:
                if self.phase != "night":
                    break
                if not self.can_move_night_to(step):
                    self.log("路徑被敵人阻擋，快速移動中止。")
                    break
                if not self.move_night_to(step):
                    break
                moved = True
                if self.survival.is_dead():
                    break
            return moved
        return False

    # =====================================================
    # 資源
    # =====================================================
    def resource_type_at(self, tile: tuple[int, int]) -> str | None:
        terrain = self.terrain[tile]
        if terrain == "forest":
            return "wood"
        if terrain == "rock":
            return "stone"
        if terrain == "grass":
            return "food"
        return None

    def resource_amount_at(self, tile: tuple[int, int]) -> int:
        return max(0, self.resources.get(tile, 0))

    def is_tile_depleted(self, tile: tuple[int, int]) -> bool:
        resource_type = self.resource_type_at(tile)
        if resource_type is None:
            return False
        return self.resource_amount_at(tile) <= 0
    
    def regenerate_resources(self) -> None:
        for tile, depleted_day in list(self.resource_depleted_day.items()):
            if self.day - depleted_day >= 2:
                self.resources[tile] = 6
                del self.resource_depleted_day[tile]

    def can_gather_at(self, tile: tuple[int, int]) -> bool:
        return (
            self.phase == "day"
            and tile == self.player
            and self.resources.get(tile, 0) > 0
            and self.resource_type_at(tile) is not None
        )

    def gather_at(self, tile: tuple[int, int]) -> bool:
        if not self.can_gather_at(tile):
            self.log("必須站在有資源的格子上才能採集。")
            return False
            
        resource = self.resource_type_at(tile)
        amount = 1
        if resource == "wood" and self.has_axe:
            amount = 2
        elif resource == "stone" and self.has_pickaxe:
            amount = 2
        amount = min(amount, self.resources[tile])
        
        self.resources[tile] -= amount

        if self.resources[tile] == 0:
            self.resource_depleted_day[tile] = self.day

        self.inventory.add(resource, amount)
        self.log(f"採集到 {amount} 個{RESOURCE_NAMES[resource]}。")
        
        # 先扣除白天回合
        self.spend_day_turn()

        # =====================================================
        # 🌟 採集時，觸發角色砍擊動作與浮動 Icon 特效！
        # =====================================================
        self.attack_target = tile
        self.attack_enemy = None
        self.attack_animating = True
        self.attack_frame = 0
        self.attack_anim_start_time = pygame.time.get_ticks()
        self.attack_anim_row = 6  # 用正面往下砍的動作來採集
        
        # 設定浮動 Icon 狀態
        self.floating_icon_type = resource  # 會是 "wood", "food", 或 "stone"
        self.floating_icon_tile = tile
        self.floating_icon_amount = amount
        self.floating_icon_start_time = pygame.time.get_ticks()
        
        return True

    # =====================================================
    # 建造
    # =====================================================
    def can_build_at(self, tile: tuple[int, int]) -> bool:
        return (
            self.phase == "day"
            and tile in self.discovered
            and tile != CAMP_POSITION
            and self.terrain[tile] != "water"
            and hex_distance(self.player, tile) <= 2
            and self.buildings.get_building(tile) is None
            and self.campfire_at(tile) is None
        )

    def build_at(self, building_type: str, tile: tuple[int, int]) -> bool:
        if not self.can_build_at(tile):
            self.log("這個位置無法建造；必須是已探索、距離 2 格內的空地。")
            return False
        success = self.buildings.build(building_type, tile, self.inventory)
        if not success:
            if building_type == BUILD_WALL:
                self.log("木牆需要 3 木材。")
            else:
                self.log("陷阱需要 2 木材 + 1 石頭。")
            return False
        name = "木牆" if building_type == BUILD_WALL else "陷阱"
        self.log(f"在 {tile} 建造{name}。")
        self.spend_day_turn()
        return True
    def can_build_campfire_at(self, tile: tuple[int, int]) -> bool:
        return (
            self.phase == "day"
            and tile in self.discovered
            and tile in self.terrain
            and self.terrain[tile] != "water"
            and hex_distance(self.player, tile) <= 2
            and self.buildings.get_building(tile) is None
            and self.campfire_at(tile) is None
        )


    def build_campfire_at(self, tile: tuple[int, int]) -> bool:
        if not self.can_build_campfire_at(tile):
            self.log("這個位置無法建造營火；必須是已探索、距離 2 格內的空地。")
            return False

        cost = {
            "wood": 3,
            "stone": 2,
        }

        if not self.inventory.spend(cost):
            self.log("營火需要 3 木材 + 2 石頭。")
            return False

        self.campfires[tile] = Campfire(tile)

        self.log(f"在 {tile} 建造營火。")
        self.spend_day_turn()
        return True
    # =====================================================
    # 生存 / 製作
    # =====================================================
    def eat(self) -> bool:
        if self.phase != "day":
            return False
        if not self.survival.eat(self.inventory):
            self.log("背包裡沒有足夠食物。")
            return False
        self.log("吃下一份食物，飢餓值降低。")
        self.spend_day_turn()
        return True

    def add_firewood_day(self, campfire: Campfire | None = None) -> bool:
        if self.phase != "day":
            return False

        target_campfire = campfire if campfire is not None else self.campfire

        if not self.is_near_campfire(target_campfire):
            self.log("你必須在營火一格範圍內才能補充或重新點燃營火。")
            return False

        if target_campfire.lit and target_campfire.fuel >= CAMPFIRE_MAX_FUEL:
            self.log("營火燃料已滿。")
            return False

        success = (
            target_campfire.add_fuel(self.inventory)
            if target_campfire.lit
            else target_campfire.relight(self.inventory)
        )

        if not success:
            self.log("需要木材才能補充或重新點燃營火。")
            return False

        self.log(f"營火燃料目前為 {target_campfire.fuel}/{CAMPFIRE_MAX_FUEL}。")
        self.spend_day_turn()
        return True

    def craft_spear(self) -> bool:
        if self.phase != "day":
            return False
        if self.has_spear:
            self.log("你已經擁有石矛。")
            return False
        if not self.inventory.spend({"wood": 2, "stone": 1}):
            self.log("石矛需要 2 木材 + 1 石頭。")
            return False
        self.has_spear = True
        self.log("製作石矛成功！攻擊力提升。")
        self.spend_day_turn()
        return True

    def craft_axe(self) -> bool:
        if self.phase != "day":
            return False
        if self.has_axe:
            self.log("你已經擁有石斧。")
            return False
        if not self.inventory.spend({"wood": 1, "stone": 2}):
            self.log("石斧需要 1 木材 + 2 石頭。")
            return False
        self.has_axe = True
        self.log("製作石斧成功！採木效率提升。")
        self.spend_day_turn()
        return True

    def craft_pickaxe(self) -> bool:
        if self.phase != "day":
            return False
        if self.has_pickaxe:
            self.log("你已經擁有石鎬。")
            return False
        if not self.inventory.spend({"wood": 2, "stone": 2}):
            self.log("石鎬需要 2 木材 + 2 石頭。")
            return False
        self.has_pickaxe = True
        self.log("製作石鎬成功！採石效率提升。")
        self.spend_day_turn()
        return True

    def craft_armor(self) -> bool:
        if self.phase != "day":
            return False
        if not self.inventory.spend({"hide": 2, "stone": 1}):
            self.log("獸皮護甲需要 2 獸皮 + 1 石頭。")
            return False
        self.survival.add_armor(25)
        self.log("製作獸皮護甲成功！護甲 +25。")
        self.spend_day_turn()
        return True

    # =====================================================
    # 夜晚開始
    # =====================================================
    def start_night(self) -> None:
        if self.phase != "day":
            return
        self.selected_tile = self.player
        self.survival.apply_daily_hunger()
        
        if self.survival.is_dead():
            self.phase = "game_over"
            self.log("你因飢餓與傷勢倒下了。")
            return
            
        self.phase = "night"
        self.night_turns_left = NIGHT_TURNS
        self.spawn_enemies()
        
        wolves = sum(1 for enemy in self.enemies if enemy.enemy_type == ENEMY_WOLF)
        boars = sum(1 for enemy in self.enemies if enemy.enemy_type == ENEMY_BOAR)
        self.log(f"夜晚開始：{wolves} 隻狼、{boars} 隻野豬從營地外圍的荒野中出現！")

    def spawn_enemies(self) -> None:
        wolf_count = min(3 + self.day, 7)
        boar_count = 0 if self.day < 2 else min(1 + (self.day - 2) // 2, 3)
        total = wolf_count + boar_count

        spawn_min_distance = 6
        spawn_max_distance = 9

        candidates: list[tuple[int, int]] = []

        for r in range(MAP_ROWS):
            for q in range(MAP_COLS):
                tile = (q, r)

                if tile == CAMP_POSITION:
                    continue

                if self.terrain[tile] == "water":
                    continue

                distance = hex_distance(tile, CAMP_POSITION)

                if spawn_min_distance <= distance <= spawn_max_distance:
                    candidates.append(tile)

        rng = random.Random(1000 + self.day)
        rng.shuffle(candidates)

        if not candidates:
            self.enemies = []
            return

        if len(candidates) < total:
            positions = [
                rng.choice(candidates)
                for _ in range(total)
            ]
        else:
            positions = candidates[:total]

        self.enemies = []
        index = 0

        for _ in range(wolf_count):
            self.enemies.append(
                create_enemy(
                    ENEMY_WOLF,
                    positions[index],
                )
            )
            index += 1

        for _ in range(boar_count):
            self.enemies.append(
                create_enemy(
                    ENEMY_BOAR,
                    positions[index],
                )
            )
            index += 1

    def alive_enemies(self):
        return [enemy for enemy in self.enemies if enemy.alive]

    def enemies_at(self, tile: tuple[int, int]):
        return [enemy for enemy in self.enemies if enemy.alive and enemy.position == tile]

    # =====================================================
    # 戰利品
    # =====================================================
    def collect_loot(self, enemy) -> None:
        loot = claim_loot(enemy)
        for resource, amount in loot.items():
            self.inventory.add(resource, amount)
        if loot:
            loot_text = "、".join(
                f"{RESOURCE_NAMES.get(resource, resource)} +{amount}"
                for resource, amount in loot.items()
            )
            self.log(f"擊敗敵人，獲得 {loot_text}。")

    # =====================================================
    # 玩家攻擊 (只負責設定動畫狀態)
    # =====================================================
    def attack_enemy_at(self, tile: tuple[int, int]) -> bool:
        if self.phase != "night":
            return False
        if self.attack_animating:
            self.log("攻擊動作尚未完成。")
            return False

        enemies = self.enemies_at(tile)
        if not enemies:
            self.log("這個格子沒有可以攻擊的敵人。")
            return False

        attack_range = 2 if self.has_spear else 1
        if hex_distance(self.player, tile) > attack_range:
            self.log(f"敵人距離太遠；目前攻擊距離為 {attack_range} 格。")
            return False

        enemy = enemies[0]

        # 判斷攻擊方向
        player_pixel = axial_to_pixel(self.player)
        target_pixel = axial_to_pixel(tile)
        dx = target_pixel[0] - player_pixel[0]
        dy = target_pixel[1] - player_pixel[1]

        if dy > 12:
            self.attack_anim_row = 6   # 往下 / 正面
        elif dy < -12:
            self.attack_anim_row = 8   # 往上 / 背面
        else:
            self.attack_anim_row = 7   # 左右 / 側面

        # 記錄本次攻擊狀態（正式進入攻擊狀態）
        self.attack_target = tile
        self.attack_enemy = enemy
        self.attack_animating = True
        self.attack_frame = 0
        self.attack_anim_start_time = pygame.time.get_ticks()
        
        return True

    # =====================================================
    # 攻擊動畫結算 (動畫播滿 4 幀後才呼叫)
    # =====================================================
    def finish_attack_animation(self) -> None:
        if not self.attack_animating:
            return

        enemy = self.attack_enemy
        
        # 清除攻擊動畫狀態
        self.attack_animating = False
        self.attack_anim_start_time = 0
        self.attack_frame = 0
        self.attack_target = None
        self.attack_enemy = None
        
        # 防呆：如果是砍樹 (enemy 為 None)，動畫播完直接結束，不結算傷害
        if enemy is None:
            return

        # 實際傷害結算
        damage = calculate_player_damage(self.has_spear)
        defeated = damage_enemy(enemy, damage)

        name = "狼" if enemy.enemy_type == ENEMY_WOLF else "野豬"
        self.log(f"你攻擊{name}，造成 {damage} 點傷害。")

        if defeated:
            self.collect_loot(enemy)

        # 動畫完成後才消耗夜晚回合與觸發敵人行動
        self.advance_night_turn()

    # =====================================================
    # 夜晚其他行動
    # =====================================================
    def add_firewood_night(self, campfire: Campfire | None = None) -> bool:
        if self.phase != "night":
            return False

        target_campfire = campfire if campfire is not None else self.campfire

        if not self.is_near_campfire(target_campfire):
            self.log("你必須在營火一格範圍內才能補充或重新點燃營火。")
            return False

        if target_campfire.lit and target_campfire.fuel >= CAMPFIRE_MAX_FUEL:
            self.log("營火燃料已滿。")
            return False

        success = (
            target_campfire.add_fuel(self.inventory)
            if target_campfire.lit
            else target_campfire.relight(self.inventory)
        )

        if not success:
            self.log("沒有木材，無法處理營火。")
            return False

        self.log(f"你處理了營火，目前燃料 {target_campfire.fuel}/{CAMPFIRE_MAX_FUEL}。")
        self.advance_night_turn()
        return True

    def pass_night_turn(self) -> bool:
        if self.phase != "night":
            return False
        if self.attack_animating:
            return False
        self.log("你選擇等待一回合。")
        self.advance_night_turn()
        return True

    # =====================================================
    # 夜晚回合推進與敵人 AI
    # =====================================================
    def apply_campfire_night_effects(self) -> None:
        # 玩家若不在任何點燃營火的 4 格範圍內，直接失去 1 HP。
        if not self.is_in_lit_campfire_range(self.player):
            self.survival.health = max(0, self.survival.health - 1)
            self.log("你遠離營火，在黑暗與寒冷中失去 1 HP。")
            if self.survival.is_dead():
                self.death_reason = DEATH_REASON_COLD

        # 所有位於任一點燃營火範圍內的敵人受到 2 點傷害。
        for enemy in list(self.alive_enemies()):
            if not self.is_in_lit_campfire_range(enemy.position):
                continue

            defeated = damage_enemy(enemy, 2)

            name = "野豬" if enemy.enemy_type == ENEMY_BOAR else "狼"
            self.log(f"{name}受到營火灼熱影響，失去 2 HP。")

            if defeated:
                self.collect_loot(enemy)
    def advance_night_turn(self) -> None:
        if self.phase != "night":
            return

        # 夜晚環境 / 營火效果
        self.apply_campfire_night_effects()

        # 如果已經因夜晚環境傷害死亡，就不要再繼續回合。
        if self.survival.is_dead():
            self.phase = "game_over"
            self.log("你倒在了黑暗與寒冷中。")
            return

        # 每個夜晚回合套用一次飢餓造成的回血 / 扣血。
        if not self.apply_hunger_turn_effect():
            return

        self.night_turns_left = max(0, self.night_turns_left - 1)

        # 敵人行動
        self.enemy_phase()

        if self.phase != "night":
            return

        # 所有營火各消耗 1 點燃料
        for campfire in self.campfires.values():
            was_lit = campfire.lit

            campfire.consume(1)

            if was_lit and not campfire.lit:
                self.log(f"{campfire.position} 的營火熄滅了。")

        if self.survival.is_dead():
            self.phase = "game_over"
            self.log("你倒在了營地中。")
            return

        if not self.alive_enemies():
            self.log("所有敵人都被擊退，黎明提早到來。")
            self.finish_night()
            return

        if self.night_turns_left == 0:
            self.log("夜晚 20 回合結束，剩餘敵人撤退。")
            self.finish_night()
    def enemy_target(self, enemy) -> tuple[int, int]:
        player_detection_radius = 5

        if hex_distance(enemy.position, self.player) <= player_detection_radius:
            return self.player

        return CAMP_POSITION
    def enemy_phase(self) -> None:
        for enemy in list(self.alive_enemies()):
            if not enemy.alive:
                continue
            if enemy.position == self.player:
                self.enemy_attack_player(enemy)
                if self.survival.is_dead():
                    return
                continue
                
            for _ in range(enemy.move_range):
                keep_moving = self.enemy_step(enemy)
                if not enemy.alive:
                    break
                if enemy.position == self.player:
                    self.enemy_attack_player(enemy)
                    break
                if not keep_moving:
                    break
                    
            if self.survival.is_dead():
                return

    def enemy_step(self, enemy) -> bool:
        target_position = self.enemy_target(enemy)

        if enemy.position == target_position:
            return False

        current_distance = hex_distance(
            enemy.position,
            target_position,
        )
        candidates = []
        for candidate in neighbors(enemy.position):
            if self.terrain[candidate] == "water":
                continue
            candidate_distance = hex_distance(
                candidate,
                target_position,
            )
            if candidate_distance >= current_distance:
                continue
            if (
                enemy.enemy_type == ENEMY_WOLF
                and self.is_in_lit_campfire_range(candidate)
            ):
                continue
            candidates.append(candidate)
            
        if not candidates:
            return False
            
        candidates.sort(
            key=lambda tile: (
                hex_distance(tile, target_position),
                tile[0],
                tile[1],
            )
        )
        target = candidates[0]
        
        building = self.buildings.get_building(target)
        if building is not None and building.building_type == BUILD_WALL:
            wall_damage = 25 if enemy.enemy_type == ENEMY_BOAR else 10
            position = building.position
            self.buildings.damage_building(position, wall_damage)
            
            name = "野豬" if enemy.enemy_type == ENEMY_BOAR else "狼"
            remaining = self.buildings.get_building(position)
            if remaining is None:
                self.log(f"{name}摧毀了 {position} 的木牆！")
            else:
                self.log(f"{name}撞擊木牆，牆剩 {remaining.hp} HP。")
            return False
            
        enemy.position = target
        building = self.buildings.get_building(target)
        if building is not None and building.building_type == BUILD_TRAP and building.active:
            if self.buildings.trigger_trap(target):
                defeated = damage_enemy(enemy, 25)
                name = "野豬" if enemy.enemy_type == ENEMY_BOAR else "狼"
                self.log(f"{name}踩中陷阱，受到 25 點傷害！")
                if defeated:
                    self.collect_loot(enemy)
                    return False
                if enemy.enemy_type == ENEMY_WOLF:
                    return False
        return True

    def enemy_attack_player(self, enemy) -> None:
        health_lost = self.survival.take_damage(enemy.damage)
        name = "野豬" if enemy.enemy_type == ENEMY_BOAR else "狼"

        if enemy.position == self.player:
            self.log(f"{name}撲向你！生命損失 {health_lost}。")
        else:
            self.log(f"{name}突破營地防線！生命損失 {health_lost}。")

        if self.survival.is_dead():
            if enemy.enemy_type == ENEMY_WOLF:
                self.death_reason = DEATH_REASON_WOLF
            elif enemy.enemy_type == ENEMY_BOAR:
                self.death_reason = DEATH_REASON_BOAR

    def finish_night(self) -> None:
        completed_day = self.day

        self.enemies = []
        self.day += 1
        self.completed_day = completed_day
        self.regenerate_resources()
        self.phase = "day"
        self.day_turns_left = DAY_TURNS
        self.night_turns_left = 0

        self.selected_tile = self.player
        self.reveal_around(self.player)

        # 清除任何殘留動畫
        self.attack_animating = False
        self.attack_anim_start_time = 0
        self.attack_frame = 0
        self.attack_target = None
        self.attack_enemy = None

        self.log(f"太陽升起，第 {self.day} 天開始。你重新獲得 20 回合。")

    # =====================================================
    # 右鍵情境選單
    # =====================================================
    def context_actions(self, tile: tuple[int, int]) -> list[tuple[str, str, bool]]:
        if self.phase == "day":
            actions = [
                ("move", "移動到這裡", self.can_move_to(tile)),
                ("gather", "採集這裡", self.can_gather_at(tile)),
                (
                    "wall",
                    "建造木牆（3 木材）",
                    self.can_build_at(tile)
                    and self.inventory.has({"wood": 3}),
                ),
                (
                    "trap",
                    "建造陷阱（2 木材 + 1 石頭）",
                    self.can_build_at(tile)
                    and self.inventory.has({"wood": 2, "stone": 1}),
                ),
                (
                    "campfire_build",
                    "建造營火（3 木材 + 2 石頭）",
                    self.can_build_campfire_at(tile)
                    and self.inventory.has({"wood": 3, "stone": 2}),
                ),
            ]

            campfire = self.campfire_at(tile)

            if campfire is not None:
                fire_label = "補充 1 木材" if campfire.lit else "重新點燃"
                actions.append(
                    (
                        "fire",
                        fire_label,
                        self.is_near_campfire(campfire)
                        and self.inventory.get("wood") > 0
                        and (not campfire.lit or campfire.fuel < CAMPFIRE_MAX_FUEL),
                    )
                )

            return actions
        if self.phase == "night":
            enemies = self.enemies_at(tile)
            attack_range = 2 if self.has_spear else 1

            can_attack = (
                bool(enemies)
                and hex_distance(self.player, tile) <= attack_range
                and not self.attack_animating
            )

            actions = [
                (
                    "night_move",
                    "移動到這裡",
                    self.can_move_night_to(tile)
                    and not self.attack_animating,
                ),
                (
                    "attack",
                    "攻擊這個敵人",
                    can_attack,
                ),
            ]

            campfire = self.campfire_at(tile)

            if campfire is not None:
                fire_label = "補充 1 木材" if campfire.lit else "重新點燃"
                actions.append(
                    (
                        "fire",
                        fire_label,
                        self.is_near_campfire(campfire)
                        and self.inventory.get("wood") > 0
                        and (not campfire.lit or campfire.fuel < CAMPFIRE_MAX_FUEL)
                        and not self.attack_animating,
                    )
                )

            actions.append(
                (
                    "wait",
                    "結束這個夜晚回合",
                    not self.attack_animating,
                )
            )

            return actions
    def execute_context_action(self, action: str, tile: tuple[int, int]) -> None:
        if action == "move":
            self.move_to(tile)
        elif action == "night_move":
            self.move_night_to(tile)
        elif action == "gather":
            self.gather_at(tile)
        elif action == "wall":
            self.build_at(BUILD_WALL, tile)
        elif action == "trap":
            self.build_at(BUILD_TRAP, tile)
        elif action == "campfire_build":
            self.build_campfire_at(tile)
        elif action == "attack":
            self.attack_enemy_at(tile)
        elif action == "fire":
            campfire = self.campfire_at(tile)

            if campfire is None:
                return

            if self.phase == "day":
                self.add_firewood_day(campfire)
            else:
                self.add_firewood_night(campfire)
        elif action == "wait":
            self.pass_night_turn()


# =========================================================
# UI 基礎
# =========================================================
def text(surface, font, value, x, y, color=TEXT) -> None:
    image = font.render(str(value), True, color)
    surface.blit(image, (x, y))

def centered_text(surface, font, value, center, color=TEXT) -> None:
    image = font.render(str(value), True, color)
    surface.blit(image, image.get_rect(center=center))

def panel(surface, rect, fill=PANEL, radius=14) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, BORDER, rect, 1, border_radius=radius)

def terrain_color(kind: str):
    return {
        "grass": GRASS,
        "forest": FOREST,
        "rock": ROCK,
        "water": WATER,
    }.get(kind, GRASS)


# =========================================================
# 地圖細節
# =========================================================
def draw_tree(surface, center) -> None:
    x, y = center
    pygame.draw.rect(surface, (92, 63, 40), pygame.Rect(x - 2, y, 4, 10))
    pygame.draw.circle(surface, (35, 69, 40), (x, y - 6), 8)
    pygame.draw.circle(surface, (48, 89, 50), (x - 6, y), 6)
    pygame.draw.circle(surface, (55, 101, 57), (x + 6, y), 6)

# =========================================================
# 地圖細節 (加入採集枯竭狀態)
# =========================================================
def draw_terrain_detail(surface, terrain, center, tile, visual_mgr=None, is_depleted=False) -> None:
    x, y = center
    
    # =====================================================
    # 1. 處理「已枯竭 (被採集完)」的狀態
    # =====================================================
    if is_depleted and terrain in ("forest", "rock", "grass"):
        # 將地形對應到你的檔名前綴
        res_map = {"forest": "wood", "rock": "stone", "grass": "food"}
        depleted_icon_name = f"{res_map[terrain]}_depleted"
        
        # 從 assets 資料夾強制讀取枯竭圖示
        if depleted_icon_name not in ICON_CACHE:
            try:
                img_path = os.path.join("assets", f"{depleted_icon_name}.png")
                if os.path.exists(img_path):
                    raw_img = pygame.image.load(img_path).convert_alpha()
                    # 將枯竭的圖示縮放到 30x30 適合地圖格的大小
                    ICON_CACHE[depleted_icon_name] = pygame.transform.smoothscale(raw_img, (30, 30))
                else:
                    ICON_CACHE[depleted_icon_name] = None
            except:
                ICON_CACHE[depleted_icon_name] = None
                
        img = ICON_CACHE[depleted_icon_name]
        
        # 有圖片就貼上枯竭的圖片
        if img:
            rect = img.get_rect(center=center)
            surface.blit(img, rect)
            return
        
        # 沒圖片時的「幾何圖形」備案
        if terrain == "forest":
            # 畫一個砍斷的樹樁
            pygame.draw.rect(surface, (92, 63, 40), pygame.Rect(x - 5, y + 2, 10, 8))
            pygame.draw.ellipse(surface, (160, 120, 80), pygame.Rect(x - 5, y, 10, 4))
            return
        elif terrain == "rock":
            # 畫幾顆殘留的碎石
            pygame.draw.circle(surface, (80, 80, 80), (x - 6, y + 6), 3)
            pygame.draw.circle(surface, (70, 70, 70), (x + 5, y + 8), 2)
            return
        elif terrain == "grass":
            # 食物被採光就只剩下草地背景，所以什麼都不畫
            return

    # =====================================================
    # 2. 處理「未枯竭 (還有資源)」的正常狀態
    # =====================================================
    if visual_mgr:
        img = None
        seed = abs(tile[0] * 374761393 + tile[1] * 668265263)
        
        if terrain == "rock":
            variant_idx = (seed % 6) + 1
            img = visual_mgr.get_image(f"stone_0{variant_idx}")
        elif terrain == "forest":
            variant_idx = (seed % 3) + 1
            img = visual_mgr.get_image(f"tree_0{variant_idx}")
        elif terrain == "chest":
            img = visual_mgr.get_image("chest")
            
        if img:
            rect = img.get_rect(center=center)
            surface.blit(img, rect)
            return

    # =====================================================
    # 3. 正常狀態的備用幾何圖形
    # =====================================================
    if terrain == "forest":
        for offset_x, offset_y in ((0, -3), (-12, 6), (12, 6)):
            pygame.draw.rect(surface, (92, 63, 40), pygame.Rect(x + offset_x - 2, y + offset_y, 4, 10))
            pygame.draw.circle(surface, (35, 69, 40), (x + offset_x, y + offset_y - 6), 8)
    elif terrain == "rock":
        pygame.draw.polygon(
            surface,
            (146, 143, 136),
            [(x - 14, y + 9), (x - 9, y - 7), (x, y - 13), (x + 12, y - 5), (x + 15, y + 9)],
        )
    elif terrain == "water":
        for offset in (-8, 2, 11):
            pygame.draw.arc(
                surface, (106, 163, 198),
                pygame.Rect(x - 15, y + offset - 4, 30, 8),
                3.14, 6.28, 1,
            )


# =========================================================
# 玩家繪製 (完全依靠傳入的 attack_frame)
# =========================================================
def draw_player(
    surface,
    center,
    has_spear,
    has_axe,
    visual_mgr=None,
    anim_timer=0,
    attack_animating=False,
    attack_frame=0,
    attack_row=6,
) -> None:
    x, y = center

    if visual_mgr is not None:
        img = None
        # -------------------------------------------------
        # 攻擊動畫 (以明確計算出的 attack_frame 進行索圖)
        # -------------------------------------------------
        if attack_animating:
            # 防呆：確保 Frame 不會超出 Sprite Sheet 範圍 (0~3)
            safe_frame = max(0, min(ATTACK_FRAME_COUNT - 1, attack_frame))
            img = visual_mgr.get_sprite(
                "player",
                col=safe_frame,
                row=attack_row,
                width=ATTACK_FRAME_WIDTH,
                height=ATTACK_FRAME_HEIGHT,
                scale_to=45,
            )
        # -------------------------------------------------
        # 待機動畫
        # -------------------------------------------------
        else:
            idle_frame = (anim_timer // 15) % 3
            img = visual_mgr.get_sprite(
                "player",
                col=idle_frame,
                row=0,
                width=48,
                height=48,
                scale_to=45,
            )
            
        if img is not None:
            rect = img.get_rect(center=(x, y - 15))
            surface.blit(img, rect)
            return

    # =====================================================
    # Sprite Sheet 讀取失敗：備用幾何圖形角色
    # =====================================================
    pygame.draw.ellipse(surface, (24, 23, 21), pygame.Rect(x - 15, y + 14, 30, 9))
    pygame.draw.line(surface, (78, 53, 37), (x - 5, y + 7), (x - 9, y + 18), 4)
    pygame.draw.line(surface, (78, 53, 37), (x + 5, y + 7), (x + 9, y + 18), 4)
    pygame.draw.polygon(
        surface, (151, 92, 51),
        [(x - 11, y - 6), (x + 11, y - 6), (x + 9, y + 10), (x, y + 15), (x - 9, y + 10)],
    )
    pygame.draw.circle(surface, (209, 156, 108), (x, y - 16), 9)
    pygame.draw.circle(surface, (20, 20, 20), (x - 3, y - 16), 1)
    pygame.draw.circle(surface, (20, 20, 20), (x + 3, y - 16), 1)

    if has_spear:
        pygame.draw.line(surface, (112, 74, 42), (x + 13, y + 11), (x + 21, y - 25), 3)
    elif has_axe:
        pygame.draw.line(surface, (112, 74, 42), (x + 14, y + 8), (x + 19, y - 15), 3)


# =========================================================
# 營火
# =========================================================
def draw_campfire(surface, center, lit) -> None:
    x, y = center
    pygame.draw.line(surface, (96, 58, 31), (x - 11, y + 8), (x + 11, y + 2), 5)
    pygame.draw.line(surface, (96, 58, 31), (x - 11, y + 2), (x + 11, y + 8), 5)

    if lit:
        pulse = 2 + int(abs(math.sin(pygame.time.get_ticks() / 170)) * 2)
        pygame.draw.polygon(
            surface, (241, 93, 39),
            [(x, y - 20 - pulse), (x - 10, y + 4), (x, y), (x + 10, y + 4)],
        )
        pygame.draw.polygon(
            surface, (255, 205, 72),
            [(x, y - 11 - pulse), (x - 5, y + 2), (x + 5, y + 2)],
        )


# =========================================================
# 建築物
# =========================================================
def draw_wall(surface, center, hp, max_hp) -> None:
    x, y = center
    for offset in (-12, 0, 12):
        pygame.draw.rect(
            surface, (122, 81, 45),
            pygame.Rect(x + offset - 5, y - 12, 10, 25),
            border_radius=2,
        )
        pygame.draw.circle(surface, (166, 111, 60), (x + offset, y - 11), 5)

    ratio = hp / max_hp if max_hp else 0
    pygame.draw.rect(surface, (48, 48, 48), pygame.Rect(x - 18, y + 17, 36, 4))
    pygame.draw.rect(surface, GREEN, pygame.Rect(x - 18, y + 17, int(36 * ratio), 4))

def draw_trap(surface, center, active) -> None:
    x, y = center
    color = (218, 179, 70) if active else (94, 91, 84)
    pygame.draw.circle(surface, color, center, 13, 2)
    pygame.draw.line(surface, color, (x - 8, y - 8), (x + 8, y + 8), 2)
    pygame.draw.line(surface, color, (x + 8, y - 8), (x - 8, y + 8), 2)


# =========================================================
# 狼
# =========================================================

def draw_wolf(surface, center, hp, max_hp) -> None:
    x, y = center
    
    icon_name = "wolf"
    if icon_name not in ICON_CACHE:
        try:
            img_path = os.path.join("assets", f"{icon_name}.png")
            if os.path.exists(img_path):
                raw_img = pygame.image.load(img_path).convert_alpha()
                # 狼的體型設定為 45x45
                ICON_CACHE[icon_name] = pygame.transform.smoothscale(raw_img, (45, 45))
            else:
                ICON_CACHE[icon_name] = None
        except:
            ICON_CACHE[icon_name] = None
            
    img = ICON_CACHE[icon_name]
    
    if img:
        # 有圖片就直接貼上圖片
        rect = img.get_rect(center=(x, y - 5))
        surface.blit(img, rect)
    else:
        # 備用幾何圖形
        outline = (42, 45, 49)
        fur_dark = (63, 69, 75)
        fur_mid = (88, 95, 103)
        fur_light = (132, 138, 142)
        muzzle = (159, 157, 146)
        eye = (244, 186, 65)

        pygame.draw.ellipse(surface, (24, 25, 27), pygame.Rect(x - 23, y + 12, 47, 9))
        pygame.draw.lines(surface, outline, False, [(x - 15, y - 1), (x - 25, y - 8), (x - 29, y - 17), (x - 24, y - 20)], 8)
        pygame.draw.lines(surface, fur_mid, False, [(x - 15, y - 1), (x - 25, y - 8), (x - 29, y - 17), (x - 24, y - 20)], 5)
        pygame.draw.ellipse(surface, outline, pygame.Rect(x - 19, y - 10, 38, 25))
        pygame.draw.ellipse(surface, fur_mid, pygame.Rect(x - 17, y - 9, 34, 22))
        pygame.draw.arc(surface, fur_dark, pygame.Rect(x - 15, y - 8, 31, 15), math.pi, math.pi * 2, 4)
        pygame.draw.polygon(surface, fur_light, [(x + 7, y - 5), (x + 15, y + 1), (x + 8, y + 11), (x + 2, y + 6)])
        pygame.draw.polygon(surface, outline, [(x + 6, y - 8), (x + 15, y - 16), (x + 23, y - 9), (x + 18, y + 5), (x + 7, y + 4)])
        pygame.draw.polygon(surface, fur_mid, [(x + 8, y - 7), (x + 15, y - 14), (x + 21, y - 8), (x + 16, y + 3), (x + 8, y + 2)])
        pygame.draw.ellipse(surface, outline, pygame.Rect(x + 9, y - 23, 24, 20))
        pygame.draw.ellipse(surface, fur_mid, pygame.Rect(x + 11, y - 22, 20, 18))
        pygame.draw.polygon(surface, outline, [(x + 12, y - 19), (x + 13, y - 31), (x + 20, y - 21)])
        pygame.draw.polygon(surface, fur_dark, [(x + 14, y - 21), (x + 14, y - 28), (x + 18, y - 21)])
        pygame.draw.polygon(surface, outline, [(x + 22, y - 21), (x + 28, y - 30), (x + 29, y - 18)])
        pygame.draw.polygon(surface, fur_dark, [(x + 24, y - 21), (x + 27, y - 27), (x + 27, y - 20)])
        pygame.draw.ellipse(surface, outline, pygame.Rect(x + 23, y - 15, 17, 11))
        pygame.draw.ellipse(surface, muzzle, pygame.Rect(x + 24, y - 14, 14, 9))
        pygame.draw.circle(surface, (24, 24, 25), (x + 38, y - 9), 3)
        pygame.draw.circle(surface, eye, (x + 25, y - 15), 2)
        pygame.draw.circle(surface, (25, 22, 18), (x + 25, y - 15), 1)

        for leg_x in (x - 11, x - 3, x + 7, x + 13):
            pygame.draw.line(surface, outline, (leg_x, y + 8), (leg_x - 1, y + 18), 5)
            pygame.draw.line(surface, fur_dark, (leg_x, y + 8), (leg_x - 1, y + 17), 3)

    # 不論是圖片還是幾何圖形，統一在底部畫出 HP 血條
    ratio = max(0, hp) / max_hp
    pygame.draw.rect(surface, (44, 45, 47), pygame.Rect(x - 22, y + 24, 48, 6), border_radius=3)
    pygame.draw.rect(surface, RED, pygame.Rect(x - 22, y + 24, int(48 * ratio), 6), border_radius=3)


# =========================================================
# 野豬
# =========================================================
def draw_boar(surface, center, hp, max_hp) -> None:
    x, y = center
    
    icon_name = "boar"
    if icon_name not in ICON_CACHE:
        try:
            img_path = os.path.join("assets", f"{icon_name}.png")
            if os.path.exists(img_path):
                raw_img = pygame.image.load(img_path).convert_alpha()
                # 野豬比較大隻，設定為 48x48
                ICON_CACHE[icon_name] = pygame.transform.smoothscale(raw_img, (48, 48))
            else:
                ICON_CACHE[icon_name] = None
        except:
            ICON_CACHE[icon_name] = None
            
    img = ICON_CACHE[icon_name]
    
    if img:
        # 有圖片就直接貼上圖片
        rect = img.get_rect(center=(x, y - 5))
        surface.blit(img, rect)
    else:
        # 備用幾何圖形
        pygame.draw.ellipse(surface, (100, 66, 46), pygame.Rect(x - 17, y - 8, 30, 19))
        pygame.draw.circle(surface, (112, 75, 50), (x + 13, y - 3), 9)
        pygame.draw.polygon(surface, (85, 55, 40), [(x + 7, y - 10), (x + 10, y - 19), (x + 14, y - 9)])
        pygame.draw.circle(surface, BLACK, (x + 16, y - 5), 2)
        pygame.draw.arc(surface, (231, 220, 184), pygame.Rect(x + 13, y - 1, 12, 10), 0, math.pi, 2)
        pygame.draw.line(surface, (81, 54, 39), (x - 10, y + 7), (x - 11, y + 16), 4)
        pygame.draw.line(surface, (81, 54, 39), (x + 5, y + 7), (x + 6, y + 16), 4)

    # 不論是圖片還是幾何圖形，統一在底部畫出 HP 血條
    ratio = max(0, hp) / max_hp
    pygame.draw.rect(surface, (48, 48, 48), pygame.Rect(x - 18, y + 20, 36, 5))
    pygame.draw.rect(surface, RED, pygame.Rect(x - 18, y + 20, int(36 * ratio), 5))

# =========================================================
# HUD
# =========================================================
def draw_bar(surface, fonts, x, y, width, label, value, maximum, color) -> None:
    text(surface, fonts["small"], f"{label}  {value}/{maximum}", x, y)
    background = pygame.Rect(x, y + 22, width, 12)
    pygame.draw.rect(surface, (48, 51, 54), background, border_radius=6)
    ratio = 0 if maximum <= 0 else max(0, min(1, value / maximum))
    fill = pygame.Rect(x, y + 22, int(width * ratio), 12)
    if fill.width > 0:
        pygame.draw.rect(surface, color, fill, border_radius=6)

def draw_button(surface, fonts, rect, label, enabled=True, accent=False) -> None:
    if not enabled:
        fill = (45, 47, 49)
        border = (62, 64, 66)
        color = (101, 103, 103)
    elif accent:
        fill = (118, 79, 39)
        border = GOLD
        color = GOLD_LIGHT
    else:
        fill = PANEL_2
        border = (82, 87, 92)
        color = TEXT

    pygame.draw.rect(surface, fill, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 1, border_radius=8)
    centered_text(surface, fonts["small"], label, rect.center, color)

def hud_buttons(game: Game):
    surface = pygame.display.get_surface()
    hud = get_right_hud_rect(surface) if surface is not None else HUD_PANEL
    if game.phase == "day":
        entries = [
            ("eat", "吃食物", game.inventory.get("food") > 0),
            ("spear", "製作石矛", not game.has_spear and game.inventory.has({"wood": 2, "stone": 1})),
            ("axe", "製作石斧", not game.has_axe and game.inventory.has({"wood": 1, "stone": 2})),
            ("pickaxe", "製作石鎬", not game.has_pickaxe and game.inventory.has({"wood": 2, "stone": 2})),
            ("armor", "製作護甲", game.inventory.has({"hide": 2, "stone": 1})),
        ]
        y = hud.y + 438
        columns = 2
    elif game.phase == "night":
        entries = [
            ("wait", "結束這回合", not game.attack_animating),
        ]
        y = hud.y + 440
        columns = 1
    else:
        entries = [("restart", "重新開始", True)]
        y = hud.y + 430
        columns = 1

    buttons = []
    for index, (action, label, enabled) in enumerate(entries):
        gap = 8
        button_width = (hud.width - 28 - gap * (columns - 1)) // columns
        row = index // columns
        col = index % columns
        rect = pygame.Rect(
            hud.x + 14 + col * (button_width + gap),
            y + row * 39,
            button_width,
            33,
        )
        buttons.append((action, label, rect, enabled))
    return buttons

def execute_hud_action(game: Game, action: str) -> None:
    if action == "eat":
        game.eat()
    elif action == "fire_day":
        game.add_firewood_day()
    elif action == "spear":
        game.craft_spear()
    elif action == "axe":
        game.craft_axe()
    elif action == "pickaxe":
        game.craft_pickaxe()
    elif action == "armor":
        game.craft_armor()
    elif action == "fire_night":
        game.add_firewood_night()
    elif action == "wait":
        game.pass_night_turn()
    elif action == "restart":
        game.reset()


# =========================================================
# 合成清單
# =========================================================
def recipe_button_rect() -> pygame.Rect:
    surface = pygame.display.get_surface()
    hud = get_right_hud_rect(surface) if surface is not None else HUD_PANEL
    return pygame.Rect(hud.x + 14, hud.bottom - 48, hud.width - 28, 34)

def recipe_modal_rect() -> pygame.Rect:
    surface = pygame.display.get_surface()
    width, height = surface.get_size() if surface is not None else (SCREEN_WIDTH, SCREEN_HEIGHT)
    modal_width = min(720, width - 80)
    modal_height = min(610, height - 100)
    return pygame.Rect((width - modal_width) // 2, (height - modal_height) // 2, modal_width, modal_height)

def recipe_close_rect() -> pygame.Rect:
    modal = recipe_modal_rect()
    return pygame.Rect(modal.right - 48, modal.y + 14, 32, 32)

def draw_recipe_modal(surface, fonts) -> None:
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 150))
    surface.blit(shade, (0, 0))

    modal = recipe_modal_rect()
    pygame.draw.rect(surface, (25, 28, 31), modal, border_radius=16)
    pygame.draw.rect(surface, GOLD, modal, 2, border_radius=16)

    text(surface, fonts["heading"], "合成清單", modal.x + 28, modal.y + 22, GOLD_LIGHT)
    text(surface, fonts["tiny"], "查看配方不會消耗任何回合｜ESC 或右上角 X 關閉", modal.x + 28, modal.y + 55, MUTED)

    close = recipe_close_rect()
    mouse = pygame.mouse.get_pos()
    close_fill = (112, 58, 52) if close.collidepoint(mouse) else PANEL_2
    
    pygame.draw.rect(surface, close_fill, close, border_radius=7)
    pygame.draw.rect(surface, RED, close, 1, border_radius=7)
    centered_text(surface, fonts["body"], "X", close.center, TEXT)

    y = modal.y + 92
    for category in ("裝備", "建造"):
        text(surface, fonts["body"], category, modal.x + 28, y, GOLD_LIGHT if category == "裝備" else BLUE)
        y += 29
        
        recipes = [r for r in RECIPE_CATALOG if r["category"] == category]
        for recipe in recipes:
            row = pygame.Rect(modal.x + 24, y, modal.width - 48, 64)
            pygame.draw.rect(surface, PANEL_2, row, border_radius=9)
            pygame.draw.rect(surface, (72, 76, 81), row, 1, border_radius=9)
            
            text(surface, fonts["small"], recipe["name"], row.x + 14, row.y + 8, TEXT)
            text(surface, fonts["tiny"], f"成本：{recipe['cost_text']}", row.x + 125, row.y + 10, GOLD_LIGHT)
            text(surface, fonts["tiny"], f"效果：{recipe['effect']}", row.x + 14, row.y + 36, MUTED)
            y += 70
        y += 8


# =========================================================
# 情境選單
# =========================================================
def context_menu_rows(game, tile, origin):
    actions = game.context_actions(tile)
    width = 250
    row_height = 36
    total_height = len(actions) * row_height + 10

    surface = pygame.display.get_surface()
    screen_width, screen_height = surface.get_size() if surface is not None else (SCREEN_WIDTH, SCREEN_HEIGHT)
    x = min(origin[0], screen_width - width - 10)
    y = min(origin[1], screen_height - total_height - 10)
    x = max(10, x)
    y = max(10, y)

    rows = []
    for index, (action, label, enabled) in enumerate(actions):
        rect = pygame.Rect(x + 5, y + 5 + index * row_height, width - 10, row_height - 4)
        rows.append((action, label, enabled, rect))
    return rows

def draw_context_menu(surface, fonts, game, tile, origin) -> None:
    rows = context_menu_rows(game, tile, origin)
    if not rows:
        return

    first = rows[0][3]
    last = rows[-1][3]
    background = pygame.Rect(first.x - 5, first.y - 5, first.width + 10, last.bottom - first.y + 10)
    
    pygame.draw.rect(surface, (25, 28, 31), background, border_radius=10)
    pygame.draw.rect(surface, GOLD, background, 1, border_radius=10)

    mouse = pygame.mouse.get_pos()
    for action, label, enabled, rect in rows:
        if enabled and rect.collidepoint(mouse):
            fill = (77, 59, 39)
        else:
            fill = PANEL_2 if enabled else (43, 45, 47)
            
        pygame.draw.rect(surface, fill, rect, border_radius=6)
        color = TEXT if enabled else (103, 105, 106)
        text(surface, fonts["small"], label, rect.x + 10, rect.y + 7, color)


# =========================================================
# 選取格資訊
# =========================================================
def draw_selected_tile_info(surface, fonts, game) -> None:
    tile = game.selected_tile
    hud = get_right_hud_rect(surface)
    x = hud.x + 14
    text(surface, fonts["tiny"], "目前選取", x, hud.y + 362, MUTED)
    text(surface, fonts["small"], f"六角格 {tile}", x, hud.y + 380, GOLD_LIGHT)

    if tile not in game.discovered and game.phase == "day":
        text(surface, fonts["tiny"], "尚未探索", x, hud.y + 402, MUTED)
        return

    terrain = TERRAIN_NAMES[game.terrain[tile]]
    resource = game.resource_type_at(tile)
    amount = game.resources.get(tile, 0)
    detail = terrain

    if resource and amount > 0:
        detail += f"｜{RESOURCE_NAMES[resource]} {amount}"

    building = game.buildings.get_building(tile)
    if building is not None:
        if building.building_type == BUILD_WALL:
            detail += f"｜木牆 {building.hp}/{building.max_hp}"
        else:
            detail += "｜陷阱" if building.active else "｜已觸發陷阱"

    enemies = game.enemies_at(tile)
    if enemies:
        detail += f"｜敵人 x{len(enemies)}"

    text(surface, fonts["tiny"], detail, x, hud.y + 402, TEXT)


# =========================================================
# 遊戲畫面
# =========================================================
ICON_CACHE = {}
UI_ICON_CACHE = {}


def draw_ui_icon(surface, name: str, center: tuple[int, int], fallback_color) -> None:
    """Draw an assets/ui icon, or a safe shape fallback when missing."""
    if name not in UI_ICON_CACHE:
        path = os.path.join("assets", "ui", f"{name}.png")
        try:
            image = pygame.image.load(path).convert_alpha() if os.path.exists(path) else None
            UI_ICON_CACHE[name] = pygame.transform.smoothscale(image, (24, 24)) if image else None
        except pygame.error:
            UI_ICON_CACHE[name] = None
    image = UI_ICON_CACHE[name]
    if image is None:
        pygame.draw.circle(surface, fallback_color, center, 9)
    else:
        surface.blit(image, image.get_rect(center=center))

def draw_game(
    screen,
    fonts,
    game,
    context_tile,
    context_origin,
    drag_path=None,
    recipe_open=False,
    visual_mgr=None,
    anim_timer=0,
    notification_manager=None,
    first_day_tutorial=None,
    camera=None,
) -> None:
    screen.fill(BG)

    viewport = get_game_viewport(screen)
    hud = get_right_hud_rect(screen)
    screen_width = screen.get_width()
    if camera is not None:
        player_world_pos = axial_to_world_pixel(
            game.player,
            HEX_SIZE,
            (MAP_ORIGIN_X, MAP_ORIGIN_Y),
        )

        camera.center_on(
            player_world_pos,
            viewport,
        )
    pygame.draw.rect(screen, TOP, pygame.Rect(0, 0, screen_width, 62))
    text(screen, fonts["heading"], "石器時代：荒野求生 v6", 28, 18, GOLD_LIGHT)
    text(screen, fonts["small"], "拖曳角色＝快速移動｜右鍵＝操作選單", 345, 22, MUTED)

    if game.phase == "day":
        phase_label = f"第 {game.day} 天"
        turn_label = f"白天剩餘回合：{game.day_turns_left}/{DAY_TURNS}"
        phase_color = GOLD
    elif game.phase == "night":
        phase_label = f"第 {game.day} 夜"
        turn_label = f"夜晚剩餘回合：{game.night_turns_left}/{NIGHT_TURNS}"
        phase_color = BLUE
    else:
        phase_label = "遊戲結束"
        turn_label = "生命值歸零"
        phase_color = RED

    pill = pygame.Rect(max(600, hud.x - 270), 14, 130, 34)
    pygame.draw.rect(screen, phase_color, pill, border_radius=17)
    centered_text(screen, fonts["small"], phase_label, pill.center, BLACK)
    text(screen, fonts["small"], turn_label, pill.right + 18, 22, phase_color)

    panel(screen, viewport, (23, 26, 29), 16)
    panel(screen, hud, PANEL, 16)

    hover_tile = tile_at_pixel(
        pygame.mouse.get_pos(),
        camera,
        viewport,
    )
    previous_clip = screen.get_clip()
    screen.set_clip(viewport)
    # =====================================================
    # 地圖
    # =====================================================
    for r in range(MAP_ROWS):
        for q in range(MAP_COLS):
            tile = (q, r)
            center = axial_to_pixel(tile, camera)
            discovered = tile in game.discovered
            
                
            fill = terrain_color(game.terrain[tile]) if discovered else FOG
            points = hex_points(center)
            
            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, (57, 61, 64), points, 1)
            
            if discovered:
                # 判斷這格的資源是不是被採光了
                is_depleted = game.is_tile_depleted(tile)
                
                # 將枯竭狀態傳入
                draw_terrain_detail(screen, game.terrain[tile], center, tile, visual_mgr, is_depleted)
                
                amount = game.resources.get(tile, 0)
                if amount > 0:
                    text(screen, fonts["tiny"], amount, center[0] + 16, center[1] + 12, (238, 220, 150))
                    
            if tile == hover_tile:
                pygame.draw.polygon(screen, (221, 221, 205), points, 2)
            if tile == game.selected_tile:
                pygame.draw.polygon(screen, GOLD_LIGHT, points, 3)

    # =====================================================
    # 拖曳路徑
    # =====================================================
    if drag_path and len(drag_path) > 1:
        centers = [axial_to_pixel(tile, camera) for tile in drag_path]
        pygame.draw.lines(screen, GOLD_LIGHT, False, centers, 4)
        
        for index, tile in enumerate(drag_path):
            center = axial_to_pixel(tile, camera)
            pygame.draw.polygon(screen, GOLD_LIGHT, hex_points(center), 3)
            if index > 0:
                marker_radius = 7 if index == len(drag_path) - 1 else 5
                pygame.draw.circle(screen, (255, 235, 160), center, marker_radius)
                
        cost = len(drag_path) - 1
        destination = axial_to_pixel(drag_path[-1], camera)
        text(screen, fonts["tiny"], f"移動成本：{cost} 回合", destination[0] + 18, destination[1] - 30, GOLD_LIGHT)

    # =====================================================
    # 夜晚濾鏡與營火光暈
    # =====================================================
    if game.phase == "night":
        tint = pygame.Surface((viewport.width, viewport.height), pygame.SRCALPHA)
        tint.fill((5, 10, 27, 72))
        screen.blit(tint, viewport.topleft)

            # 將所有點燃營火半徑 4 內的六角格標示為安全區。
        safe_overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        for tile in game.terrain:
            if game.is_in_lit_campfire_range(tile):
                center = axial_to_pixel(tile, camera)

                pygame.draw.polygon(
                    safe_overlay,
                    (255, 185, 72, 32),
                    hex_points(center),
                )

                pygame.draw.polygon(
                    safe_overlay,
                    (255, 205, 105, 70),
                    hex_points(center),
                    1,
                )

        screen.blit(safe_overlay, (0, 0))

    # =====================================================
    # 建築物與營火
    # =====================================================
    for building in game.buildings.buildings.values():
        center = axial_to_pixel(building.position, camera)
        if building.building_type == BUILD_WALL:
            draw_wall(screen, center, building.hp, building.max_hp)
        else:
            draw_trap(screen, center, building.active)
            
    for campfire in game.campfires.values():
        draw_campfire(
            screen,
            axial_to_pixel(campfire.position, camera),
            campfire.lit,
        )

    # =====================================================
    # 敵人
    # =====================================================
    enemy_groups = {}
    for enemy in game.alive_enemies():
        enemy_groups.setdefault(enemy.position, []).append(enemy)
        
    for tile, enemies in enemy_groups.items():
        base_x, base_y = axial_to_pixel(tile, camera)
        for index, enemy in enumerate(enemies[:3]):
            offset_x = (index - 1) * 12 if len(enemies) > 1 else 0
            center = (base_x + offset_x, base_y - 3)
            max_hp = 30 if enemy.enemy_type == ENEMY_WOLF else 55
            
            if enemy.enemy_type == ENEMY_WOLF:
                draw_wolf(screen, center, enemy.health, max_hp)
            else:
                draw_boar(screen, center, enemy.health, max_hp)
                
        if len(enemies) > 3:
            text(screen, fonts["tiny"], f"+{len(enemies) - 3}", base_x + 19, base_y - 27, RED)


    # =====================================================
    # 玩家繪製 (傳遞已經算好的 attack_frame 給繪製模組)
    # =====================================================
    player_center = axial_to_pixel(game.player, camera)
    draw_player(
        screen,
        player_center,
        game.has_spear,
        game.has_axe,
        visual_mgr,
        anim_timer,
        game.attack_animating,
        game.attack_frame,
        game.attack_anim_row,
    )

    if game.floating_icon_type is not None:
        elapsed = pygame.time.get_ticks() - game.floating_icon_start_time
        float_y = int((elapsed / 1000) * 40) # 最多往上飄移 40 pixel
        alpha = max(0, 255 - int((elapsed / 1000) * 255)) # 漸隱透明度 (255 -> 0)
        
        icon_cx, icon_cy = axial_to_pixel(
            game.floating_icon_tile,
            camera,
        )
        icon_cy -= (20 + float_y) # 往上飄移
        
        icon_name = game.floating_icon_type
        icon_img = None
        
        # 💡 [核心修改] 如果快取裡沒有這張圖，強制去 assets/ 資料夾讀取！
        if icon_name not in ICON_CACHE:
            try:
                # 動態組出路徑，例如 "assets/wood.png"
                img_path = os.path.join("assets", f"{icon_name}.png")
                if os.path.exists(img_path):
                    raw_img = pygame.image.load(img_path).convert_alpha()
                    # 把 Icon 縮小為 24x24，看起來更精緻
                    ICON_CACHE[icon_name] = pygame.transform.smoothscale(raw_img, (24, 24))
                else:
                    ICON_CACHE[icon_name] = None
            except:
                ICON_CACHE[icon_name] = None
                
        icon_img = ICON_CACHE[icon_name]
        
        if icon_img:
            # Pygame 處理帶透明通道圖片的漸隱小技巧
            icon_copy = icon_img.copy()
            icon_copy.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            
            # 將 Icon 稍微往左移，讓文字可以在它右邊
            rect = icon_copy.get_rect(center=(icon_cx - 12, icon_cy))
            screen.blit(icon_copy, rect)
            
            # 在 Icon 旁邊畫出 +1, +2
            val_text = fonts["heading"].render(f"+{game.floating_icon_amount}", True, GOLD_LIGHT)
            val_text.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(val_text, (icon_cx + 5, icon_cy - 12))
        else:
            # 防呆：如果圖片檔名真的拼錯或找不到，就直接飄純文字
            fallback_txt = f"+{game.floating_icon_amount} {RESOURCE_NAMES.get(game.floating_icon_type, '')}"
            val_text = fonts["heading"].render(fallback_txt, True, GOLD_LIGHT)
            val_text.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(val_text, val_text.get_rect(center=(icon_cx, icon_cy)))

    # ... (下半部 draw_game 的生存紀錄與 HUD 程式碼保持不變) ...
    screen.set_clip(previous_clip)
    # =====================================================
    # HUD 狀態區
    # =====================================================
    hud_x = hud.x + 14
    hud_width = hud.width - 28
    text(screen, fonts["body"], "生存狀態", hud_x, hud.y + 16, GOLD_LIGHT)
    draw_ui_icon(screen, "heart", (hud_x + 10, hud.y + 61), RED)
    draw_bar(screen, fonts, hud_x + 27, hud.y + 43, hud_width - 27, "生命", game.survival.health, 100, RED)
    draw_ui_icon(screen, "armor", (hud_x + 10, hud.y + 111), BLUE)
    draw_bar(screen, fonts, hud_x + 27, hud.y + 93, hud_width - 27, "護甲", game.survival.armor, 50, BLUE)
    draw_ui_icon(screen, "hunger", (hud_x + 10, hud.y + 161), GOLD)
    draw_bar(screen, fonts, hud_x + 27, hud.y + 143, hud_width - 27, "飢餓", game.survival.hunger, 100, GOLD)

    resource_values = [
        ("food", "食", game.inventory.get("food"), (178, 87, 63)),
        ("wood", "木", game.inventory.get("wood"), (133, 88, 52)),
        ("stone", "石", game.inventory.get("stone"), (147, 147, 143)),
        ("hide", "皮", game.inventory.get("hide"), (162, 118, 72)),
    ]
    card_gap = 8
    card_width = (hud_width - card_gap) // 2
    for index, (icon_name, label, value, color) in enumerate(resource_values):
        row = index // 2
        col = index % 2
        rect = pygame.Rect(hud_x + col * (card_width + card_gap), hud.y + 198 + row * 48, card_width, 40)
        pygame.draw.rect(screen, PANEL_2, rect, border_radius=9)
        draw_ui_icon(screen, icon_name, (rect.x + 18, rect.centery), color)
        text(screen, fonts["tiny"], label, rect.x + 34, rect.y + 5, MUTED)
        text(screen, fonts["small"], value, rect.x + 34, rect.y + 19, TEXT)

    equipment = (
        ("spear", game.has_spear),
        ("axe", game.has_axe),
        ("pickaxe", game.has_pickaxe),
    )
    for index, (icon_name, owned) in enumerate(equipment):
        center = (hud_x + 18 + index * 36, hud.y + 303)
        draw_ui_icon(screen, icon_name, center, GOLD if owned else (72, 75, 78))
        if not owned:
            veil = pygame.Surface((24, 24), pygame.SRCALPHA)
            veil.fill((20, 22, 24, 145))
            screen.blit(veil, veil.get_rect(center=center))

    fire_rect = pygame.Rect(hud_x, hud.y + 320, hud_width, 38)
    pygame.draw.rect(screen, PANEL_2, fire_rect, border_radius=9)
    fire_text = "燃燒中" if game.campfire.lit else "已熄滅"
    draw_ui_icon(screen, "campfire", (fire_rect.x + 19, fire_rect.centery), GOLD)
    text(screen, fonts["tiny"], f"{fire_text}｜{game.campfire.fuel}/{CAMPFIRE_MAX_FUEL}", fire_rect.x + 38, fire_rect.y + 11, GOLD_LIGHT if game.campfire.lit else RED)

    draw_selected_tile_info(screen, fonts, game)

    # 操作提示
    if game.phase == "day":
        text(screen, fonts["tiny"], "拖曳移動｜右鍵操作", hud_x, hud.y + 420, GOLD_LIGHT)
    elif game.phase == "night":
        if game.attack_animating:
            text(screen, fonts["tiny"], "攻擊中……", hud_x, hud.y + 420, GOLD_LIGHT)
        else:
            text(screen, fonts["tiny"], "拖曳移動｜左鍵攻擊", hud_x, hud.y + 420, BLUE)
    else:
        text(screen, fonts["tiny"], "你沒有撐過這次荒野求生。", hud_x, hud.y + 420, RED)

    # =====================================================
    # HUD 按鈕與選單
    # =====================================================
    for action, label, rect, enabled in hud_buttons(game):
        draw_button(screen, fonts, rect, label, enabled, accent=(action in ("wait", "restart")))
        
    draw_button(screen, fonts, recipe_button_rect(), "關閉合成清單" if recipe_open else "合成清單", True, accent=recipe_open)

    if context_tile is not None and not recipe_open:
        draw_context_menu(screen, fonts, game, context_tile, context_origin)
        
    if recipe_open:
        draw_recipe_modal(screen, fonts)

    if notification_manager is not None:
        notification_manager.draw(screen, fonts, viewport)

    if first_day_tutorial is not None and first_day_tutorial.current_message():
        message = first_day_tutorial.current_message()
        overlay = pygame.Rect(viewport.centerx - min(310, viewport.width // 2 - 20), viewport.y + 14, min(620, viewport.width - 40), 58)
        shade = pygame.Surface(overlay.size, pygame.SRCALPHA)
        shade.fill((15, 18, 20, 220))
        screen.blit(shade, overlay.topleft)
        pygame.draw.rect(screen, GOLD, overlay, 1, border_radius=10)
        centered_text(screen, fonts["small"], f"教學 {first_day_tutorial.step + 1}/11｜{message}", overlay.center, TEXT)


# =========================================================
# 教學
# =========================================================
TUTORIAL = [
    (
        "滑鼠操作",
        [
            "左鍵按住玩家角色並拖曳：預覽最短路徑並快速移動。",
            "左鍵點六角格仍可選取並查看資訊。",
            "右鍵點任意地圖格：開啟情境操作選單。",
            "白天的移動、採集、建造都從右鍵選單進行。",
            "右側按鈕可吃食物、加柴或製作裝備。",
        ],
    ),
    (
        "白天 20 回合",
        [
            "每天固定有 20 回合。",
            "每次成功移動、採集、建造或製作會消耗 1 回合。",
            "回合變成 0 時，遊戲會立即自動進入夜晚。",
            "趁白天收集木材、石頭與食物並建立防線。",
        ],
    ),
    (
        "夜晚 20 回合",
        [
            "狼與野豬會真的從地圖邊緣出現並向營地移動。",
            "晚上也能拖曳角色移動；每走 1 格仍會消耗 1 回合並觸發敵人行動。",
            "左鍵點攻擊範圍內的敵人即可直接攻擊；右鍵仍可開啟選單。",
            "每次你的夜晚行動後，所有敵人會移動或攻擊。",
            "木牆會擋住敵人；陷阱會在敵人踩上去時造成傷害。",
        ],
    ),
    (
        "營火與生存",
        [
            "營火燃燒時，狼不敢主動靠近營地最內圈。",
            "每個夜晚回合結束都會消耗 1 點營火燃料。",
            "夜晚撐過 20 回合，或提前擊敗全部敵人，就會進入下一天。",
            "生命值降到 0 時遊戲結束。",
        ],
    ),
]

def menu_start_rect() -> pygame.Rect:
    surface = pygame.display.get_surface()
    width, height = surface.get_size() if surface is not None else (SCREEN_WIDTH, SCREEN_HEIGHT)
    return pygame.Rect(width // 2 - 150, int(height * 0.62), 300, 58)

def draw_menu(screen, fonts) -> None:
    screen.fill(BG)
    width, height = screen.get_size()
    for row in range(height // 80 + 2):
        for col in range(width // 90 + 2):
            x = col * 90 + 20 + (row % 2) * 45
            y = row * 80 + 20
            points = [
                (
                    int(x + 30 * math.cos(math.radians(30 + i * 60))),
                    int(y + 30 * math.sin(math.radians(30 + i * 60))),
                )
                for i in range(6)
            ]
            pygame.draw.polygon(screen, (29, 32, 35), points, 1)

    centered_text(screen, fonts["title"], "石器時代：荒野求生", (width // 2, int(height * 0.24)), GOLD_LIGHT)
    centered_text(screen, fonts["body"], "滑鼠回合制生存策略", (width // 2, int(height * 0.31)), MUTED)
    draw_campfire(screen, (width // 2, int(height * 0.47)), True)
    draw_button(screen, fonts, menu_start_rect(), "開始遊戲", True, True)
    centered_text(screen, fonts["small"], "白天 20 回合｜夜晚 20 回合｜右鍵情境操作", (width // 2, int(height * 0.76)), MUTED)
    centered_text(screen, fonts["tiny"], "F11 全螢幕｜ESC 離開", (width // 2, int(height * 0.84)), MUTED)

def tutorial_buttons() -> dict[str, pygame.Rect]:
    surface = pygame.display.get_surface()
    width, height = surface.get_size() if surface is not None else (SCREEN_WIDTH, SCREEN_HEIGHT)
    y = min(height - 72, int(height * 0.78))
    return {
        "back": pygame.Rect(width // 2 - 285, y, 170, 42),
        "skip": pygame.Rect(width // 2 - 85, y, 170, 42),
        "next": pygame.Rect(width // 2 + 115, y, 170, 42),
    }

def draw_tutorial(screen, fonts, page: int) -> None:
    screen.fill(BG)
    width, height = screen.get_size()
    card_width = min(920, width - 80)
    card_height = min(530, height - 120)
    card = pygame.Rect((width - card_width) // 2, 72, card_width, card_height)
    panel(screen, card, (29, 32, 36), 22)
    
    title_value, lines = TUTORIAL[page]
    text(screen, fonts["tiny"], f"新手教學 {page + 1}/{len(TUTORIAL)}", card.x + 55, card.y + 33, MUTED)
    text(screen, fonts["title"], title_value, card.x + 55, card.y + 68, GOLD_LIGHT)
    
    y = card.y + 153
    for line in lines:
        pygame.draw.circle(screen, GOLD, (253, y + 10), 5)
        text(screen, fonts["body"], line, 278, y, TEXT)
        y += 58
        
    for index in range(len(TUTORIAL)):
        pygame.draw.circle(
            screen,
            GOLD if index == page else (75, 78, 82),
            (width // 2 - 45 + index * 30, card.bottom - 30),
            6,
        )
        
    buttons = tutorial_buttons()
    draw_button(screen, fonts, buttons["back"], "上一頁", page > 0)
    draw_button(screen, fonts, buttons["skip"], "跳過教學", True)
    draw_button(screen, fonts, buttons["next"], "開始遊戲" if page == len(TUTORIAL) - 1 else "下一頁", True, True)


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    try:
        pygame.init()
        pygame.display.set_caption("石器時代：荒野求生 v6 - 音效整合")

        start_game = intro.play_intro()

        if not start_game:
            pygame.quit()
            return

        display_manager = DisplayManager()
        screen = display_manager.create_window()
        clock = pygame.time.Clock()
        fonts = create_fonts()
        
        # display 建立後才載入圖片
        visual_mgr = VisualManager()
        game = Game()
        camera = Camera()
        notification_manager = FloatingNotificationManager()
        first_day_tutorial = TutorialController(game)
    except Exception as e:
        print()
        print("=" * 45)
        print("遊戲初始化失敗")
        print("=" * 45)
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤內容：{e}")
        print("=" * 45)
        print()
        try:
            pygame.quit()
        except Exception:
            pass
        try:
            input("按 Enter 關閉...")
        except Exception:
            pass
        return

    view = "menu"
    tutorial_page = 0
    context_tile = None
    context_origin = (0, 0)
    dragging_player = False
    drag_path = None
    recipe_open = False
    anim_timer = 0
    
    last_phase = game.phase
    fire_loop_playing = False
    main_bgm_playing = False
    running = True

    while running:
        # =================================================
        # 事件處理
        # =================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                screen = display_manager.resize(event.size)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen = display_manager.toggle_fullscreen()
                    continue
                if (
                    view == "game"
                    and event.key in (pygame.K_RETURN, pygame.K_SPACE)
                    and first_day_tutorial.step in (0, 8)
                ):
                    first_day_tutorial.acknowledge(game)
                    continue
                if event.key == pygame.K_ESCAPE:
                    if view == "game":
                        if recipe_open:
                            recipe_open = False
                        elif context_tile is not None:
                            context_tile = None
                        else:
                            running = False
                    else:
                        running = False
                elif event.key == pygame.K_h and view == "game":
                    view = "tutorial"
                    tutorial_page = 0
                    context_tile = None
                    recipe_open = False
                    dragging_player = False
                    drag_path = None

            # -------------------------------------------------
            # 1. 主選單
            # -------------------------------------------------
            if view == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_start_rect().collidepoint(event.pos):
                        audio.play_sfx("click")
                        view = "tutorial"
                        tutorial_page = 0
                continue

            # -------------------------------------------------
            # 2. 教學
            # -------------------------------------------------
            if view == "tutorial":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = tutorial_buttons()
                    mouse = event.pos
                    if buttons["back"].collidepoint(mouse) and tutorial_page > 0:
                        audio.play_sfx("click")
                        tutorial_page -= 1
                    elif buttons["skip"].collidepoint(mouse):
                        audio.play_sfx("click")
                        view = "game"
                    elif buttons["next"].collidepoint(mouse):
                        audio.play_sfx("click")
                        if tutorial_page >= len(TUTORIAL) - 1:
                            view = "game"
                        else:
                            tutorial_page += 1
                continue

            # -------------------------------------------------
            # 3. 遊戲畫面
            # -------------------------------------------------
            if view == "game":
                # =================================================
                # 🛡️ 攻擊動畫播放期間：鎖定所有互動
                # =================================================
                if game.attack_animating:
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        continue # 忽略所有的滑鼠操作直到動畫播完！

                # =================================================
                # 玩家拖曳移動
                # =================================================
                if event.type == pygame.MOUSEMOTION and dragging_player and not recipe_open:
                    tile = tile_at_pixel(
                    event.pos,
                    camera,
                    get_game_viewport(screen),
                )
                    if tile is None:
                        drag_path = None
                    else:
                        game.selected_tile = tile
                        drag_path = game.preview_drag_path(tile)
                    continue

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_player:
                    dragging_player = False
                    if drag_path and len(drag_path) > 1:
                        game.execute_drag_path(drag_path)
                    drag_path = None
                    context_tile = None
                    continue

                if event.type != pygame.MOUSEBUTTONDOWN:
                    continue

                mouse = event.pos

                # =================================================
                # 合成清單
                # =================================================
                if event.button == 1 and recipe_button_rect().collidepoint(mouse):
                    audio.play_sfx("click")
                    recipe_open = not recipe_open
                    context_tile = None
                    dragging_player = False
                    drag_path = None
                    continue

                if recipe_open:
                    if event.button == 1 and recipe_close_rect().collidepoint(mouse):
                        audio.play_sfx("click")
                        recipe_open = False
                    continue

                # =================================================
                # 右鍵選單
                # =================================================
                if event.button == 3:
                    tile = tile_at_pixel(
                        mouse,
                        camera,
                        get_game_viewport(screen),
                    )
                    if tile is not None and game.phase != "game_over":
                        game.selected_tile = tile
                        context_tile = tile
                        context_origin = mouse
                    else:
                        context_tile = None
                    continue

                if event.button != 1:
                    continue

                # 左鍵點擊情境選單
                clicked_menu = False
                if context_tile is not None:
                    for action, label, enabled, rect in context_menu_rows(game, context_tile, context_origin):
                        if rect.collidepoint(mouse):
                            clicked_menu = True
                            audio.play_sfx("click")
                            if enabled:
                                gathering_wood = (action == "gather" and game.resource_type_at(context_tile) == "wood")
                                game.execute_context_action(action, context_tile)
                                if gathering_wood:
                                    audio.play_sfx("chop")
                            context_tile = None
                            break
                if clicked_menu:
                    continue

                # 左鍵點擊 HUD 按鈕
                clicked_hud = False
                for action, label, rect, enabled in hud_buttons(game):
                    if rect.collidepoint(mouse):
                        clicked_hud = True
                        audio.play_sfx("click")
                        if enabled:
                            execute_hud_action(game, action)
                        context_tile = None
                        break
                if clicked_hud:
                    continue

                # =================================================
                # 點擊地圖
                # =================================================
                tile = tile_at_pixel(
                    mouse,
                    camera,
                    get_game_viewport(screen),
                )

                # 按下自己所在的位置：準備拖曳
                if tile == game.player and game.phase in ("day", "night"):
                    dragging_player = True
                    drag_path = [game.player]
                    context_tile = None
                    continue

                # 點擊其他位置：直接攻擊或移動
                if tile is not None:
                    game.selected_tile = tile
                    if game.phase == "night":
                        if game.enemies_at(tile):
                            game.attack_enemy_at(tile)
                        elif game.can_move_night_to(tile):
                            game.move_night_to(tile)
                context_tile = None
                continue
        if view == "game" and game.completed_day is not None:
            completed_day = game.completed_day
            game.completed_day = None

            day_transition.play_day_survived(completed_day)

            screen = display_manager.restore()

            pygame.display.set_caption("石器時代：荒野求生 v6 - 音效整合")

        # =====================================================
        # 音效同步
        # =====================================================
        if game.phase != last_phase:
            if game.phase == "night":
                audio.play_sfx("wolf_howl")
            if last_phase == "night" and game.phase != "night":
                audio.stop_sfx("fire")
                fire_loop_playing = False
            last_phase = game.phase

        should_play_fire = (
            view == "game"
            and game.phase == "night"
            and bool(game.lit_campfires())
        )

        if should_play_fire and not fire_loop_playing:
            fire_loop_playing = audio.play_sfx("fire", loops=-1)
        elif not should_play_fire and fire_loop_playing:
            audio.stop_sfx("fire")
            fire_loop_playing = False

        should_play_main_bgm = (
            view == "game"
            and game.phase != "game_over"
        )

        if should_play_main_bgm and not main_bgm_playing:
            music_path = os.path.join("assets", "audio", "old.wav")

            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)
                    main_bgm_playing = True
                except pygame.error as exc:
                    print(f"背景音樂播放失敗：{exc}")

        elif not should_play_main_bgm and main_bgm_playing:
            pygame.mixer.music.fadeout(1000)
            main_bgm_playing = False

        if view == "game" and game.phase == "game_over":
            audio.stop_all()
            fire_loop_playing = False
            main_bgm_playing = False

            action = game_over.play_game_over(game.death_reason)
            screen = display_manager.restore()

            if action == "restart":
                game = Game()
                notification_manager = FloatingNotificationManager()
                first_day_tutorial = TutorialController(game)
                context_tile = None
                dragging_player = False
                drag_path = None
                recipe_open = False
                last_phase = game.phase

                pygame.display.set_caption(
                    "石器時代：荒野求生 v6 - 音效整合"
                )

                continue

            running = False
            continue

        anim_timer += 1

        # =====================================================
        # ★ 核心關鍵：在此獨立更新攻擊動畫的邏輯 (Update Phase)
        # =====================================================
        
        if view == "game" and game.attack_animating:
            elapsed = pygame.time.get_ticks() - game.attack_anim_start_time
            game.attack_frame = int(elapsed // ATTACK_FRAME_DURATION)
            
            # 動畫播滿 4 幀，正式結算傷害與關閉狀態
            if game.attack_frame >= ATTACK_FRAME_COUNT:
                game.finish_attack_animation()

        # =====================================================
        # 🌟 更新浮動 Icon 的生命週期 (漂浮 1 秒後消失)
        # =====================================================
        if view == "game" and game.floating_icon_type is not None:
            if pygame.time.get_ticks() - game.floating_icon_start_time > 1000:
                game.floating_icon_type = None

        if view == "game":
            now_ms = pygame.time.get_ticks()
            notification_manager.sync_from_logs(game.logs, now_ms)
            notification_manager.update(now_ms)
            first_day_tutorial.update(game)
        # =====================================================
        # 畫面渲染 (Render Phase)
        # =====================================================
        if view == "menu":
            draw_menu(screen, fonts)
        elif view == "tutorial":
            draw_tutorial(screen, fonts, tutorial_page)
        else:
            draw_game(
                screen,
                fonts,
                game,
                context_tile,
                context_origin,
                drag_path,
                recipe_open,
                visual_mgr,
                anim_timer,
                notification_manager,
                first_day_tutorial,
                camera,
            )

        pygame.display.flip()
        clock.tick(FPS)

    audio.stop_all()
    pygame.quit()

if __name__ == "__main__":
    main()
