import pytest
from hex_map import HexMap
from resource_system import populate_resources, gather_resource, populate_special_tiles, trigger_special_tile
from constants import CAMP_POSITION, TERRAIN_WATER, SPECIAL_REWARD

def test_resources():
    hm = HexMap(seed=42)
    populate_resources(hm, seed=42)
    populate_special_tiles(hm, seed=42)
    
    camp_tile = hm.get_tile(*CAMP_POSITION)
    assert camp_tile.resource is None
    
    # 測試 gather 例外
    with pytest.raises(ValueError):
        gather_resource(camp_tile, -1)
        
    res_type, amt = gather_resource(camp_tile, 1)
    assert res_type is None
    assert amt == 0