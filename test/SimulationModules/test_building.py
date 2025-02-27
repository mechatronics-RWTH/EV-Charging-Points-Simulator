from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory,TimeOutOfRangeErrorHigh
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock
import pytest

def side_effect_function(time):
    if time > datetime(2021, 1, 1, 2, 0, 0):
        raise TimeOutOfRangeErrorHigh("TimeOutOfRangeErrorHigh")
    else:
        return PowerType(400, PowerTypeUnit.KW)

#mock_time_manager = MagicMock(spec=InterfaceTimeManager)

mock_power_trajectory = MagicMock(spec=PowerTrajectory)

@pytest.fixture
def building():
    building = Building(name = "test_building", future_power_map= MagicMock())
    building.power_trajectory = mock_power_trajectory
    return building

class TestBuilding:

    def test_init(self):
        building = Building(name = "test_building", future_power_map= MagicMock())
        assert building.name == "test_building"
    
    def test_get_power_contribution(self,building: Building):
        building.future_power_map= MagicMock()
        
        building.get_power_contribution()
        building.future_power_map.get_power_for_time.assert_called_once()

    def test_get_power_contribution_assert_power(self,building: Building):
        building.future_power_map= MagicMock()
        building.future_power_map.get_power_for_time.return_value = PowerType(100, PowerTypeUnit.KW)
        assert building.get_power_contribution() == PowerType(-100, PowerTypeUnit.KW)

    @pytest.mark.skip(reason="Not relevant with new implementation, keeping it, if implementation will be made flexible in future")
    def test_update_horizon(self,building: Building):
        building.horizon_steps = 20
        building.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
        building.time_manager.get_step_time.return_value = timedelta(hours=1)
        building.update_horizon()
        assert len(building.horizon) == 20

    @pytest.mark.skip(reason="Not relevant with new implementation, keeping it, if implementation will be made flexible in future")
    def test_update_horizon_assert(self,building: Building):
        building.horizon_steps = 20
        building.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
        building.time_manager.get_step_time.return_value = timedelta(hours=1)
        building.update_horizon()
        assert building.horizon[0] == datetime(2021, 1, 1, 0, 0, 0)

    @pytest.mark.skip(reason="Not relevant with new implementation, keeping it, if implementation will be made flexible in future")
    def test_update_horizon_assert_last(self,building: Building):
        building.horizon_steps = 20
        building.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
        building.time_manager.get_step_time.return_value = timedelta(hours=1)
        building.update_horizon()
        assert building.horizon[-1] == datetime(2021, 1, 1, 19, 0, 0)


    def test_get_power_future(self,building: Building):
        time_values = [datetime(2021, 1, 1, 0, 0, 0), 
                            datetime(2021, 1, 1, 1, 0, 0),
                            datetime(2021, 1, 1, 2, 0, 0),
                            datetime(2021, 1, 1, 3, 0, 0)]

        
        power_values = [PowerType(100, PowerTypeUnit.KW),
                        PowerType(200, PowerTypeUnit.KW),
                        PowerType(300, PowerTypeUnit.KW),
                        PowerType(400, PowerTypeUnit.KW)]

        power_traj = PowerTrajectory()
        for power_val,time_val in zip(power_values,time_values):
            power_traj.add_power_value(power=power_val,time=time_val)

        building.future_power_map.get_future_power_for_time.return_value = power_traj
        
        assert building.get_power_future() == power_traj


        