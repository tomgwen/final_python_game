import random
from hex_map import HexMap, HexTile
from constants import (
    CAMP_POSITION, TERRAIN_WATER, TERRAIN_FOREST, TERRAIN_ROCK, TERRAIN_GRASS,
    RESOURCE_WOOD, RESOURCE_STONE, RESOURCE_FOOD, SPECIAL_REWARD, SPECIAL_TRAP
)

def populate_resources(hex_map: HexMap, seed: int | None = None) -> None:
    rng = random.Random(seed)
    
    for tile in hex_map.get_all_tiles():
        if (tile.q, tile.r) == CAMP_POSITION:
            continue
        if tile.terrain == TERRAIN_WATER:
            continue
            
        if tile.terrain == TERRAIN_FOREST:
            if rng.random() < 0.7:
                tile.resource = RESOURCE_WOOD
        elif tile.terrain == TERRAIN_ROCK:
            if rng.random() < 0.7:
                tile.resource = RESOURCE_STONE
        elif tile.terrain == TERRAIN_GRASS:
            if rng.random() < 0.3:
                tile.resource = RESOURCE_FOOD
                
        if tile.resource is not None:
            tile.resource_amount = rng.randint(1, 3)

def gather_resource(tile: HexTile, gather_amount: int = 1) -> tuple[str | None, int]:
    if gather_amount < 0:
        raise ValueError("gather_amount cannot be negative")
        
    if gather_amount == 0 or tile.resource is None or tile.resource_amount <= 0:
        return None, 0
        
    actual_amount = min(gather_amount, tile.resource_amount)
    resource_type = tile.resource
    
    tile.resource_amount -= actual_amount
    if tile.resource_amount == 0:
        tile.resource = None
        
    return resource_type, actual_amount

def populate_special_tiles(hex_map: HexMap, seed: int | None = None) -> None:
    rng = random.Random(seed)
    
    valid_tiles = [
        t for t in hex_map.get_all_tiles()
        if (t.q, t.r) != CAMP_POSITION and t.terrain != TERRAIN_WATER
    ]
    
    empty_tiles = [t for t in valid_tiles if t.resource is None]
    resource_tiles = [t for t in valid_tiles if t.resource is not None]
    
    # 優先選擇沒有資源的格，避免重疊
    pool = empty_tiles + resource_tiles
    
    if len(pool) < 6:
        selected_tiles = pool
    else:
        selected_tiles = rng.sample(pool, 6)
        
    for i, tile in enumerate(selected_tiles):
        if i < 3:
            tile.special = SPECIAL_REWARD
        elif i < 6:
            tile.special = SPECIAL_TRAP

def trigger_special_tile(tile: HexTile) -> str | None:
    if tile.special is None:
        return None
        
    if tile.special_triggered:
        return None
        
    tile.special_triggered = True
    
    if tile.special == SPECIAL_REWARD:
        return SPECIAL_REWARD
    elif tile.special == SPECIAL_TRAP:
        return SPECIAL_TRAP
        
    return None