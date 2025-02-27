from abc import ABC, abstractmethod
from datetime import datetime
from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.datatypes.PowerType import PowerType
from typing import List
import math 

class InterfacePowerTransferTrajectory(ABC):
    power_trajectory: List[PowerType]
    energy_trajectory: List[EnergyType]
    requested_energy_trajectory: List[EnergyType] = []
    time_trajectory: List[datetime]

    @abstractmethod
    def add_entry(self, 
                  power: PowerType, 
                  energy: EnergyType,
                  requested_energy: EnergyType,
                  time: datetime):
        pass

    @abstractmethod
    def get_energy_trajectory(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_power_trajectory(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_time_trajectory(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_last_energy_value(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_start_energy_request(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_end_energy_request(self):
        raise NotImplementedError


class PowerTransferTrajectory(InterfacePowerTransferTrajectory):

    def __init__(self):

        self.power_trajectory: List[PowerType] = []
        self.energy_trajectory: List[EnergyType] = []
        self.requested_energy_trajectory: List[EnergyType] = []
        self.time_trajectory: List[datetime] = []

    def add_entry(self, 
                  power: PowerType, 
                  energy: EnergyType,
                  requested_energy: EnergyType,
                  time: datetime):
        if not isinstance(power, PowerType):
            raise ValueError("Power must be of type PowerType")
        if not isinstance(energy, EnergyType):
            raise ValueError("Energy must be of type EnergyType")
        if not isinstance(requested_energy, EnergyType):
            raise ValueError(f"Requested energy must be of type EnergyType, not {type(requested_energy)}")
        if not isinstance(time, datetime):
            raise ValueError("Time must be of type datetime")
        self.power_trajectory.append(power) 
        self.energy_trajectory.append(energy)
        self.requested_energy_trajectory.append(requested_energy)
        self.time_trajectory.append(time)

    def get_energy_trajectory(self):
        return self.energy_trajectory
    
    def get_power_trajectory(self):
        return self.power_trajectory
    
    def get_time_trajectory(self):
        return self.time_trajectory
    
    def get_last_energy_value(self):
        if len(self.energy_trajectory) == 0:
            return EnergyType(0)
        return self.energy_trajectory[-1]
    

    def get_start_energy_request(self):
        return self.requested_energy_trajectory[0]
    

    def get_end_energy_request(self):
        return self.requested_energy_trajectory[-1]
    
    def get_charged_energy(self):
        #self.check_charged_energy()
        return sum(self.energy_trajectory)
    
    def check_charged_energy(self):
        if len(self) > 1:
            energy_charged_trajectory = sum(self.energy_trajectory)
            energy_charged_requested = self.requested_energy_trajectory[0] - self.requested_energy_trajectory[-1]
            requested_energy_in_kwh = [request.get_in_kwh() for request in self.requested_energy_trajectory]
            assert math.isclose(energy_charged_trajectory.get_in_kwh().value, energy_charged_requested.get_in_kwh().value, rel_tol=1e-3), (
            f"Sum of energy charged trajectory {self.energy_trajectory} "
            f"does not match difference of requested energy {requested_energy_in_kwh}"
            f" {energy_charged_trajectory.get_in_kwh()} != {energy_charged_requested.get_in_kwh()}")

    
    def __len__(self):
        return len(self.time_trajectory)
    
    