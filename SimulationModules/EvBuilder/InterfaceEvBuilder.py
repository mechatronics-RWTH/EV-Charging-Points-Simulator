from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class InterfaceEvBuilder(ABC):
    
    @abstractmethod
    def build_evs(self, ):
        raise NotImplementedError