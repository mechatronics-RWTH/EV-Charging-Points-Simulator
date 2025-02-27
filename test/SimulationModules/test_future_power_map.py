from SimulationModules.ElectricalGrid.FuturePowerMapCreator import FuturePowerMap, InterfaceFuturePowerMap
from unittest.mock import Mock
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
#from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from datetime import datetime, timedelta
import pytest

@pytest.fixture
def mock_time_manager():
    mock_time_manager= Mock(spec=InterfaceTimeManager)
    mock_time_manager.get_start_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    mock_time_manager.get_stop_time.return_value = datetime(2021, 1, 1, 10, 0, 0)
    mock_time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    mock_time_manager.get_step_time.return_value = timedelta(minutes=30)
    return mock_time_manager

class TestFuturePowerMap:

    def test_init(self,
                  mock_time_manager):
        future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=20)
        assert isinstance(future_power_map, InterfaceFuturePowerMap)

    def test_create_from_trajectory(self,
                                    mock_time_manager):
        future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=20)
        power_trajectory = Mock()
        power_trajectory.get_power_at_time.return_value = PowerType(10, PowerTypeUnit.KW)
        future_power_map.create_from_trajectory(power_trajectory)
        expected_len = (mock_time_manager.get_stop_time() - mock_time_manager.get_start_time())/mock_time_manager.get_step_time() + 1
        assert len(future_power_map.future_power_map) ==expected_len

    def test_create_from_trajectory_assert_element(self,
                                    mock_time_manager):
        future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=20)
        power_trajectory = Mock()
        power_trajectory.get_power_at_time.return_value = PowerType(10, PowerTypeUnit.KW)
        future_power_map.create_from_trajectory(power_trajectory)
        expected_len = (mock_time_manager.get_stop_time() - mock_time_manager.get_start_time())/mock_time_manager.get_step_time() + 1
        assert len(future_power_map.future_power_map[mock_time_manager.get_start_time()]) ==20

    def test_get_future_power_for_time(self,
                                        mock_time_manager):
          power_val = PowerType(10, PowerTypeUnit.KW)
          future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=20)
          power_trajectory = Mock()
          power_trajectory.get_power_at_time.return_value = power_val
          future_power_map.create_from_trajectory(power_trajectory)
          future_power = future_power_map.get_future_power_for_time()
          assert future_power.power[0] == power_val 

    def test_get_future_power_for_time_len(self,
                                        mock_time_manager):
          power_val = PowerType(10, PowerTypeUnit.KW)
          horizon_steps = 20
          future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=horizon_steps)
          power_trajectory = Mock()
          power_trajectory.get_power_at_time.return_value = power_val
          future_power_map.create_from_trajectory(power_trajectory)
          future_power = future_power_map.get_future_power_for_time()
          assert len(future_power) == horizon_steps

    def test_get_power_for_time(self,
                                mock_time_manager):
        future_power_map = FuturePowerMap(time_manager=mock_time_manager, horizon_steps=20)
        power_trajectory = Mock()
        power_trajectory.get_power_at_time.return_value = PowerType(10, PowerTypeUnit.KW)
        future_power_map.create_from_trajectory(power_trajectory)
        print(future_power_map.future_power_map)
        power = future_power_map.get_power_for_time()
        assert power == PowerType(10, PowerTypeUnit.KW)

    



