from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable


class InterfaceEvUserData(ABC):
    ev_user_data_parameters: Callable[[], timedelta]
    max_parking_time: timedelta
    min_parking_time: timedelta
    arrival_datetime: datetime

    @abstractmethod
    def get_arrival_datetime(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_stay_duration(self):
        raise NotImplementedError
    
    @abstractmethod
    def update_time(self,time: datetime):
        raise NotImplementedError
