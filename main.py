"""石器時代：荒野求生 - 滑鼠回合制可玩版。

主要操作：
- 左鍵：選擇地圖格 / 點擊右側按鈕
- 右鍵：在地圖格開啟情境選單
- 白天 20 回合；成功操作消耗 1 回合，歸零立即入夜
- 夜晚 20 回合；每次玩家行動後敵人移動/攻擊
"""

from __future__ import annotations

import math
import os
import random

import pygame

from building import BuildingManager
from campfire import Campfire
from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    CAMP_POSITION,
    ENEMY_BOAR,
    ENEMY_WOLF,
    FPS,
    MAP_COLS,
    MAP_ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from enemy import calculate_player_damage, claim_loot, create_enemy, damage_enemy
from inventory import Inventory
from pathfinding import find_hex_path
from recipe_catalog import RECIPE_CATALOG
from survival import SurvivalStats


DAY_TURNS = 20
NIGHT_TURNS = 20

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


def axial_to_pixel(position: tuple[int, int]) -> tuple[int, int]:
    q, r = position

    x = MAP_ORIGIN_X + HEX_SIZE * math.sqrt(3) * (q + r / 2)
    y = MAP_ORIGIN_Y + HEX_SIZE * 1.5 * r

    return int(x), int(y)


def hex_points(center: tuple[int, int]) -> list[tuple[int, int]]:
    cx, cy = center

    return [
        (
            int(cx + HEX_SIZE * math.cos(math.radians(30 + i * 60))),
            int(cy + HEX_SIZE * math.sin(math.radians(30 + i * 60))),
        )
        for i in range(6)
    ]


def tile_at_pixel(mouse_pos: tuple[int, int]) -> tuple[int, int] | None:
    if not MAP_PANEL.collidepoint(mouse_pos):
        return None

    best_tile = None
    best_distance = HEX_SIZE * 1.05

    for r in range(MAP_ROWS):
        for q in range(MAP_COLS):
            tile = (q, r)
            cx, cy = axial_to_pixel(tile)
            distance = math.hypot(mouse_pos[0] - cx, mouse_pos[1] - cy)

            if distance < best_distance:
                best_distance = distance
                best_tile = tile

    return best_tile


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
            resources[position] = 0 if kind == "water" else rng.randint(1, 3)

    return terrain, resources


class Game:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.terrain, self.resources = create_world()

        self.inventory = Inventory()
        self.survival = SurvivalStats()
        self.buildings = BuildingManager()
        self.campfire = Campfire(CAMP_POSITION)

        self.player = CAMP_POSITION
        self.selected_tile = CAMP_POSITION

        self.discovered = {CAMP_POSITION}
        self.discovered.update(neighbors(CAMP_POSITION))

        self.day = 1
        self.phase = "day"

        self.day_turns_left = DAY_TURNS
        self.night_turns_left = 0

        self.has_spear = False
        self.has_axe = False

        self.enemies = []

        self.logs = [
            "你在石器時代的荒野中醒來。",
            "白天共有 20 回合。右鍵點地圖格開始行動。",
        ]

    def log(self, message: str) -> None:
        self.logs.append(message)
        self.logs = self.logs[-7:]

    # -------------------- 白天 --------------------

    def spend_day_turn(self) -> None:
        if self.phase != "day":
            return

        self.day_turns_left = max(0, self.day_turns_left - 1)

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

        self.discovered.add(target)
        self.discovered.update(neighbors(target))

        self.log(f"移動到 {target}。")
        self.spend_day_turn()
        return True

    def can_move_night_to(self, target: tuple[int, int]) -> bool:
        """夜晚可移動到相鄰、可通行且沒有敵人的格子。"""
        if self.phase != "night":
            return False

        if target not in neighbors(self.player):
            return False

        if self.terrain[target] == "water":
            return False

        if self.enemies_at(target):
            return False

        # 玩家可以穿越自己建造的木牆防線。
        # 木牆只阻擋敵人，不阻擋玩家夜間移動。
        return True

    def move_night_to(self, target: tuple[int, int]) -> bool:
        """夜晚移動 1 格，並消耗 1 個夜晚回合。"""
        if not self.can_move_night_to(target):
            self.log("夜晚只能移動到相鄰、可通行且沒有敵人的格子。")
            return False

        self.player = target
        self.selected_tile = target
        self.log(f"你在夜色中移動到 {target}。")

        self.advance_night_turn()
        return True

    def path_is_walkable(self, tile: tuple[int, int]) -> bool:
        """Return whether the player may route through a map tile."""
        return self.terrain[tile] != "water"

    def preview_drag_path(
        self,
        target: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """Return the current shortest path used by drag movement."""
        if self.phase not in ("day", "night"):
            return None

        blocked: set[tuple[int, int]] = set()

        if self.phase == "night":
            blocked = {
                enemy.position
                for enemy in self.alive_enemies()
            }
            blocked.discard(self.player)

        return find_hex_path(
            self.player,
            target,
            is_walkable=self.path_is_walkable,
            blocked=blocked,
        )

    def execute_drag_path(
        self,
        path: list[tuple[int, int]] | None,
    ) -> bool:
        """Execute a previewed drag path while preserving turn costs.

        Day:
            Every crossed hex edge costs one day turn. If the entire
            path costs more turns than remain, the move is rejected
            before the player moves at all.

        Night:
            Every crossed hex edge costs one night turn and triggers
            the normal enemy phase. The route stops immediately if the
            phase changes, the player dies, or the next tile becomes
            blocked by an enemy.
        """
        if not path:
            return False

        if path[0] != self.player:
            return False

        movement_cost = len(path) - 1

        if movement_cost <= 0:
            return False

        if self.phase == "day":
            if movement_cost > self.day_turns_left:
                self.log(
                    f"路徑需要 {movement_cost} 回合，"
                    f"但目前只剩 {self.day_turns_left} 回合。"
                )
                return False

            destination = path[-1]

            for step in path[1:]:
                if self.phase != "day":
                    break

                if not self.move_to(step):
                    return False

            if self.player == destination:
                self.log(
                    f"快速移動完成，共消耗 {movement_cost} 回合。"
                )

            return True

        if self.phase == "night":
            if movement_cost > self.night_turns_left:
                self.log(
                    f"夜間路徑需要 {movement_cost} 回合，"
                    f"但目前只剩 {self.night_turns_left} 回合。"
                )
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

    def resource_type_at(self, tile: tuple[int, int]) -> str | None:
        terrain = self.terrain[tile]

        if terrain == "forest":
            return "wood"
        if terrain == "rock":
            return "stone"
        if terrain == "grass":
            return "food"

        return None

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
        amount = 2 if resource == "wood" and self.has_axe else 1
        amount = min(amount, self.resources[tile])

        self.resources[tile] -= amount
        self.inventory.add(resource, amount)

        self.log(f"採集到 {amount} 個{RESOURCE_NAMES[resource]}。")
        self.spend_day_turn()
        return True

    def can_build_at(self, tile: tuple[int, int]) -> bool:
        return (
            self.phase == "day"
            and tile in self.discovered
            and tile != CAMP_POSITION
            and self.terrain[tile] != "water"
            and hex_distance(self.player, tile) <= 2
            and self.buildings.get_building(tile) is None
        )

    def build_at(self, building_type: str, tile: tuple[int, int]) -> bool:
        if not self.can_build_at(tile):
            self.log("這個位置無法建造；必須是已探索、距離 2 格內的空地。")
            return False

        success = self.buildings.build(
            building_type,
            tile,
            self.inventory,
        )

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

    def eat(self) -> bool:
        if self.phase != "day":
            return False

        if not self.survival.eat(self.inventory):
            self.log("背包裡沒有足夠食物。")
            return False

        self.log("吃下一份食物，飢餓值降低。")
        self.spend_day_turn()
        return True

    def add_firewood_day(self) -> bool:
        if self.phase != "day":
            return False

        success = (
            self.campfire.add_fuel(self.inventory)
            if self.campfire.lit
            else self.campfire.relight(self.inventory)
        )

        if not success:
            self.log("需要木材才能補充或重新點燃營火。")
            return False

        self.log(f"營火燃料目前為 {self.campfire.fuel}/12。")
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

    # -------------------- 夜晚 --------------------

    def start_night(self) -> None:
        if self.phase != "day":
            return

        self.player = CAMP_POSITION
        self.selected_tile = CAMP_POSITION

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

        self.log(f"夜晚開始：{wolves} 隻狼、{boars} 隻野豬從地圖邊緣出現！")

    def spawn_enemies(self) -> None:
        wolf_count = min(3 + self.day, 7)
        boar_count = 0 if self.day < 2 else min(1 + (self.day - 2) // 2, 3)
        total = wolf_count + boar_count

        candidates = []

        for r in range(MAP_ROWS):
            for q in range(MAP_COLS):
                tile = (q, r)

                if q in (0, MAP_COLS - 1) or r in (0, MAP_ROWS - 1):
                    if tile != CAMP_POSITION and self.terrain[tile] != "water":
                        candidates.append(tile)

        rng = random.Random(1000 + self.day)
        rng.shuffle(candidates)

        if len(candidates) < total:
            positions = [rng.choice(candidates) for _ in range(total)]
        else:
            positions = candidates[:total]

        self.enemies = []

        index = 0

        for _ in range(wolf_count):
            self.enemies.append(create_enemy(ENEMY_WOLF, positions[index]))
            index += 1

        for _ in range(boar_count):
            self.enemies.append(create_enemy(ENEMY_BOAR, positions[index]))
            index += 1

    def alive_enemies(self):
        return [enemy for enemy in self.enemies if enemy.alive]

    def enemies_at(self, tile: tuple[int, int]):
        return [
            enemy
            for enemy in self.enemies
            if enemy.alive and enemy.position == tile
        ]

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

    def attack_enemy_at(self, tile: tuple[int, int]) -> bool:
        if self.phase != "night":
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
        damage = calculate_player_damage(self.has_spear)
        defeated = damage_enemy(enemy, damage)

        name = "狼" if enemy.enemy_type == ENEMY_WOLF else "野豬"
        self.log(f"你攻擊{name}，造成 {damage} 點傷害。")

        if defeated:
            self.collect_loot(enemy)

        self.advance_night_turn()
        return True

    def add_firewood_night(self) -> bool:
        if self.phase != "night":
            return False

        success = (
            self.campfire.add_fuel(self.inventory)
            if self.campfire.lit
            else self.campfire.relight(self.inventory)
        )

        if not success:
            self.log("沒有木材，無法處理營火。")
            return False

        self.log(f"你處理了營火，目前燃料 {self.campfire.fuel}/12。")
        self.advance_night_turn()
        return True

    def pass_night_turn(self) -> bool:
        if self.phase != "night":
            return False

        self.log("你選擇等待一回合。")
        self.advance_night_turn()
        return True

    def advance_night_turn(self) -> None:
        if self.phase != "night":
            return

        self.night_turns_left = max(0, self.night_turns_left - 1)

        self.enemy_phase()

        if self.phase != "night":
            return

        self.campfire.consume(1)

        if not self.campfire.lit:
            self.log("營火熄滅，狼群不再害怕靠近營地！")

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

    def enemy_phase(self) -> None:
        for enemy in list(self.alive_enemies()):
            if not enemy.alive:
                continue

            if enemy.position == self.player or enemy.position == CAMP_POSITION:
                self.enemy_attack_player(enemy)

                if self.survival.is_dead():
                    return

                continue

            for _ in range(enemy.move_range):
                keep_moving = self.enemy_step(enemy)

                if not enemy.alive:
                    break

                if enemy.position == self.player or enemy.position == CAMP_POSITION:
                    self.enemy_attack_player(enemy)
                    break

                if not keep_moving:
                    break

            if self.survival.is_dead():
                return

    def enemy_step(self, enemy) -> bool:
        current_distance = hex_distance(enemy.position, CAMP_POSITION)
        candidates = []

        for candidate in neighbors(enemy.position):
            if self.terrain[candidate] == "water":
                continue

            candidate_distance = hex_distance(candidate, CAMP_POSITION)

            if candidate_distance >= current_distance:
                continue

            if (
                enemy.enemy_type == ENEMY_WOLF
                and self.campfire.lit
                and candidate_distance <= 1
            ):
                continue

            candidates.append(candidate)

        if not candidates:
            return False

        candidates.sort(
            key=lambda tile: (
                hex_distance(tile, CAMP_POSITION),
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

        if (
            building is not None
            and building.building_type == BUILD_TRAP
            and building.active
        ):
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

    def finish_night(self) -> None:
        self.enemies = []
        self.day += 1
        self.phase = "day"

        self.day_turns_left = DAY_TURNS
        self.night_turns_left = 0

        self.player = CAMP_POSITION
        self.selected_tile = CAMP_POSITION

        self.discovered.add(CAMP_POSITION)
        self.discovered.update(neighbors(CAMP_POSITION))

        self.log(f"太陽升起，第 {self.day} 天開始。你重新獲得 20 回合。")

    # -------------------- 右鍵情境選單 --------------------

    def context_actions(self, tile: tuple[int, int]) -> list[tuple[str, str, bool]]:
        if self.phase == "day":
            return [
                ("move", "移動到這裡", self.can_move_to(tile)),
                ("gather", "採集這裡", self.can_gather_at(tile)),
                (
                    "wall",
                    "建造木牆（3 木材）",
                    self.can_build_at(tile) and self.inventory.has({"wood": 3}),
                ),
                (
                    "trap",
                    "建造陷阱（2 木材 + 1 石頭）",
                    self.can_build_at(tile)
                    and self.inventory.has({"wood": 2, "stone": 1}),
                ),
            ]

        if self.phase == "night":
            enemies = self.enemies_at(tile)
            attack_range = 2 if self.has_spear else 1
            can_attack = (
                bool(enemies)
                and hex_distance(self.player, tile) <= attack_range
            )

            return [
                ("night_move", "移動到這裡", self.can_move_night_to(tile)),
                ("attack", "攻擊這個敵人", can_attack),
                (
                    "fire",
                    "補充 / 重新點燃營火",
                    self.inventory.get("wood") > 0,
                ),
                ("wait", "結束這個夜晚回合", True),
            ]

        return []

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
        elif action == "attack":
            self.attack_enemy_at(tile)
        elif action == "fire":
            if self.phase == "day":
                self.add_firewood_day()
            else:
                self.add_firewood_night()
        elif action == "wait":
            self.pass_night_turn()


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


def draw_tree(surface, center) -> None:
    x, y = center

    pygame.draw.rect(surface, (92, 63, 40), pygame.Rect(x - 2, y, 4, 10))
    pygame.draw.circle(surface, (35, 69, 40), (x, y - 6), 8)
    pygame.draw.circle(surface, (48, 89, 50), (x - 6, y), 6)
    pygame.draw.circle(surface, (55, 101, 57), (x + 6, y), 6)


def draw_terrain_detail(surface, terrain, center) -> None:
    x, y = center

    if terrain == "forest":
        draw_tree(surface, (x, y - 3))
        draw_tree(surface, (x - 12, y + 6))
        draw_tree(surface, (x + 12, y + 6))

    elif terrain == "rock":
        pygame.draw.polygon(
            surface,
            (146, 143, 136),
            [
                (x - 14, y + 9),
                (x - 9, y - 7),
                (x, y - 13),
                (x + 12, y - 5),
                (x + 15, y + 9),
            ],
        )

    elif terrain == "water":
        for offset in (-8, 2, 11):
            pygame.draw.arc(
                surface,
                (106, 163, 198),
                pygame.Rect(x - 15, y + offset - 4, 30, 8),
                math.pi,
                math.pi * 2,
                1,
            )

    else:
        for offset in (-11, 0, 11):
            pygame.draw.line(
                surface,
                (128, 155, 90),
                (x + offset, y + 9),
                (x + offset + 3, y + 1),
                1,
            )


def draw_player(surface, center, has_spear, has_axe) -> None:
    x, y = center

    pygame.draw.ellipse(surface, (24, 23, 21), pygame.Rect(x - 15, y + 14, 30, 9))

    pygame.draw.line(surface, (78, 53, 37), (x - 5, y + 7), (x - 9, y + 18), 4)
    pygame.draw.line(surface, (78, 53, 37), (x + 5, y + 7), (x + 9, y + 18), 4)

    pygame.draw.polygon(
        surface,
        (151, 92, 51),
        [
            (x - 11, y - 6),
            (x + 11, y - 6),
            (x + 9, y + 10),
            (x, y + 15),
            (x - 9, y + 10),
        ],
    )

    pygame.draw.line(surface, (221, 160, 85), (x - 8, y + 2), (x + 8, y + 2), 2)

    pygame.draw.line(surface, (204, 150, 101), (x - 8, y - 2), (x - 15, y + 6), 4)
    pygame.draw.line(surface, (204, 150, 101), (x + 8, y - 2), (x + 15, y + 5), 4)

    pygame.draw.circle(surface, (209, 156, 108), (x, y - 16), 9)
    pygame.draw.arc(
        surface,
        (51, 39, 32),
        pygame.Rect(x - 10, y - 26, 20, 17),
        math.pi,
        math.pi * 2,
        5,
    )

    pygame.draw.circle(surface, BLACK, (x - 3, y - 16), 1)
    pygame.draw.circle(surface, BLACK, (x + 3, y - 16), 1)

    if has_spear:
        pygame.draw.line(surface, (112, 74, 42), (x + 13, y + 11), (x + 21, y - 25), 3)
        pygame.draw.polygon(
            surface,
            (194, 194, 185),
            [
                (x + 21, y - 32),
                (x + 17, y - 23),
                (x + 24, y - 24),
            ],
        )

    elif has_axe:
        pygame.draw.line(surface, (112, 74, 42), (x + 14, y + 8), (x + 19, y - 15), 3)
        pygame.draw.polygon(
            surface,
            (168, 170, 164),
            [
                (x + 17, y - 18),
                (x + 30, y - 21),
                (x + 26, y - 10),
                (x + 18, y - 11),
            ],
        )


def draw_campfire(surface, center, lit) -> None:
    x, y = center

    pygame.draw.line(surface, (96, 58, 31), (x - 11, y + 8), (x + 11, y + 2), 5)
    pygame.draw.line(surface, (96, 58, 31), (x - 11, y + 2), (x + 11, y + 8), 5)

    if lit:
        pulse = 2 + int(abs(math.sin(pygame.time.get_ticks() / 170)) * 2)

        pygame.draw.polygon(
            surface,
            (241, 93, 39),
            [
                (x, y - 20 - pulse),
                (x - 10, y + 4),
                (x, y),
                (x + 10, y + 4),
            ],
        )

        pygame.draw.polygon(
            surface,
            (255, 205, 72),
            [
                (x, y - 11 - pulse),
                (x - 5, y + 2),
                (x + 5, y + 2),
            ],
        )


def draw_wall(surface, center, hp, max_hp) -> None:
    x, y = center

    for offset in (-12, 0, 12):
        pygame.draw.rect(
            surface,
            (122, 81, 45),
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


def draw_wolf(surface, center, hp, max_hp) -> None:
    """繪製較完整的灰狼：身體、頭、口鼻、耳朵、尾巴與腿。"""
    x, y = center

    outline = (42, 45, 49)
    fur_dark = (63, 69, 75)
    fur_mid = (88, 95, 103)
    fur_light = (132, 138, 142)
    muzzle = (159, 157, 146)
    eye = (244, 186, 65)

    # 地面影子
    pygame.draw.ellipse(
        surface,
        (24, 25, 27),
        pygame.Rect(x - 23, y + 12, 47, 9),
    )

    # 尾巴：向後上方翹起，讓輪廓更像狼
    pygame.draw.lines(
        surface,
        outline,
        False,
        [
            (x - 15, y - 1),
            (x - 25, y - 8),
            (x - 29, y - 17),
            (x - 24, y - 20),
        ],
        8,
    )
    pygame.draw.lines(
        surface,
        fur_mid,
        False,
        [
            (x - 15, y - 1),
            (x - 25, y - 8),
            (x - 29, y - 17),
            (x - 24, y - 20),
        ],
        5,
    )

    # 身體外框與主色
    pygame.draw.ellipse(
        surface,
        outline,
        pygame.Rect(x - 19, y - 10, 38, 25),
    )
    pygame.draw.ellipse(
        surface,
        fur_mid,
        pygame.Rect(x - 17, y - 9, 34, 22),
    )

    # 背部深色毛
    pygame.draw.arc(
        surface,
        fur_dark,
        pygame.Rect(x - 15, y - 8, 31, 15),
        math.pi,
        math.pi * 2,
        4,
    )

    # 胸口
    pygame.draw.polygon(
        surface,
        fur_light,
        [
            (x + 7, y - 5),
            (x + 15, y + 1),
            (x + 8, y + 11),
            (x + 2, y + 6),
        ],
    )

    # 頸部外框
    pygame.draw.polygon(
        surface,
        outline,
        [
            (x + 6, y - 8),
            (x + 15, y - 16),
            (x + 23, y - 9),
            (x + 18, y + 5),
            (x + 7, y + 4),
        ],
    )
    pygame.draw.polygon(
        surface,
        fur_mid,
        [
            (x + 8, y - 7),
            (x + 15, y - 14),
            (x + 21, y - 8),
            (x + 16, y + 3),
            (x + 8, y + 2),
        ],
    )

    # 頭部
    pygame.draw.ellipse(
        surface,
        outline,
        pygame.Rect(x + 9, y - 23, 24, 20),
    )
    pygame.draw.ellipse(
        surface,
        fur_mid,
        pygame.Rect(x + 11, y - 22, 20, 18),
    )

    # 尖耳
    pygame.draw.polygon(
        surface,
        outline,
        [
            (x + 12, y - 19),
            (x + 13, y - 31),
            (x + 20, y - 21),
        ],
    )
    pygame.draw.polygon(
        surface,
        fur_dark,
        [
            (x + 14, y - 21),
            (x + 14, y - 28),
            (x + 18, y - 21),
        ],
    )

    pygame.draw.polygon(
        surface,
        outline,
        [
            (x + 22, y - 21),
            (x + 28, y - 30),
            (x + 29, y - 18),
        ],
    )
    pygame.draw.polygon(
        surface,
        fur_dark,
        [
            (x + 24, y - 21),
            (x + 27, y - 27),
            (x + 27, y - 20),
        ],
    )

    # 口鼻向前突出
    pygame.draw.ellipse(
        surface,
        outline,
        pygame.Rect(x + 23, y - 15, 17, 11),
    )
    pygame.draw.ellipse(
        surface,
        muzzle,
        pygame.Rect(x + 24, y - 14, 14, 9),
    )

    # 鼻子與眼睛
    pygame.draw.circle(surface, (24, 24, 25), (x + 38, y - 9), 3)
    pygame.draw.circle(surface, eye, (x + 25, y - 15), 2)
    pygame.draw.circle(surface, (25, 22, 18), (x + 25, y - 15), 1)

    # 四肢
    for leg_x in (x - 11, x - 3, x + 7, x + 13):
        pygame.draw.line(
            surface,
            outline,
            (leg_x, y + 8),
            (leg_x - 1, y + 18),
            5,
        )
        pygame.draw.line(
            surface,
            fur_dark,
            (leg_x, y + 8),
            (leg_x - 1, y + 17),
            3,
        )

    # HP 條
    ratio = max(0, hp) / max_hp
    pygame.draw.rect(
        surface,
        (44, 45, 47),
        pygame.Rect(x - 22, y + 24, 48, 6),
        border_radius=3,
    )
    pygame.draw.rect(
        surface,
        RED,
        pygame.Rect(x - 22, y + 24, int(48 * ratio), 6),
        border_radius=3,
    )

def draw_boar(surface, center, hp, max_hp) -> None:
    x, y = center

    pygame.draw.ellipse(surface, (100, 66, 46), pygame.Rect(x - 17, y - 8, 30, 19))
    pygame.draw.circle(surface, (112, 75, 50), (x + 13, y - 3), 9)

    pygame.draw.polygon(
        surface,
        (85, 55, 40),
        [(x + 7, y - 10), (x + 10, y - 19), (x + 14, y - 9)],
    )

    pygame.draw.circle(surface, BLACK, (x + 16, y - 5), 2)

    pygame.draw.arc(
        surface,
        (231, 220, 184),
        pygame.Rect(x + 13, y - 1, 12, 10),
        0,
        math.pi,
        2,
    )

    pygame.draw.line(surface, (81, 54, 39), (x - 10, y + 7), (x - 11, y + 16), 4)
    pygame.draw.line(surface, (81, 54, 39), (x + 5, y + 7), (x + 6, y + 16), 4)

    ratio = max(0, hp) / max_hp
    pygame.draw.rect(surface, (48, 48, 48), pygame.Rect(x - 18, y + 20, 36, 5))
    pygame.draw.rect(surface, RED, pygame.Rect(x - 18, y + 20, int(36 * ratio), 5))


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
    if game.phase == "day":
        entries = [
            ("eat", "吃食物", game.inventory.get("food") > 0),
            ("fire_day", "加入柴火", game.inventory.get("wood") > 0),
            (
                "spear",
                "製作石矛",
                not game.has_spear
                and game.inventory.has({"wood": 2, "stone": 1}),
            ),
            (
                "axe",
                "製作石斧",
                not game.has_axe
                and game.inventory.has({"wood": 1, "stone": 2}),
            ),
            (
                "armor",
                "製作護甲",
                game.inventory.has({"hide": 2, "stone": 1}),
            ),
        ]
        y = 520

    elif game.phase == "night":
        entries = [
            ("fire_night", "加入柴火", game.inventory.get("wood") > 0),
            ("wait", "結束這回合", True),
        ]
        y = 555

    else:
        entries = [("restart", "重新開始", True)]
        y = 545

    buttons = []

    for index, (action, label, enabled) in enumerate(entries):
        row = index // 2
        col = index % 2

        rect = pygame.Rect(
            855 + col * 185,
            y + row * 42,
            170,
            34,
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
    elif action == "armor":
        game.craft_armor()
    elif action == "fire_night":
        game.add_firewood_night()
    elif action == "wait":
        game.pass_night_turn()
    elif action == "restart":
        game.reset()



def recipe_button_rect() -> pygame.Rect:
    """HUD button used to open/close the recipe catalog."""
    return pygame.Rect(855, 646, 355, 34)


def recipe_modal_rect() -> pygame.Rect:
    """Main recipe modal bounds."""
    return pygame.Rect(310, 82, 660, 556)


def recipe_close_rect() -> pygame.Rect:
    """Close button in the top-right corner of the recipe modal."""
    modal = recipe_modal_rect()
    return pygame.Rect(modal.right - 48, modal.y + 14, 32, 32)


def draw_recipe_modal(surface, fonts) -> None:
    """Draw the recipe catalog as a modal overlay.

    This is intentionally a functional/basic UI. The art branch can
    later replace only the rendering while keeping RECIPE_CATALOG as
    the shared data source.
    """
    shade = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA,
    )
    shade.fill((0, 0, 0, 150))
    surface.blit(shade, (0, 0))

    modal = recipe_modal_rect()

    pygame.draw.rect(
        surface,
        (25, 28, 31),
        modal,
        border_radius=16,
    )
    pygame.draw.rect(
        surface,
        GOLD,
        modal,
        2,
        border_radius=16,
    )

    text(
        surface,
        fonts["heading"],
        "合成清單",
        modal.x + 28,
        modal.y + 22,
        GOLD_LIGHT,
    )
    text(
        surface,
        fonts["tiny"],
        "查看配方不會消耗任何回合｜ESC 或右上角 X 關閉",
        modal.x + 28,
        modal.y + 55,
        MUTED,
    )

    close = recipe_close_rect()
    mouse = pygame.mouse.get_pos()
    close_fill = (112, 58, 52) if close.collidepoint(mouse) else PANEL_2

    pygame.draw.rect(
        surface,
        close_fill,
        close,
        border_radius=7,
    )
    pygame.draw.rect(
        surface,
        RED,
        close,
        1,
        border_radius=7,
    )
    centered_text(
        surface,
        fonts["body"],
        "X",
        close.center,
        TEXT,
    )

    y = modal.y + 92

    for category in ("裝備", "建造"):
        text(
            surface,
            fonts["body"],
            category,
            modal.x + 28,
            y,
            GOLD_LIGHT if category == "裝備" else BLUE,
        )
        y += 29

        recipes = [
            recipe
            for recipe in RECIPE_CATALOG
            if recipe["category"] == category
        ]

        for recipe in recipes:
            row = pygame.Rect(
                modal.x + 24,
                y,
                modal.width - 48,
                64,
            )

            pygame.draw.rect(
                surface,
                PANEL_2,
                row,
                border_radius=9,
            )
            pygame.draw.rect(
                surface,
                (72, 76, 81),
                row,
                1,
                border_radius=9,
            )

            text(
                surface,
                fonts["small"],
                recipe["name"],
                row.x + 14,
                row.y + 8,
                TEXT,
            )
            text(
                surface,
                fonts["tiny"],
                f"成本：{recipe['cost_text']}",
                row.x + 125,
                row.y + 10,
                GOLD_LIGHT,
            )
            text(
                surface,
                fonts["tiny"],
                f"效果：{recipe['effect']}",
                row.x + 14,
                row.y + 36,
                MUTED,
            )

            y += 70

        y += 8

def context_menu_rows(game, tile, origin):
    actions = game.context_actions(tile)

    width = 250
    row_height = 36
    total_height = len(actions) * row_height + 10

    x = min(origin[0], SCREEN_WIDTH - width - 10)
    y = min(origin[1], SCREEN_HEIGHT - total_height - 10)

    x = max(10, x)
    y = max(10, y)

    rows = []

    for index, (action, label, enabled) in enumerate(actions):
        rect = pygame.Rect(
            x + 5,
            y + 5 + index * row_height,
            width - 10,
            row_height - 4,
        )
        rows.append((action, label, enabled, rect))

    return rows


def draw_context_menu(surface, fonts, game, tile, origin) -> None:
    rows = context_menu_rows(game, tile, origin)

    if not rows:
        return

    first = rows[0][3]
    last = rows[-1][3]

    background = pygame.Rect(
        first.x - 5,
        first.y - 5,
        first.width + 10,
        last.bottom - first.y + 10,
    )

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


def draw_selected_tile_info(surface, fonts, game) -> None:
    tile = game.selected_tile

    text(surface, fonts["small"], "目前選取", 855, 430, MUTED)
    text(surface, fonts["body"], f"六角格 {tile}", 855, 451, GOLD_LIGHT)

    if tile not in game.discovered and game.phase == "day":
        text(surface, fonts["small"], "尚未探索", 1050, 454, MUTED)
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

    text(surface, fonts["small"], detail, 1050, 454, TEXT)


def draw_game(screen, fonts, game, context_tile, context_origin, drag_path=None, recipe_open=False) -> None:
    screen.fill(BG)

    pygame.draw.rect(screen, TOP, pygame.Rect(0, 0, SCREEN_WIDTH, 62))

    text(screen, fonts["heading"], "石器時代：荒野求生 v5", 28, 18, GOLD_LIGHT)
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

    pill = pygame.Rect(920, 14, 130, 34)
    pygame.draw.rect(screen, phase_color, pill, border_radius=17)
    centered_text(screen, fonts["small"], phase_label, pill.center, BLACK)

    text(screen, fonts["small"], turn_label, 1070, 22, phase_color)

    panel(screen, MAP_PANEL, (23, 26, 29), 16)
    panel(screen, HUD_PANEL, PANEL, 16)
    panel(screen, LOG_PANEL, (23, 26, 29), 14)

    hover_tile = tile_at_pixel(pygame.mouse.get_pos())

    for r in range(MAP_ROWS):
        for q in range(MAP_COLS):
            tile = (q, r)
            center = axial_to_pixel(tile)
            discovered = tile in game.discovered

            if game.phase == "night":
                discovered = True

            fill = terrain_color(game.terrain[tile]) if discovered else FOG
            points = hex_points(center)

            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, (57, 61, 64), points, 1)

            if discovered:
                draw_terrain_detail(screen, game.terrain[tile], center)

                amount = game.resources.get(tile, 0)

                if amount > 0:
                    text(
                        screen,
                        fonts["tiny"],
                        amount,
                        center[0] + 16,
                        center[1] + 12,
                        (238, 220, 150),
                    )

            if tile == hover_tile:
                pygame.draw.polygon(screen, (221, 221, 205), points, 2)

            if tile == game.selected_tile:
                pygame.draw.polygon(screen, GOLD_LIGHT, points, 3)

    # 拖曳中的最短路徑預覽。
    if drag_path and len(drag_path) > 1:
        centers = [
            axial_to_pixel(tile)
            for tile in drag_path
        ]

        pygame.draw.lines(
            screen,
            GOLD_LIGHT,
            False,
            centers,
            4,
        )

        for index, tile in enumerate(drag_path):
            center = axial_to_pixel(tile)

            pygame.draw.polygon(
                screen,
                GOLD_LIGHT,
                hex_points(center),
                3,
            )

            if index > 0:
                marker_radius = 7 if index == len(drag_path) - 1 else 5

                pygame.draw.circle(
                    screen,
                    (255, 235, 160),
                    center,
                    marker_radius,
                )

        cost = len(drag_path) - 1
        destination = axial_to_pixel(drag_path[-1])

        text(
            screen,
            fonts["tiny"],
            f"移動成本：{cost} 回合",
            destination[0] + 18,
            destination[1] - 30,
            GOLD_LIGHT,
        )

    if game.phase == "night":
        tint = pygame.Surface((MAP_PANEL.width, MAP_PANEL.height), pygame.SRCALPHA)
        tint.fill((5, 10, 27, 72))
        screen.blit(tint, MAP_PANEL.topleft)

    if game.phase == "night" and game.campfire.lit:
        center = axial_to_pixel(CAMP_POSITION)
        glow = pygame.Surface((300, 300), pygame.SRCALPHA)

        pygame.draw.circle(glow, (255, 153, 50, 38), (150, 150), 125)
        pygame.draw.circle(glow, (255, 195, 78, 20), (150, 150), 148)

        screen.blit(glow, (center[0] - 150, center[1] - 150))

    for building in game.buildings.buildings.values():
        center = axial_to_pixel(building.position)

        if building.building_type == BUILD_WALL:
            draw_wall(screen, center, building.hp, building.max_hp)
        else:
            draw_trap(screen, center, building.active)

    draw_campfire(screen, axial_to_pixel(CAMP_POSITION), game.campfire.lit)

    enemy_groups = {}

    for enemy in game.alive_enemies():
        enemy_groups.setdefault(enemy.position, []).append(enemy)

    for tile, enemies in enemy_groups.items():
        base_x, base_y = axial_to_pixel(tile)

        for index, enemy in enumerate(enemies[:3]):
            offset_x = (index - 1) * 12 if len(enemies) > 1 else 0
            center = (base_x + offset_x, base_y - 3)

            max_hp = 30 if enemy.enemy_type == ENEMY_WOLF else 55

            if enemy.enemy_type == ENEMY_WOLF:
                draw_wolf(screen, center, enemy.health, max_hp)
            else:
                draw_boar(screen, center, enemy.health, max_hp)

        if len(enemies) > 3:
            text(
                screen,
                fonts["tiny"],
                f"+{len(enemies) - 3}",
                base_x + 19,
                base_y - 27,
                RED,
            )

    draw_player(
        screen,
        axial_to_pixel(game.player),
        game.has_spear,
        game.has_axe,
    )

    text(screen, fonts["small"], "生存紀錄", 38, 607, GOLD_LIGHT)

    y = 635

    for message in game.logs[-3:]:
        text(screen, fonts["small"], "• " + message[:72], 38, y, MUTED)
        y += 21

    text(screen, fonts["heading"], "生存狀態", 855, 102)

    draw_bar(screen, fonts, 855, 141, 175, "生命", game.survival.health, 100, RED)
    draw_bar(screen, fonts, 1050, 141, 175, "護甲", game.survival.armor, 50, BLUE)
    draw_bar(screen, fonts, 855, 194, 370, "飢餓", game.survival.hunger, 100, GOLD)

    resource_values = [
        ("食物", game.inventory.get("food"), (178, 87, 63)),
        ("木材", game.inventory.get("wood"), (133, 88, 52)),
        ("石頭", game.inventory.get("stone"), (147, 147, 143)),
        ("獸皮", game.inventory.get("hide"), (162, 118, 72)),
    ]

    for index, (label, value, color) in enumerate(resource_values):
        row = index // 2
        col = index % 2

        rect = pygame.Rect(
            855 + col * 185,
            250 + row * 58,
            170,
            48,
        )

        pygame.draw.rect(screen, PANEL_2, rect, border_radius=9)
        pygame.draw.circle(screen, color, (rect.x + 20, rect.centery), 8)

        text(screen, fonts["tiny"], label, rect.x + 36, rect.y + 7, MUTED)
        text(screen, fonts["body"], value, rect.x + 36, rect.y + 22, TEXT)

    fire_rect = pygame.Rect(855, 372, 355, 44)
    pygame.draw.rect(screen, PANEL_2, fire_rect, border_radius=9)

    fire_text = "燃燒中" if game.campfire.lit else "已熄滅"

    text(screen, fonts["small"], "營火", 870, 384, MUTED)
    text(
        screen,
        fonts["small"],
        f"{fire_text}｜燃料 {game.campfire.fuel}/12",
        945,
        384,
        GOLD_LIGHT if game.campfire.lit else RED,
    )

    draw_selected_tile_info(screen, fonts, game)

    if game.phase == "day":
        text(screen, fonts["small"], "拖曳角色快速移動｜右鍵：採集 / 建造", 855, 487, GOLD_LIGHT)

    elif game.phase == "night":
        text(screen, fonts["small"], "拖曳角色＝移動｜左鍵敵人＝攻擊", 855, 487, BLUE)

    else:
        text(screen, fonts["small"], "你沒有撐過這次荒野求生。", 855, 487, RED)

    for action, label, rect, enabled in hud_buttons(game):
        draw_button(
            screen,
            fonts,
            rect,
            label,
            enabled,
            accent=action in ("wait", "restart"),
        )

    draw_button(
        screen,
        fonts,
        recipe_button_rect(),
        "關閉合成清單" if recipe_open else "合成清單",
        True,
        accent=recipe_open,
    )

    if context_tile is not None and not recipe_open:
        draw_context_menu(screen, fonts, game, context_tile, context_origin)

    if recipe_open:
        draw_recipe_modal(screen, fonts)


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
    return pygame.Rect(490, 445, 300, 58)


def draw_menu(screen, fonts) -> None:
    screen.fill(BG)

    for row in range(9):
        for col in range(15):
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

    centered_text(
        screen,
        fonts["title"],
        "石器時代：荒野求生",
        (SCREEN_WIDTH // 2, 175),
        GOLD_LIGHT,
    )

    centered_text(
        screen,
        fonts["body"],
        "滑鼠回合制生存策略",
        (SCREEN_WIDTH // 2, 225),
        MUTED,
    )

    draw_campfire(screen, (SCREEN_WIDTH // 2, 340), True)

    draw_button(screen, fonts, menu_start_rect(), "開始遊戲", True, True)

    centered_text(
        screen,
        fonts["small"],
        "白天 20 回合｜夜晚 20 回合｜右鍵情境操作",
        (SCREEN_WIDTH // 2, 545),
        MUTED,
    )

    centered_text(
        screen,
        fonts["tiny"],
        "ESC 離開",
        (SCREEN_WIDTH // 2, 600),
        MUTED,
    )


def tutorial_buttons() -> dict[str, pygame.Rect]:
    return {
        "back": pygame.Rect(315, 560, 170, 42),
        "skip": pygame.Rect(555, 560, 170, 42),
        "next": pygame.Rect(795, 560, 170, 42),
    }


def draw_tutorial(screen, fonts, page: int) -> None:
    screen.fill(BG)

    card = pygame.Rect(180, 92, 920, 530)
    panel(screen, card, (29, 32, 36), 22)

    title_value, lines = TUTORIAL[page]

    text(
        screen,
        fonts["tiny"],
        f"新手教學 {page + 1}/{len(TUTORIAL)}",
        235,
        125,
        MUTED,
    )

    text(screen, fonts["title"], title_value, 235, 160, GOLD_LIGHT)

    y = 245

    for line in lines:
        pygame.draw.circle(screen, GOLD, (253, y + 10), 5)
        text(screen, fonts["body"], line, 278, y, TEXT)
        y += 58

    for index in range(len(TUTORIAL)):
        pygame.draw.circle(
            screen,
            GOLD if index == page else (75, 78, 82),
            (SCREEN_WIDTH // 2 - 45 + index * 30, 520),
            6,
        )

    buttons = tutorial_buttons()

    draw_button(screen, fonts, buttons["back"], "上一頁", page > 0)
    draw_button(screen, fonts, buttons["skip"], "跳過教學", True)
    draw_button(
        screen,
        fonts,
        buttons["next"],
        "開始遊戲" if page == len(TUTORIAL) - 1 else "下一頁",
        True,
        True,
    )


def main() -> None:
    pygame.init()
    pygame.display.set_caption("石器時代：荒野求生 v5 - 合成清單")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fonts = create_fonts()

    game = Game()

    view = "menu"
    tutorial_page = 0

    context_tile = None
    context_origin = (0, 0)

    dragging_player = False
    drag_path = None
    recipe_open = False

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if view == "game":
                        if recipe_open:
                            recipe_open = False
                        else:
                            context_tile = None
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
            # 玩家拖曳：移動中持續更新最短路徑預覽
            # -------------------------------------------------
            if (
                view == "game"
                and event.type == pygame.MOUSEMOTION
                and dragging_player
                and not recipe_open
            ):
                tile = tile_at_pixel(event.pos)

                if tile is None:
                    drag_path = None
                else:
                    game.selected_tile = tile
                    drag_path = game.preview_drag_path(tile)

                continue

            # -------------------------------------------------
            # 玩家拖曳：放開左鍵後才正式執行路徑
            # -------------------------------------------------
            if (
                view == "game"
                and event.type == pygame.MOUSEBUTTONUP
                and event.button == 1
                and dragging_player
            ):
                dragging_player = False

                if drag_path and len(drag_path) > 1:
                    game.execute_drag_path(drag_path)

                drag_path = None
                context_tile = None
                continue

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            mouse = event.pos

            if view == "menu":
                if event.button == 1 and menu_start_rect().collidepoint(mouse):
                    view = "tutorial"
                    tutorial_page = 0
                continue

            if view == "tutorial":
                if event.button != 1:
                    continue

                buttons = tutorial_buttons()

                if buttons["back"].collidepoint(mouse) and tutorial_page > 0:
                    tutorial_page -= 1

                elif buttons["skip"].collidepoint(mouse):
                    view = "game"

                elif buttons["next"].collidepoint(mouse):
                    if tutorial_page >= len(TUTORIAL) - 1:
                        view = "game"
                    else:
                        tutorial_page += 1

                continue

            if view != "game":
                continue

            # -------------------------------------------------
            # 合成清單 Modal
            # -------------------------------------------------
            if event.button == 1 and recipe_button_rect().collidepoint(mouse):
                recipe_open = not recipe_open
                context_tile = None
                dragging_player = False
                drag_path = None
                continue

            if recipe_open:
                if (
                    event.button == 1
                    and recipe_close_rect().collidepoint(mouse)
                ):
                    recipe_open = False

                # Modal 開啟期間完全阻擋地圖、HUD、攻擊與建造點擊，
                # 避免 UI click-through。
                continue

            if event.button == 3:
                tile = tile_at_pixel(mouse)

                if tile is not None and game.phase != "game_over":
                    game.selected_tile = tile
                    context_tile = tile
                    context_origin = mouse
                else:
                    context_tile = None

                continue

            if event.button != 1:
                continue

            clicked_menu = False

            if context_tile is not None:
                for action, label, enabled, rect in context_menu_rows(
                    game,
                    context_tile,
                    context_origin,
                ):
                    if rect.collidepoint(mouse):
                        clicked_menu = True

                        if enabled:
                            game.execute_context_action(action, context_tile)

                        context_tile = None
                        break

            if clicked_menu:
                continue

            clicked_hud = False

            for action, label, rect, enabled in hud_buttons(game):
                if rect.collidepoint(mouse):
                    clicked_hud = True

                    if enabled:
                        execute_hud_action(game, action)

                    context_tile = None
                    break

            if clicked_hud:
                continue

            tile = tile_at_pixel(mouse)

            # 只有從玩家目前所在的 hex 按住左鍵，才進入拖曳模式。
            if (
                tile == game.player
                and game.phase in ("day", "night")
            ):
                dragging_player = True
                drag_path = [game.player]
                context_tile = None
                continue

            if tile is not None:
                game.selected_tile = tile

                # 夜晚改成更直覺的滑鼠操作：
                # 左鍵相鄰空格 = 直接移動
                # 左鍵敵人格 = 直接攻擊
                if game.phase == "night":
                    if game.enemies_at(tile):
                        game.attack_enemy_at(tile)

                    elif game.can_move_night_to(tile):
                        game.move_night_to(tile)

            context_tile = None

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
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()