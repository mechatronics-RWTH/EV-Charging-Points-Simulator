from abc import ABC, abstractmethod
from SimulationModules.datatypes.PowerType import PowerType

class InterfaceChargingSessionParticipant():
    @abstractmethod
    def set_actual_charging_power(self, power: PowerType):
        raise NotImplementedError

    @abstractmethod
    def is_ready_start_session(self) -> bool:
        raise NotImplementedError