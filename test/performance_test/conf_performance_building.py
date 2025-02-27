from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
import pytest
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock

def create_starttimes(starttime: datetime, horizon_steps: int):
    starttimes = []
    for i in range(horizon_steps):
        starttimes.append(starttime + timedelta(minutes=i*15))
    return starttimes

def create_future_map(starttime: datetime, horizon_steps: int):
    future_map = {}
    starttimes = create_starttimes(starttime, horizon_steps)
    for time in starttimes:
        power_trajectory =PowerTrajectory()
        future_map[time] = power_trajectory
        for i in range(horizon_steps):
            power_trajectory.add_power_value(PowerType(0, PowerTypeUnit.KW), time + timedelta(minutes=i*15))
    return future_map




# @pytest.fixture
# def conv_building(time_manager):
#     building = Building(name = "test",time_manager=time_manager, horizon_steps=96)
#     building.update_horizon()
#     building.power_trajectory = PowerTrajectory()
#     for i in range(96):
#         building.power_trajectory.add_power_value(PowerType(0, PowerTypeUnit.KW), time_manager.get_start_time() + timedelta(minutes=i*15))    
#     return building


