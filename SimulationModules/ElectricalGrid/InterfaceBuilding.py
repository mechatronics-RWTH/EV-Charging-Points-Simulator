from abc import ABC, abstractmethod
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.ElectricalGrid.FuturePowerMapCreator import InterfaceFuturePowerMap

class InterfaceBuilding(ABC):

    
    @abstractmethod       
    def get_power_contribution(self) -> PowerType:
        raise NotImplementedError
    
    @abstractmethod
    def get_power_future(self) -> PowerTrajectory:
        raise NotImplementedError