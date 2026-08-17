from hex_map import HexMap
from fog import initialize_fog, reveal_around
from constants import CAMP_POSITION

def test_fog():
    hm = HexMap(seed=42)
    initialize_fog(hm, CAMP_POSITION)
    
    camp_tile = hm.get_tile(*CAMP_POSITION)
    assert camp_tile.discovered is True
    
    neighbors = hm.get_neighbors(*CAMP_POSITION)
    for n in neighbors:
        assert hm.get_tile(*n).discovered is True