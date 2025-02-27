from abc import ABC, abstractmethod
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager

class InterfaceTimeDependent(ABC):
    @property
    @abstractmethod
    def time_manager(self) -> InterfaceTimeManager:
        pass

