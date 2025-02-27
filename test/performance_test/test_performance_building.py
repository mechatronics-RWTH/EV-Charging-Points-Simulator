from SimulationModules.ElectricalGrid.Building import Building
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricalGrid.FuturePowerMapCreator import InterfaceFuturePowerMap, FuturePowerMap

def create_starttimes(starttime: datetime, horizon_steps: int):
    starttimes = []
    for i in range(horizon_steps):
        starttimes.append(starttime + timedelta(minutes=i*15))
    return starttimes

def create_power_trajectory(starttime: datetime, horizon_steps: int):
    future_map = {}
    starttimes = create_starttimes(starttime, horizon_steps*2)
    power_trajectory =PowerTrajectory()
    for time in starttimes:
        power_trajectory.add_power_value(PowerType(0, PowerTypeUnit.KW), time)
    return power_trajectory

@pytest.fixture
def time_manager():
    mock_time_manager = MagicMock(spec= InterfaceTimeManager)
    mock_time_manager.get_start_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    mock_time_manager.get_stop_time.return_value = datetime(2021, 1, 2, 0, 0, 0)
    mock_time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    mock_time_manager.get_step_time.return_value = timedelta(minutes=15)
    return mock_time_manager


@pytest.fixture
def building(time_manager):
    horizon_steps = 96
    future_power_map = FuturePowerMap(time_manager, horizon_steps)
    power_traj = create_power_trajectory(datetime(2021, 1, 1, 0, 0, 0), horizon_steps)
    future_power_map.create_from_trajectory(power_traj)
    mock_building = Building(name = "test", future_power_map= future_power_map)
    #mock_building.create_future_power_map()
    return mock_building


class TestPerformanceBuilding:

    @pytest.mark.performance
    def test_performance_building_get_power_future(self,benchmark,
                                                   building: Building):
        #building.future_power_map = create_future_map(datetime(2021, 1, 1, 0, 0, 0), 96)
        benchmark.group = "get_power_future"
        benchmark(building.get_power_future)
        stats= benchmark.stats

    # @pytest.mark.performance
    # def test_performance_building_conventional_get_power_future(self,benchmark,
    #                                                conv_building: Building):
    #     conv_building.create_future_power_map()
    #     benchmark.group = "get_power_future"
    #     benchmark(conv_building.get_power_future)
    #     stats= benchmark.stats




        
