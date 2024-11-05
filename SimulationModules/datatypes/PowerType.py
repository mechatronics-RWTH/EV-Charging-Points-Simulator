from enum import Enum
import numbers
from typing import Union
from SimulationModules.datatypes.DatatypesBaseClass import DatatypesBaseClass
from datetime import timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit


class PowerTypeUnit(str, Enum):

    W = 'W'
    KW = 'kW'


class PowerType(DatatypesBaseClass):
    
    def __init__(self, power_in_w= numbers.Number, unit: PowerTypeUnit = PowerTypeUnit.W):
        self.value = power_in_w
        self.unit = unit
        self.units = PowerTypeUnit
        #
        # if abs(power_in_w)>0 and abs(power_in_w)< 0.1*1000:
        #     raise UserWarning(f"Your power amount is only {power_in_w} {self.unit}..."
        #     "You might have used the wrong unit when defining it")


    def get_in_w(self):
        self._kw_to_w()
        return self

    def get_in_kw(self):
        self._w_to_kw()
        return self
 


    def _w_to_kw(self):
        if self.unit is PowerTypeUnit.KW:
            return
        self.value =self.value/(1000)
        self.unit = PowerTypeUnit.KW

    def _kw_to_w(self):
        if self.unit is PowerTypeUnit.W:
            return
        self.value =self.value*1000
        self.unit = PowerTypeUnit.W

    def _transform_unit(self):
        switch_func ={
            PowerTypeUnit.W: self.get_in_kw,
            PowerTypeUnit.KW: self.get_in_w,
        }
        switch_func[self.unit]()

    def __mul__(self, other: Union[timedelta, numbers.Number]):
        """
        __mul__ is the function overloader for * (multiplication)
        """
        if isinstance(other,timedelta):
            self._kw_to_w()
            value = EnergyType(self.value*other.total_seconds(), EnergyTypeUnit.J)
            return value
        else:

            value = self.value * other
            return PowerType(value, self.unit)

