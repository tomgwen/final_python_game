from hex_map import HexMap
from constants import CAMP_POSITION, TERRAIN_GRASS

def test_hex_map():
    hm = HexMap(seed=42)
    tiles = hm.get_all_tiles()
    assert len(tiles) == 88 # 11x8
    
    camp = hm.get_tile(*CAMP_POSITION)
    assert camp is not None
    assert camp.terrain == TERRAIN_GRASS
    assert camp.resource is None
    
    assert hm.is_valid(0, 0)
    assert not hm.is_valid(-1, -1)
    
    neighbors = hm.get_neighbors(*CAMP_POSITION)
    assert len(neighbors) == 6