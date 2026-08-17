from constants import MAX_DAY_ACTIONS, STATE_DAY, STATE_NIGHT

class DaySystem:
    def __init__(self):
        self.day: int = 1
        self.max_actions: int = MAX_DAY_ACTIONS
        self.actions_left: int = MAX_DAY_ACTIONS
        self.phase: str = STATE_DAY

    def can_act(self) -> bool:
        return self.phase == STATE_DAY and self.actions_left > 0

    def spend_action(self, cost: int = 1) -> bool:
        if cost < 0:
            raise ValueError("cost cannot be negative")
        if cost == 0:
            return True
        if self.phase != STATE_DAY:
            return False
        if self.actions_left < cost:
            return False
            
        self.actions_left -= cost
        return True

    def end_day(self) -> None:
        self.phase = STATE_NIGHT
        self.actions_left = 0

    def start_new_day(self) -> None:
        self.day += 1
        self.phase = STATE_DAY
        self.actions_left = self.max_actions