from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory, TimeOutOfRangeErrorHigh
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
from config.logger_config import get_module_logger
import numpy as np

logger = get_module_logger(__name__)



class PowerTypeBasedPowerTrajectory(PowerTrajectory): 

    def get_power_at_time(self, time: datetime) -> PowerType:
        self.check_axis_length()
        if time < self.time[0]:
            if self.time[0] - time < timedelta(minutes=15):
                logger.warning(f"Time {time} is before first timestamp {self.time[0]}")
            else:
                raise ValueError(f"Time {time} is before first timestamp {self.time[0]}")
    
        if time > self.time[-1]:
            if time - self.time[-1] < timedelta(hours=1):
                logger.debug(f"Time {time} is after last timestamp {self.time[-1]}")
            else:
                raise TimeOutOfRangeErrorHigh(f"Time {time} is after last timestamp {self.time[-1]}")
        
        # Use cached values
        query_time = time.timestamp()
        _time_stamps = np.array([t.timestamp() for t in self.time])
        _power_in_j = np.array([float(p.get_in_w().value) for p in self.power])
        
        try:
            interpolated_power = np.interp(query_time, _time_stamps, _power_in_j)
        except TypeError as e:
            raise TypeError(f"Could not interpolate for {query_time} and {_time_stamps}: {e}")
        
        return PowerType(power_in_w=interpolated_power, unit=PowerTypeUnit.W)
    
    def add_power_value(self, PowerType: PowerType, time: datetime):
        self.power.append(PowerType)
        self.time.append(time)
        self.check_axis_length()
        


class NpBasedPowerTrajectory(PowerTrajectory):
    
    def get_power_at_time(self, time: datetime) -> PowerType:
        self.check_axis_length()
        if time < self.time[0]:
            if self.time[0] - time < timedelta(minutes=15):
                logger.warning(f"Time {time} is before first timestamp {self.time[0]}")
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
        
    def add_power_value(self, PowerType: PowerType, time: datetime):
        self.power.append(PowerType)
        self.time.append(time)
        self.check_axis_length()
        
        # Update cached values
        # Update cached values efficiently
        self._time_stamps = np.append(self._time_stamps, time.timestamp())
        self._power_in_j = np.append(self._power_in_j, float(PowerType.get_in_w().value))