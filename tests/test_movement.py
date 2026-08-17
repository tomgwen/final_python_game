from hex_map import HexMap
from movement import can_move, move_player
from constants import CAMP_POSITION, TERRAIN_WATER

def test_movement():
    hm = HexMap(seed=42)
    current = CAMP_POSITION
    # 找一個合法的鄰居
    neighbors = hm.get_neighbors(*current)
    target = neighbors[0]
    
    # 強制把目標設為草地以確保可走
    hm.get_tile(*target).terrain = "grass"
    
    assert can_move(hm, current, target)
    new_pos, success = move_player(hm, current, target)
    assert success
    assert new_pos == target
    
    # 測試跨格不可走
    far_target = (0, 0)
    if far_target not in neighbors:
        assert not can_move(hm, current, far_target)