from dataclasses import dataclass
import random
from constants import RESOURCE_ARROW

@dataclass
class TreasureChest:
    position: tuple[int, int]
    contents: dict[str, int]
    opened: bool = False


def generate_chest_contents(rng: random.Random | None = None) -> dict[str, int]:
    """Generate a large random resource reward for one treasure chest."""
    rng = rng or random.Random()

    possible_rewards = {
        "food": (6, 12),
        "wood": (6, 12),
        "stone": (4, 10),
        "hide": (2, 6),
        RESOURCE_ARROW: (3, 8),
    }

    reward_count = rng.randint(2, 4)
    selected = rng.sample(list(possible_rewards.keys()), reward_count)

    contents: dict[str, int] = {}

    for resource in selected:
        minimum, maximum = possible_rewards[resource]
        contents[resource] = rng.randint(minimum, maximum)

    return contents