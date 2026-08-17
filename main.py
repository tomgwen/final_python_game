"""石器時代：荒野求生 - 可玩中文版 MVP"""

from __future__ import annotations

import random

import pygame

import pygame

# 引入剛才寫好的音效管理員
from audio_manager import audio

# --- 遊戲初始化設定 ---
pygame.init()

# 載入你的實體 .wav 檔案 (請將檔名替換成你實際下載的名稱)
audio.load_sound("click1", "click1.WAV")      # 介面點擊聲
audio.load_sound("chop", "chop.WAV")        # 砍樹聲
audio.load_sound("wolf", "wolf_howl.WAV")   # 狼嚎聲

from building import BuildingManager
from campfire import Campfire
from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    CAMP_POSITION,
    FPS,
    MAP_COLS,
    MAP_ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from inventory import Inventory
from survival import SurvivalStats
from ui import (
    TUTORIAL_PAGE_COUNT,
    create_fonts,
    draw_game,
    draw_menu,
)


MAX_ACTIONS = 6
MAX_NIGHT_ROUNDS = 4


# ============================================================
# 六角方向
# ============================================================

MOVE_KEYS = {
    pygame.K_w: (0, -1),
    pygame.K_e: (1, -1),
    pygame.K_d: (1, 0),
    pygame.K_x: (0, 1),
    pygame.K_z: (-1, 1),
    pygame.K_a: (-1, 0),
}


def valid_position(position):

    q, r = position

    return (
        0 <= q < MAP_COLS
        and 0 <= r < MAP_ROWS
    )


def neighbors(position):

    q, r = position

    result = []

    for dq, dr in (
        MOVE_KEYS.values()
    ):

        target = (
            q + dq,
            r + dr,
        )

        if valid_position(
            target
        ):

            result.append(
                target
            )

    return result


# ============================================================
# 建立地圖
# ============================================================

def create_world():

    rng = random.Random(7)

    terrain = {}
    resources = {}

    for r in range(
        MAP_ROWS
    ):

        for q in range(
            MAP_COLS
        ):

            position = (
                q,
                r,
            )

            roll = rng.random()

            if roll < 0.10:

                kind = "water"

            elif roll < 0.38:

                kind = "forest"

            elif roll < 0.58:

                kind = "rock"

            else:

                kind = "grass"

            if (
                position
                == CAMP_POSITION
            ):

                kind = "grass"

            terrain[
                position
            ] = kind

            if kind == "water":

                resources[
                    position
                ] = 0

            else:

                resources[
                    position
                ] = rng.randint(
                    1,
                    3,
                )

    return (
        terrain,
        resources,
    )


# ============================================================
# GAME
# ============================================================

class Game:

    def __init__(self):

        self.reset()

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self):

        (
            self.terrain,
            self.resources,
        ) = create_world()

        self.inventory = (
            Inventory()
        )

        self.survival = (
            SurvivalStats()
        )

        self.buildings = (
            BuildingManager()
        )

        self.campfire = (
            Campfire(
                CAMP_POSITION
            )
        )

        self.player = (
            CAMP_POSITION
        )

        self.discovered = {
            CAMP_POSITION
        }

        self.discovered.update(
            neighbors(
                CAMP_POSITION
            )
        )

        self.day = 1

        self.actions_left = (
            MAX_ACTIONS
        )

        self.phase = "day"

        self.has_spear = False
        self.has_axe = False

        self.night_round = 0

        self.enemies = []

        self.logs = [
            "你在陌生的石器時代荒野中醒來。",
            "趁天黑以前收集資源，準備今晚的防禦！",
        ]

    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    def log(self, message):

        self.logs.append(
            message
        )

        self.logs = (
            self.logs[-7:]
        )

    # ========================================================
    # DAY
    # ========================================================

    def move(self, direction):

        if self.phase != "day":
            return

        if self.actions_left < 1:

            self.log(
                "行動點數不足。"
            )

            return

        q, r = self.player

        dq, dr = direction

        target = (
            q + dq,
            r + dr,
        )

        if not valid_position(
            target
        ):

            self.log(
                "已經到達地圖邊界。"
            )

            return

        if (
            self.terrain[target]
            == "water"
        ):

            self.log(
                "前方是水域，無法通行。"
            )

            return

        self.player = target

        self.actions_left -= 1

        self.discovered.add(
            target
        )

        self.discovered.update(
            neighbors(
                target
            )
        )

        self.log(
            f"移動到 {target}。"
        )

    # --------------------------------------------------------
    # 採集
    # --------------------------------------------------------

    def gather(self):
        if self.phase != "day":
            return

        if self.actions_left < 1:
            self.log(
                "行動點數不足。"
            )
            return

        terrain = (
            self.terrain[
                self.player
            ]
        )

        amount_left = (
            self.resources[
                self.player
            ]
        )

        resource = None

        if terrain == "forest":
            resource = "wood"
        elif terrain == "rock":
            resource = "stone"
        elif terrain == "grass":
            resource = "food"

        if (
            resource is None
            or amount_left <= 0
        ):
            self.log(
                "這裡已經沒有可以採集的資源。"
            )
            return

        amount = 1

        # ==========================================
        # 咻一下優化區：依照資源種類播放音效與計算加成
        # ==========================================
        if resource == "wood":
            audio.play("chop")
            # 檢查是否有石斧，有的話採集量變 2
            if hasattr(self, 'has_axe') and self.has_axe:
                amount = 2
                
        elif resource == "stone":
            # 替換成你實際的敲石頭音效名稱
            audio.play("mine") 
            
        elif resource == "food":
            # 使用你剛剛加入的 click1 音效來當作採集草叢聲
            audio.play("click1") 
        # ==========================================

        # ... (這裡接著寫你原本把 amount 加進背包、扣除 action_left 的程式碼)

        # 石斧採木材 +1
        if (
            resource == "wood"
            and self.has_axe
        ):

            amount = 2
            audio.play("chop")

        amount = min(
            amount,
            amount_left,
        )

        self.resources[
            self.player
        ] -= amount

        self.inventory.add(
            resource,
            amount,
        )

        self.actions_left -= 1

        resource_names = {
            "wood": "木材",
            "stone": "石頭",
            "food": "食物",
        }

        self.log(
            f"取得 {amount} 個"
            f"{resource_names[resource]}。"
        )

    # --------------------------------------------------------
    # 吃東西
    # --------------------------------------------------------

    def eat(self):

        if self.phase != "day":
            return

        if self.actions_left < 1:

            self.log(
                "行動點數不足。"
            )

            return

        if self.survival.eat(
            self.inventory
        ):

            self.actions_left -= 1

            self.log(
                "你吃了一份食物，飢餓感降低。"
            )

        else:

            self.log(
                "背包裡沒有食物。"
            )

    # --------------------------------------------------------
    # 營火
    # --------------------------------------------------------

    def add_firewood(self):

        if (
            self.phase == "day"
            and self.actions_left < 1
        ):

            self.log(
                "行動點數不足。"
            )

            return False

        if self.campfire.lit:

            success = (
                self.campfire
                .add_fuel(
                    self.inventory
                )
            )

        else:

            success = (
                self.campfire
                .relight(
                    self.inventory
                )
            )

        if not success:

            self.log(
                "無法加入柴火，可能是木材不足。"
            )

            return False

        # ==========================================
        # ▼ ▼ 加在這裡：成功加入柴火或重新點燃時播放音效 ▼ ▼
        # ==========================================
        audio.play_sfx("fire")
        # ==========================================

        if self.phase == "day":

            self.actions_left -= 1

        self.log(
            "營火燃料增加，"
            f"目前 {self.campfire.fuel}/12。"
        )

        return True
    # --------------------------------------------------------
    # 石矛
    # --------------------------------------------------------

    def craft_spear(self):

        if self.phase != "day":
            return

        if self.actions_left < 2:

            self.log(
                "製作裝備需要 2 點行動點數。"
            )

            return

        if self.has_spear:

            self.log(
                "你已經擁有石矛。"
            )

            return

        if not self.inventory.spend(
            {
                "wood": 2,
                "stone": 1,
            }
        ):

            self.log(
                "製作石矛需要 2 木材 + 1 石頭。"
            )

            return

        self.has_spear = True

        self.actions_left -= 2

        self.log(
            "成功製作石矛！夜晚攻擊力提升。"
        )

    # --------------------------------------------------------
    # 石斧
    # --------------------------------------------------------

    def craft_axe(self):

        if self.phase != "day":
            return

        if self.actions_left < 2:

            self.log(
                "製作裝備需要 2 點行動點數。"
            )

            return

        if self.has_axe:

            self.log(
                "你已經擁有石斧。"
            )

            return

        if not self.inventory.spend(
            {
                "wood": 1,
                "stone": 2,
            }
        ):

            self.log(
                "製作石斧需要 1 木材 + 2 石頭。"
            )

            return

        self.has_axe = True

        self.actions_left -= 2

        self.log(
            "成功製作石斧！採集木材效率提升。"
        )

    # --------------------------------------------------------
    # 護甲
    # --------------------------------------------------------

    def craft_armor(self):

        if self.phase != "day":
            return

        if self.actions_left < 2:

            self.log(
                "製作裝備需要 2 點行動點數。"
            )

            return

        if not self.inventory.spend(
            {
                "hide": 2,
                "stone": 1,
            }
        ):

            self.log(
                "護甲需要 2 獸皮 + 1 石頭。"
            )

            return

        self.survival.add_armor(
            25
        )

        self.actions_left -= 2

        self.log(
            "成功製作獸皮護甲！護甲 +25。"
        )

    # --------------------------------------------------------
    # 建築
    # --------------------------------------------------------

    def build(self, building_type):

        if self.phase != "day":
            return

        if self.actions_left < 2:

            self.log(
                "建造需要 2 點行動點數。"
            )

            return

        if (
            self.player
            == CAMP_POSITION
        ):

            self.log(
                "營火所在地不能建造其他設施。"
            )

            return

        success = (
            self.buildings.build(
                building_type,
                self.player,
                self.inventory,
            )
        )

        if success:

            self.actions_left -= 2

            if (
                building_type
                == BUILD_WALL
            ):

                name = "木牆"

            else:

                name = "陷阱"

            self.log(
                f"在 {self.player} 建造了{name}。"
            )

        else:

            self.log(
                "無法在這裡建造，可能是資源不足或已有建築。"
            )

    # ========================================================
    # NIGHT
    # ========================================================

    def start_night(self):

        if self.phase != "day":
            return

        # 夜晚自動回營地
        self.player = (
            CAMP_POSITION
        )

        # 每日飢餓
        self.survival.apply_daily_hunger()

        if self.survival.is_dead():

            self.phase = (
                "game_over"
            )

            return

        wolf_count = min(
            2 + self.day - 1,
            6,
        )

        boar_count = 0

        if self.day >= 3:

            boar_count = min(
                1 + self.day // 4,
                2,
            )

        self.enemies = []

        for _ in range(
            wolf_count
        ):

            self.enemies.append(
                {
                    "type": "wolf",
                    "hp": 30,
                    "damage": 10,
                }
            )

        for _ in range(
            boar_count
        ):

            self.enemies.append(
                {
                    "type": "boar",
                    "hp": 55,
                    "damage": 15,
                }
            )

        self.phase = "night"

        self.night_round = 1

        audio.play("wolf")

        self.log(
            "夜幕降臨！"
            f"{wolf_count} 隻狼"
            f"、{boar_count} 隻野豬"
            "正在接近營地。"
        )

    # --------------------------------------------------------
    # 敵人
    # --------------------------------------------------------

    def alive_enemies(self):

        return [
            enemy
            for enemy
            in self.enemies
            if enemy["hp"] > 0
        ]

    def first_enemy(self):

        enemies = (
            self.alive_enemies()
        )

        if not enemies:

            return None

        return enemies[0]

    # --------------------------------------------------------
    # 掉落
    # --------------------------------------------------------

    def give_loot(self, enemy):

        self.inventory.add(
            "hide",
            1,
        )

        if (
            enemy["type"]
            == "boar"
        ):

            self.inventory.add(
                "food",
                1,
            )

        enemy_name = (
            "狼"
            if enemy["type"]
            == "wolf"
            else "野豬"
        )

        self.log(
            f"擊敗{enemy_name}！取得戰利品。"
        )

    # --------------------------------------------------------
    # 玩家攻擊
    # --------------------------------------------------------

    def player_attack(self):

        if self.phase != "night":
            return

        enemy = (
            self.first_enemy()
        )

        if enemy is None:

            self.finish_night()

            return

        damage = (
            20
            if self.has_spear
            else 10
        )

        enemy["hp"] = max(
            0,
            enemy["hp"] - damage,
        )

        enemy_name = (
            "狼"
            if enemy["type"]
            == "wolf"
            else "野豬"
        )

        self.log(
            f"你攻擊{enemy_name}，"
            f"造成 {damage} 點傷害。"
        )

        if enemy["hp"] == 0:

            self.give_loot(
                enemy
            )

        self.enemy_turn()

    # --------------------------------------------------------
    # 夜晚加柴
    # --------------------------------------------------------

    def night_firewood(self):

        if self.phase != "night":
            return

        if self.add_firewood():

            self.enemy_turn()

    # --------------------------------------------------------
    # 找牆
    # --------------------------------------------------------

    def first_wall(self):

        for building in (
            self.buildings
            .buildings
            .values()
        ):

            if (
                building.building_type
                == BUILD_WALL
            ):

                return building

        return None

    # --------------------------------------------------------
    # 陷阱
    # --------------------------------------------------------

    def activate_traps(self):

        for building in list(
            self.buildings
            .buildings
            .values()
        ):

            if (
                building.building_type
                != BUILD_TRAP
            ):

                continue

            if not building.active:

                continue

            enemy = (
                self.first_enemy()
            )

            if enemy is None:

                return

            if self.buildings.trigger_trap(
                building.position
            ):

                enemy["hp"] = max(
                    0,
                    enemy["hp"] - 25,
                )

                enemy_name = (
                    "狼"
                    if enemy["type"]
                    == "wolf"
                    else "野豬"
                )

                self.log(
                    f"陷阱命中{enemy_name}！"
                    "造成 25 點傷害。"
                )

                if enemy["hp"] == 0:

                    self.give_loot(
                        enemy
                    )

    # --------------------------------------------------------
    # 敵人回合
    # --------------------------------------------------------

    def enemy_turn(self):

        if self.phase != "night":
            return

        self.activate_traps()

        for enemy in (
            self.alive_enemies()
        ):

            enemy_name = (
                "狼"
                if enemy["type"]
                == "wolf"
                else "野豬"
            )

            wall = (
                self.first_wall()
            )

            if wall is not None:

                damage = (
                    25
                    if enemy["type"]
                    == "boar"
                    else 10
                )

                position = (
                    wall.position
                )

                self.buildings.damage_building(
                    position,
                    damage,
                )

                if (
                    self.buildings
                    .get_building(
                        position
                    )
                    is None
                ):

                    self.log(
                        f"{enemy_name}摧毀了一面木牆！"
                    )

                else:

                    self.log(
                        f"{enemy_name}正在攻擊木牆。"
                    )

            else:

                damage_taken = (
                    self.survival
                    .take_damage(
                        enemy["damage"]
                    )
                )

                self.log(
                    f"{enemy_name}攻擊你！"
                    f"生命損失 {damage_taken}。"
                )

            if self.survival.is_dead():

                self.phase = (
                    "game_over"
                )

                self.log(
                    "你倒在了荒野之中……"
                )

                return

        # 每輪消耗 1 fuel
        self.campfire.consume(
            1
        )

        if not self.campfire.lit:

            self.log(
                "營火熄滅了！黑暗籠罩營地。"
            )

        # 全部殺死
        if not self.alive_enemies():

            self.finish_night()

            return

        # 第四輪結束
        if (
            self.night_round
            >= MAX_NIGHT_ROUNDS
        ):

            self.log(
                "黎明到來，剩餘敵人逃回森林。"
            )

            self.finish_night()

            return

        self.night_round += 1

    # --------------------------------------------------------
    # PASS
    # --------------------------------------------------------

    def pass_night_turn(self):

        if self.phase == "night":

            self.log(
                "你選擇防守並等待敵人的行動。"
            )

            self.enemy_turn()

    # --------------------------------------------------------
    # 夜晚結束
    # --------------------------------------------------------

    def finish_night(self):

        self.enemies = []

        self.day += 1

        self.actions_left = (
            MAX_ACTIONS
        )

        self.phase = "day"

        self.player = (
            CAMP_POSITION
        )

        self.log(
            f"太陽升起，第 {self.day} 天開始了。"
        )

    # ========================================================
    # INPUT
    # ========================================================

    def handle_key(self, key):

        if key == pygame.K_ESCAPE:

            return False

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if (
            self.phase
            == "game_over"
        ):

            if key == pygame.K_r:

                self.reset()

            return True

        # ----------------------------------------------------
        # DAY
        # ----------------------------------------------------

        if self.phase == "day":

            if key in MOVE_KEYS:

                self.move(
                    MOVE_KEYS[key]
                )

            elif key == pygame.K_g:

                self.gather()

            elif key == pygame.K_c:

                self.eat()

            elif key == pygame.K_f:

                self.add_firewood()

            elif key == pygame.K_1:

                self.craft_spear()

            elif key == pygame.K_2:

                self.craft_axe()

            elif key == pygame.K_3:

                self.craft_armor()

            elif key == pygame.K_b:

                self.build(
                    BUILD_WALL
                )

            elif key == pygame.K_t:

                self.build(
                    BUILD_TRAP
                )

            elif key == pygame.K_n:

                self.start_night()

        # ----------------------------------------------------
        # NIGHT
        # ----------------------------------------------------

        elif self.phase == "night":

            if key == pygame.K_a:

                self.player_attack()

            elif key == pygame.K_f:

                self.night_firewood()

            elif key == pygame.K_SPACE:

                self.pass_night_turn()

        return True


# ============================================================
# MAIN
# ============================================================

def main():

    pygame.init()

    pygame.display.set_caption(
        "石器時代：荒野求生"
    )

    screen = (
        pygame.display.set_mode(
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            )
        )
    )

    clock = pygame.time.Clock()

    fonts = create_fonts()

    game = Game()

    # menu / tutorial / game
    view = "menu"

    tutorial_page = 0

    running = True

    while running:

        for event in (
            pygame.event.get()
        ):

            if (
                event.type
                == pygame.QUIT
            ):

                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                 audio.play("click1")

            elif (
                event.type
                == pygame.KEYDOWN
            ):

                # ============================================
                # MENU
                # ============================================

                if view == "menu":

                    if (
                        event.key
                        == pygame.K_RETURN
                    ):

                        view = "tutorial"

                        tutorial_page = 0

                    elif (
                        event.key
                        == pygame.K_ESCAPE
                    ):

                        running = False

                # ============================================
                # TUTORIAL
                # ============================================

                elif view == "tutorial":

                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                        pygame.K_RIGHT,
                    ):

                        tutorial_page += 1

                        if (
                            tutorial_page
                            >= TUTORIAL_PAGE_COUNT
                        ):

                            tutorial_page = 0

                            view = "game"

                    elif event.key in (
                        pygame.K_BACKSPACE,
                        pygame.K_LEFT,
                    ):

                        tutorial_page = max(
                            0,
                            tutorial_page - 1,
                        )

                    elif event.key in (
                        pygame.K_s,
                        pygame.K_ESCAPE,
                    ):

                        tutorial_page = 0

                        view = "game"

                # ============================================
                # GAME
                # ============================================

                elif view == "game":

                    if (
                        event.key
                        == pygame.K_h
                    ):

                        tutorial_page = 0

                        view = "tutorial"

                    else:

                        running = (
                            game.handle_key(
                                event.key
                            )
                        )

        # ====================================================
        # DRAW
        # ====================================================

        if view == "menu":

            draw_menu(
                screen,
                fonts,
            )

        elif view == "tutorial":

            # 教學底下顯示遊戲地圖
            draw_game(
                screen,
                fonts,
                game,
                tutorial_active=True,
                tutorial_page=tutorial_page,
                max_night_rounds=MAX_NIGHT_ROUNDS,
            )

        else:

            draw_game(
                screen,
                fonts,
                game,
                tutorial_active=False,
                tutorial_page=0,
                max_night_rounds=MAX_NIGHT_ROUNDS,
            )

        pygame.display.flip()

        clock.tick(
            FPS
        )

    pygame.quit()


if __name__ == "__main__":
    main()


    
    # ... 下面接著原本的移動或點擊邏輯