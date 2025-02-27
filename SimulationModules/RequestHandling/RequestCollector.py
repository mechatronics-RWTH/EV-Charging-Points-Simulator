from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from SimulationModules.RequestHandling.Request import Request
from typing import List
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class InterfaceRequestCollector(ABC):
    active_requests: List[Request] = []
    request_archive: List[Request] = []

    @abstractmethod
    def add_request(self, request: Request):
        pass

    @abstractmethod
    def get_requests(self) -> List[Request]:
        pass

    @abstractmethod
    def remove_request(self, request: Request):
        pass


class RequestCollector(InterfaceRequestCollector):
    """
    This class should keep track of all active requests in the simulation
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        #if not hasattr(self, 'active_requests'):
        self.active_requests: List[Request] = []
        #if not hasattr(self, 'request_archive'):
        self.request_archive: List[Request] = []

    def add_request(self, request: Request):
        if request in self.active_requests:
            raise ValueError("Request already exists in active requests")
        if not isinstance(request, Request):
            raise TypeError("Request is not of type Request")
        self.active_requests.append(request)

    def get_requests(self):
        return self.active_requests

    def remove_request(self, request: Request):
        if request not in self.active_requests:
            raise ValueError("Request does not exist in active requests")
        self.active_requests.remove(request)
        self.request_archive.append(request)

    def clear_requests(self):
        self.active_requests: List[Request] = []
        self.request_archive: List[Request] = []
