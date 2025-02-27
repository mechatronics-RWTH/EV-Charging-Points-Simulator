from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from datetime import datetime, timedelta
from unittest.mock import Mock
import pytest

# @pytest.fixture
# def mock_time_manager():
#     return Mock(spec=InterfaceTimeManager)

@pytest.fixture
def photovoltaic_array():
    return PhotovoltaicArray(name="test",future_power_map=None)

class TestPhotovoltaicArray:

    def test_init(self,
                  ):
        photovoltaic_array = PhotovoltaicArray(name="test", future_power_map=None)
        assert photovoltaic_array is not None

    @pytest.mark.skip(reason="Not relevant with new implementation, keeping it, if implementation will be made flexible in future")
    def test_update_horizon(self,
                            photovoltaic_array: PhotovoltaicArray):
        photovoltaic_array.horizon_steps = 20
        photovoltaic_array.time_manager.get_step_time.return_value = timedelta(minutes=30)
        photovoltaic_array.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
        photovoltaic_array.update_horizon()
        assert len(photovoltaic_array.horizon) == 20

    @pytest.mark.skip(reason="Not relevant with new implementation, keeping it, if implementation will be made flexible in future")
    def test_update_horizon_start_time_end_time(self,
                            photovoltaic_array: PhotovoltaicArray):
        photovoltaic_array.horizon_steps = 20
        photovoltaic_array.time_manager.get_step_time.return_value = timedelta(minutes=30)
        photovoltaic_array.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
        photovoltaic_array.update_horizon()
        assert photovoltaic_array.horizon[0] == datetime(2021, 1, 1, 0, 0, 0)
        assert photovoltaic_array.horizon[-1] == datetime(2021, 1, 1, 9, 30, 0)

    def test_get_power_contribution(self,
                                    photovoltaic_array: PhotovoltaicArray):
        photovoltaic_array.future_power_map = Mock()
        photovoltaic_array.future_power_map.get_power_for_time.return_value = PowerType(10, PowerTypeUnit.KW)
        assert photovoltaic_array.get_power_contribution() == PowerType(10, PowerTypeUnit.KW)

    def test_get_power_future(self, 
                              photovoltaic_array: PhotovoltaicArray):
        photovoltaic_array.future_power_map = Mock()
        power_trajectory = Mock()
        photovoltaic_array.future_power_map.get_future_power_for_time.return_value = power_trajectory
        power_future = photovoltaic_array.get_power_future()
        assert power_future == power_trajectory
                                         

    
    