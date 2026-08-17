from hex_map import HexMap
from constants import TERRAIN_WATER

def can_move(
    hex_map: HexMap,
    current_position: tuple[int, int],
    target_position: tuple[int, int]
) -> bool:
    if not hex_map.is_valid(target_position[0], target_position[1]):
        return False
        
    if target_position not in hex_map.get_neighbors(current_position[0], current_position[1]):
        return False
        
    tile = hex_map.get_tile(target_position[0], target_position[1])
    if tile is not None and tile.terrain == TERRAIN_WATER:
        return False
        
    return True

def move_player(
    hex_map: HexMap,
    current_position: tuple[int, int],
    target_position: tuple[int, int]
) -> tuple[tuple[int, int], bool]:
    if can_move(hex_map, current_position, target_position):
        return target_position, True
    return current_position, False