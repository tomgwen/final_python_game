import pytest
from day_system import DaySystem
from constants import STATE_DAY, STATE_NIGHT

def test_day_system():
    ds = DaySystem()
    assert ds.day == 1
    assert ds.actions_left == 6
    assert ds.can_act()
    
    assert ds.spend_action(2)
    assert ds.actions_left == 4
    
    assert not ds.spend_action(5) # 點數不足
    
    with pytest.raises(ValueError):
        ds.spend_action(-1)
        
    ds.end_day()
    assert ds.phase == STATE_NIGHT
    assert ds.actions_left == 0
    
    ds.start_new_day()
    assert ds.day == 2
    assert ds.phase == STATE_DAY
    assert ds.actions_left == 6