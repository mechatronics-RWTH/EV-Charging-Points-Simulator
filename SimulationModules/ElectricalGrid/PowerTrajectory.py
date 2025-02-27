from typing import List, Optional
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
import numpy as np
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class TimeOutOfRangeErrorHigh(Exception):
    pass


class PowerTrajectory:
    def __init__(self, 
                 power_list: Optional[List[PowerType]] = None, 
                 timestamp_list: Optional[List[datetime]] = None):
        self.power: List[PowerType] = power_list if power_list is not None else []
        self.time: List[datetime] = timestamp_list if timestamp_list is not None else []
        self._determine_np_values()
        self.check_axis_length()

    def get_power_at_time(self, time: datetime) -> PowerType:  # Replace Any with the actual type of PowerType
        self.check_axis_length()
        if time < self.time[0]:
            if self.time[0] - time < timedelta(minutes=15):
                logger.debug(f"Time {time} is before first timestamp {self.time[0]}")
            else:
                raise ValueError(f"Time {time} is before first timestamp {self.time[0]}")
    
        if time > self.time[-1]:
            if time - self.time[-1] < timedelta(hours=1):
                logger.debug(f"Time {time} is after last timestamp {self.time[-1]}")
            else:
                raise TimeOutOfRangeErrorHigh(f"Time {time} is after last timestamp {self.time[-1]}")
        
        # Use cached values
        query_time = time.timestamp()
        
        try:
            interpolated_power = np.interp(query_time, self._time_stamps, self._power_in_j)
        except TypeError as e:
            raise TypeError(f"Could not interpolate for {query_time} and {self.time_stamps}: {e}")
        
        return PowerType(power_in_w=interpolated_power, unit=PowerTypeUnit.W)
    
    def get_max_time(self) -> datetime:
        return self.time[-1]

    def get_power_list(self) -> List[PowerType]:
        return self.power

    def get_time_list(self) -> List[datetime]:
        return self.time
    
    def check_axis_length(self):
        if len(self.power) != len(self.time):
            raise ValueError("Power and time lists must have the same length")
    
    def add_power_value(self, power: PowerType, time: datetime):
        self.power.append(power)
        self.time.append(time)
        self.check_axis_length()
        self._update_np_values(power, time)

    def _update_np_values(self, power: PowerType, time: datetime):        
        # Update cached values efficiently
        self._time_stamps = np.append(self._time_stamps, time.timestamp())
        self._power_in_j = np.append(self._power_in_j, float(power.get_in_w().value))

    def _determine_np_values(self):
        self._time_stamps = np.array([time.timestamp() for time in self.time])
        self._power_in_j = np.array([float(power.get_in_w().value) for power in self.power])

    def __len__(self):
        self.check_axis_length()
        return len(self.power)



    