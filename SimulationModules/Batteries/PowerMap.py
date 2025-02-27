from abc import ABC, abstractmethod
from enum import IntEnum
import numbers
import random
from typing import Union
from config.logger_config import get_module_logger

import numpy as np

from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

logger = get_module_logger(__name__)

class TypeOfChargingCurve(IntEnum):
        """
        #the following describes, which kind of Charging-curve is meant. The curves are from
        https://www.fastnedcharging.com/de/uebersicht-der-marken but they are scaled to 
        min/max power.
        """
        #https://www.fastnedcharging.com/de/uebersicht-der-marken/fiat?model=500e
        COMPACT = 0
        #https://www.fastnedcharging.com/de/uebersicht-der-marken/mazda
        LIMOUSINE = 1
        #https://www.fastnedcharging.com/de/uebersicht-der-marken/porsche?model=Taycan
        SPORT = 2
        #https://www.fastnedcharging.com/de/uebersicht-der-marken/mercedes-benz?model=EQS%20SUV
        SUV = 3  

class InterfaceChargingPowerMap(ABC):
    maximum_power: PowerType
    minimum_power: PowerType

    @abstractmethod
    def get_maximum_charging_power(self, soc: numbers.Number) -> PowerType:
        raise NotImplementedError

    @abstractmethod
    def get_minimum_charging_power(self, soc: numbers.Number):
        raise NotImplementedError
    
    def _set_maximum_charging_power(self, max_charging_points: np.array, maximum_power: PowerType):
        #logger.info(type(maximumPower * max_charging_points))


        return maximum_power * max_charging_points

    def _set_minimum_charging_power(self, min_charging_points: np.array, minimum_power: PowerType):
        return minimum_power * min_charging_points

class SimpleChargingPowerMap(InterfaceChargingPowerMap):
    """
    This class represents a power map for charging. Based on the State of charge
    a different amount of charging and discharging power is available. 
    The maximum and minimum power for a given SoC can be requested via the get_maximum_charging_power 
    and get_minimum_charging_power methods.
    """

    def __init__(self,
                 soc_points: np.array =np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])/ 100,
                 relative_maximum_charging_power_points: np.ndarray = np.array(
                     [100, 100, 95, 90, 85, 75, 60, 40, 20, 10, 5]) / 100,
                 relative_minimum_charging_power_points: np.ndarray = np.flip(
                     np.array([100, 100, 95, 90, 85, 75, 60, 40, 20, 10, 5]) / (-100)),
                 maximum_power: PowerType = PowerType(power_in_w=50 * 1000),
                 minimum_power: PowerType = PowerType(power_in_w=50 * 1000)):

        self.soc_points = soc_points
        self.maximum_power_points: PowerType = self._set_maximum_charging_power(relative_maximum_charging_power_points,
                                                                              maximum_power)
        self.minimum_power_points: PowerType = self._set_minimum_charging_power(relative_minimum_charging_power_points,
                                                                              minimum_power)
        self.map_type = None

    

    def get_maximum_charging_power(self, soc: numbers.Number) -> PowerType:
        if soc == 1:
            return PowerType(0)
        idx = self._find_first_idx(self.soc_points, soc)
        idx1, idx2 = self._get_interp_vals(idx, self.soc_points)
        x1 = self.soc_points[idx1]
        x2 = self.soc_points[idx2]
        y1= self.maximum_power_points[idx1]
        y2= self.maximum_power_points[idx2]
        maximum_charging_power = self._interpolate(x1, x2, y1, y2, soc)
        return maximum_charging_power

    def get_minimum_charging_power(self, soc: numbers.Number) -> PowerType:
        if soc == 0:
            return PowerType(0)
        idx1, idx2 = self._find_indices(self.soc_points, soc)
        x1 = self.soc_points[idx1]
        x2 = self.soc_points[idx2]
        y1= self.minimum_power_points[idx1]
        y2= self.minimum_power_points[idx2]
        minimum_charging_power = self._interpolate(x1, x2, y1, y2, soc)
        return minimum_charging_power

    def _get_interp_vals(self, idx, x_vals):
        idx1 = idx
        idx2 = min(idx1 + 1, len(self.soc_points) - 1)

        return idx1, idx2

    def _find_first_idx(self, lst, soc):
        full_lst = self._find_indices(lst, soc)
        if not full_lst:
            raise ValueError("Soc is not part of axis. Check unit")
        return full_lst[0]

    def _find_indices(self, lst, soc):
        equal_idx_list=[i for i, elem in enumerate(lst) if elem == soc]
        greater_equal_idx_list = [i for i, elem in enumerate(lst) if elem >= soc]
        if equal_idx_list:
            idx1 =equal_idx_list[0]
            idx2= idx1
        elif greater_equal_idx_list:
            idx1 = greater_equal_idx_list[0]-1
            idx2 = min(idx1+1, len(self.soc_points) - 1)
        else:
            raise ValueError('SoC might be out of list range')
        return idx1, idx2

    def _interpolate(self, x1, x2, y1, y2, xsol):
        if x1 != x2:
            dy_inter=(y2 - y1)
            dx_inter=(x2 - x1)
            m = ( dy_inter / dx_inter)
            # logger.info (f'Steigung M: {m}')
        else:
            m = (y2 - y1) * 0 # make sure that m has the right type
        dx = (xsol - x1)
        #logger.info(type(m))
        ysol = y1 + m * dx
        return PowerType(ysol.value, ysol.unit)

class EmpriricChargingPowerMap(InterfaceChargingPowerMap):
    """
    This class represents a power map for charging. Based on the State of charge
    a different amount of charging and discharging power is available. 
    The maximum and minimum power for a given SoC can be requested via the get_maximum_charging_power 
    and get_minimum_charging_power methods.
    This implementation uses charging curves from https://www.fastnedcharging.com/de/uebersicht-der-marken.
    That for, the method expects the Type of the vehicle as a parameter. Depending on this,
    the Relativemaximum_charging_powerPoints are extracted from one of these curves. 
    """
    def __init__(self,
                 maximum_power: PowerType = PowerType(power_in_w=50 * 1000), 
                 minimum_power: PowerType = PowerType(power_in_w=50 * 1000),
                 type = None):
        self.maximum_power = maximum_power
        self.minimum_power = minimum_power
        self.soc_points=np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])/ 100
        
        relative_maximum_charging_power_points = self._set_relative_maximum_charging_power_points()
        relative_minimum_charging_power_points=np.flip(
                     np.array([100, 100, 95, 90, 85, 75, 60, 40, 20, 10, 5]) / (-100))
        

        self.maximum_power_points: PowerType = self._set_maximum_charging_power(relative_maximum_charging_power_points,
                                                                              self.maximum_power)
        self.minimum_power_points: PowerType = self._set_minimum_charging_power(relative_minimum_charging_power_points,
                                                                              self.minimum_power)
        self.map_type = type
        logger.debug(f"Empirical Power Map with max power {self.maximum_power_points} and min power {self.minimum_power_points} created")
    
    @abstractmethod
    def _set_relative_maximum_charging_power_points(self):
        raise NotImplementedError
    
    def get_maximum_charging_power(self, soc) -> PowerType:     
        return self._interpolate_power_values(soc, self.soc_points, self.maximum_power_points)

    def get_minimum_charging_power(self, soc) -> PowerType:
        return self._interpolate_power_values(soc, self.soc_points, self.minimum_power_points)
    
    def _interpolate_power_values(self, soc, soc_points, power_points):


        power_values_in_W=np.array([power.get_in_w().value for power in power_points])

        power_value_in_W=np.interp(soc, soc_points, power_values_in_W)
        return PowerType(power_in_w=power_value_in_W, unit=PowerTypeUnit.W)
    
    # def set_map_type(self, map_type: TypeOfChargingCurve):
    #     self.map_type = map_type

    def get_map_type(self):
        return self.map_type
    
class COMPACTEmpriricChargingPowerMap(EmpriricChargingPowerMap):


    def _set_relative_maximum_charging_power_points(self):
        
        relative_maximum_charging_power_points=np.array(
            [72, 73, 85, 80, 68, 66, 53, 53, 45, 13, 5]) / 85

        return relative_maximum_charging_power_points
    
class LIMOUSINEEmpriricChargingPowerMap(EmpriricChargingPowerMap):


    def _set_relative_maximum_charging_power_points(self):

       
        relative_maximum_charging_power_points=np.array(
            [34, 35, 36, 36, 37, 38, 34, 28, 22, 17, 11]) / 40
             
        return relative_maximum_charging_power_points

class SPORTEmpriricChargingPowerMap(EmpriricChargingPowerMap):


    def _set_relative_maximum_charging_power_points(self):
       
        relative_maximum_charging_power_points=np.array(
            [227, 250, 260, 265, 268, 270, 185, 160, 62, 30, 6]) / 270


        return relative_maximum_charging_power_points

class SUVEmpriricChargingPowerMap(EmpriricChargingPowerMap):

    def _set_relative_maximum_charging_power_points(self):

        
        relative_maximum_charging_power_points=np.array(
            [160, 200, 205, 207, 185, 170, 155, 130, 120, 75, 22]) / 207

        return relative_maximum_charging_power_points
    
class EmpiricPowerMapFactory:

    def __init__(self):
        self.types={
            TypeOfChargingCurve.COMPACT.value: COMPACTEmpriricChargingPowerMap,
            TypeOfChargingCurve.LIMOUSINE.value: LIMOUSINEEmpriricChargingPowerMap,
            TypeOfChargingCurve.SPORT.value: SPORTEmpriricChargingPowerMap,
            TypeOfChargingCurve.SUV.value: SUVEmpriricChargingPowerMap
        }

    def get_power_map_by_type(self, type: Union[TypeOfChargingCurve, None],
                            maximum_power: PowerType = PowerType(power_in_w=50 * 1000), 
                            minimum_power: PowerType = PowerType(power_in_w=50 * 1000)) -> InterfaceChargingPowerMap:

        map=None
        if type is None:
            raise ValueError("Type of Charging curve is not defined")
            # map: EmpriricChargingPowerMap=self.get_power_map_random_type(maximum_power=maximum_power,
            #                                    minimum_power=minimum_power)
        else:
            MapType =self.types.get(type)
            map: EmpriricChargingPowerMap=MapType(maximum_power=maximum_power,
                                                  minimum_power=minimum_power,
                                                  type=type)
        return map
    
    def get_power_map_random_type(self,
                            maximum_power: PowerType = PowerType(power_in_w=50 * 1000), 
                            minimum_power: PowerType = PowerType(power_in_w=50 * 1000)):

        random_key=random.choice(list(self.types.keys()))
        map_type=self.types.get(random_key)
        generated_map: EmpriricChargingPowerMap = map_type(maximum_power=maximum_power,
                                                           minimum_power=minimum_power,
                                                           type=random_key)
        return generated_map
