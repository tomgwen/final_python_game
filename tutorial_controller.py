"""State-observing first-day tutorial controller."""

from __future__ import annotations


MESSAGES = (
    "先認識生命、飢餓與晝夜資訊。按 Enter 或 Space 開始。",
    "拖曳阿強到相鄰格，完成第一次移動。",
    "前往森林並採集木材。",
    "前往草地並採集食物。",
    "前往岩地並採集石頭。",
    "吃一份食物，讓飢餓值下降。",
    "製作石斧或石鎬。",
    "靠近任一營火，右鍵營火補充木材。",
    "點燃營火周圍 4 格是夜間安全區。按 Enter 或 Space 繼續。",
    "準備完成，度過白天並進入夜晚。",
    "撐過第一晚，迎接第 2 天。",
)


class TutorialController:
    """Observe Game state and advance without modifying gameplay state."""

    def __init__(self, game=None) -> None:
        self.active = True
        self.step = 0
        self.completed = False
        self._initialized = False
        if game is not None:
            self._capture_initial(game)

    def _capture_initial(self, game) -> None:
        self.initial_player_position = game.player
        self.starting_wood = game.inventory.get("wood")
        self.starting_food = game.inventory.get("food")
        self.starting_stone = game.inventory.get("stone")
        self.hunger_at_step = game.survival.hunger
        self.starting_fuel = {position: fire.fuel for position, fire in game.campfires.items()}
        self._initialized = True

    def current_message(self) -> str | None:
        if not self.active or self.completed:
            return None
        return MESSAGES[self.step]

    def acknowledge(self, game) -> None:
        if not self._initialized:
            self._capture_initial(game)
        if self.step in (0, 8):
            self.step += 1
            if self.step == 5:
                self.hunger_at_step = game.survival.hunger

    def update(self, game) -> None:
        if not self.active or self.completed:
            return
        if not self._initialized:
            self._capture_initial(game)

        advanced = False
        if self.step == 1:
            advanced = game.player != self.initial_player_position
        elif self.step == 2:
            advanced = game.inventory.get("wood") > self.starting_wood
        elif self.step == 3:
            advanced = game.inventory.get("food") > self.starting_food
        elif self.step == 4:
            advanced = game.inventory.get("stone") > self.starting_stone
        elif self.step == 5:
            advanced = game.survival.hunger < self.hunger_at_step
        elif self.step == 6:
            advanced = game.has_axe or game.has_pickaxe
        elif self.step == 7:
            advanced = any(
                position in self.starting_fuel
                and fire.fuel > self.starting_fuel[position]
                for position, fire in game.campfires.items()
            )
        elif self.step == 9:
            advanced = game.phase == "night"
        elif self.step == 10 and game.day >= 2 and game.phase == "day":
            self.complete()
            return

        if advanced:
            self.step += 1
            if self.step == 5:
                self.hunger_at_step = game.survival.hunger

    def complete(self) -> None:
        self.completed = True
        self.active = False
