from abc import ABC, abstractmethod
from datetime import datetime, timedelta
#from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField



#TODO: The Gini_State moving should maybe be related to this one
class InterfaceMobileChargingStation(ABC):
    travel_time: timedelta
    time_step_remainder: timedelta
    status: str
    # _current_field: InterfaceField
    # target_field: InterfaceField

    @abstractmethod
    def update_remaining_travel_time(self, time: timedelta):
        raise NotImplementedError
    
    @abstractmethod
    def get_remaining_travel_time(self):
        raise NotImplementedError
    
    @abstractmethod
    def is_traveling(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_time_step_remainder(self):
        raise NotImplementedError

    @abstractmethod
    def set_target_field(self, target_field):
        raise NotImplementedError
    
    @abstractmethod
    def get_current_field(self):
        raise NotImplementedError


    



