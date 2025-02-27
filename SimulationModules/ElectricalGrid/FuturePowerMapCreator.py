from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager



class InterfaceFuturePowerMap(ABC):
    future_power_map: dict = {}

    @abstractmethod
    def create_from_trajectory(self, power_trajectory):
        pass

    @abstractmethod
    def get_future_power_for_time(self) -> PowerTrajectory:
        pass

    @abstractmethod
    def get_power_for_time(self, time: datetime) -> PowerType:
        pass

class FuturePowerMap(InterfaceFuturePowerMap):
        
    def __init__(self, 
                 time_manager, 
                 horizon_steps):
        self.time_manager: InterfaceTimeManager = time_manager
        self.horizon_steps: int = horizon_steps
        self.future_power_map = {}
    
    def create_from_trajectory(self, power_trajectory: PowerTrajectory):
        time = self.time_manager.get_start_time()
        while time <= self.time_manager.get_stop_time():
            temp_power_trajectory = PowerTrajectory()
            self.future_power_map[time]=temp_power_trajectory#
            for i in range(self.horizon_steps):
                prediction_time = time + self.time_manager.get_step_time()*i
                temp_power_trajectory.add_power_value(power_trajectory.get_power_at_time(prediction_time), prediction_time)
            time += self.time_manager.get_step_time()

    def get_future_power_for_time(self) -> PowerTrajectory:
        return self.future_power_map[self.time_manager.get_current_time()]

    def get_power_for_time(self) -> PowerType:
        power:PowerType = self.future_power_map[self.time_manager.get_current_time()].power[0]
        return power
