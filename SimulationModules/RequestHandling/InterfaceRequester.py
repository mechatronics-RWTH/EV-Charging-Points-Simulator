from abc import ABC, abstractmethod
from SimulationModules.RequestHandling.Request import Request


class InterfaceRequester(ABC):
    @property
    @abstractmethod
    def charging_request(self) -> Request:
        pass