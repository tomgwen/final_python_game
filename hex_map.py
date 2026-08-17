from dataclasses import dataclass
import random
from constants import (
    MAP_COLS, MAP_ROWS, CAMP_POSITION, 
    TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_ROCK, TERRAIN_WATER
)

HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
]

@dataclass
class HexTile:
    q: int
    r: int
    terrain: str
    resource: str | None = None
    resource_amount: int = 0
    discovered: bool = False
    special: str | None = None
    special_triggered: bool = False

class HexMap:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.tiles: dict[tuple[int, int], HexTile] = {}
        self._generate_map()

    def _generate_map(self) -> None:
        # 控制地形比例: Grass 最高, Forest 次之, Rock/Water 少量
        terrain_pool = (
            [TERRAIN_GRASS] * 12 + 
            [TERRAIN_FOREST] * 6 + 
            [TERRAIN_ROCK] * 2 + 
            [TERRAIN_WATER] * 2
        )
        
        for q in range(MAP_COLS):
            for r in range(MAP_ROWS):
                if (q, r) == CAMP_POSITION:
                    terrain = TERRAIN_GRASS
                else:
                    terrain = self.rng.choice(terrain_pool)
                
                self.tiles[(q, r)] = HexTile(q=q, r=r, terrain=terrain)

    def get_tile(self, q: int, r: int) -> HexTile | None:
        return self.tiles.get((q, r))

    def is_valid(self, q: int, r: int) -> bool:
        return 0 <= q < MAP_COLS and 0 <= r < MAP_ROWS

    def get_neighbors(self, q: int, r: int) -> list[tuple[int, int]]:
        neighbors = []
        for dq, dr in HEX_DIRECTIONS:
            nq, nr = q + dq, r + dr
            if self.is_valid(nq, nr):
                neighbors.append((nq, nr))
        return neighbors

    def get_all_tiles(self) -> list[HexTile]:
        # 確保順序：先 q 再 r，讓 pytest 結果穩定
        return [self.tiles[(q, r)] for q in range(MAP_COLS) for r in range(MAP_ROWS)]