from datetime import datetime, timedelta
from SimulationModules.EvBuilder.InterfaceEvUserData import InterfaceEvUserData
from typing import Callable
import numpy as np
from dataclasses import dataclass



@dataclass
class EvUserDataParameters:
    MEAN_DURATION_IN_S=1627 
    STDDEV_DURATION_IN_S=987


class EvUserData(InterfaceEvUserData):

    def __init__(self, 
                 max_parking_time: timedelta,
                 step_time: timedelta):
        self.ev_user_data_parameters = EvUserDataParameters()
        self.arrival_datetime: datetime = None
        self.max_parking_time: timedelta = max_parking_time
        self.min_parking_time: timedelta = timedelta(minutes=10)
        self.step_time: timedelta = step_time
        
        
        self.stay_duration_distribution: Callable[[],timedelta] = \
            lambda: max(self.min_parking_time,min([timedelta(\
                seconds=np.random.normal(self.ev_user_data_parameters.MEAN_DURATION_IN_S + self.step_time.total_seconds(),\
                                         self.ev_user_data_parameters.STDDEV_DURATION_IN_S)), self.max_parking_time]))

     
    def get_arrival_datetime(self):
        return self.arrival_datetime
    
    def get_stay_duration(self):
        return self.stay_duration_distribution()
    
    def update_time(self,time: datetime):
        self.arrival_datetime = time

