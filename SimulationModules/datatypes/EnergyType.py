from enum import Enum
import numbers
from SimulationModules.datatypes.DatatypesBaseClass import DatatypesBaseClass
import copy
from datetime import timedelta

    


class EnergyTypeUnit(str, Enum):
    J = 'J'
    KWH = 'kWh'


class EnergyType(DatatypesBaseClass):

    def __init__(self, energy_amount_in_j: numbers.Number, 
                 unit: EnergyTypeUnit = EnergyTypeUnit.J):

        self.value = energy_amount_in_j
        self.unit = unit
        self.units = EnergyTypeUnit
        # if abs(energyAmount_in_Js)>0 and abs(energyAmount_in_Js)< 0.1*3600*1000:
        #     raise UserWarning(f"Your energy amount is only {energyAmount_in_Js} {self.unit}..."
        #     "You might have used the wrong unit when defining it")

    def get_in_j(self):
        self._kwh_to_j()
        return self

    def get_in_kwh(self):
        self._j_to_kwh()
        return self

    def set_value(self, set_object: 'EnergyType'):
        if type(set_object) is EnergyType:
            self.value = set_object.value
        else:
            UserWarning(f"Set a numeric value to a EnergyType object. Since unit cannot be checked...\
                this is not a save operation")
            self.value = set_object
        return self

    def _transform_unit(self):
        switch_func = {
            EnergyTypeUnit.KWH: self.get_in_j,
            EnergyTypeUnit.J: self.get_in_kwh,
        }
        switch_func[self.unit]()

    def _j_to_kwh(self):
        if self.unit is EnergyTypeUnit.KWH:
            return
        self.value = self.value / (3600 * 1000)
        self.unit = EnergyTypeUnit.KWH

    def _kwh_to_j(self):
        if self.unit is EnergyTypeUnit.J:
            return
        self.value = self.value * (3600 * 1000)
        self.unit = EnergyTypeUnit.J

    def __truediv__(self, other: 'DatatypesBaseClass'):
        if type(self) == type(other):
            a=copy.deepcopy(self)
            b=copy.deepcopy(other)
            a._same_unit(b)
            value = a.value / b.value
            return value
        elif isinstance(other, timedelta):
            from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
            res_value = self.get_in_j().value / other.total_seconds()
            return PowerType(res_value, PowerTypeUnit.W)
        else:
            res=copy.deepcopy(self)
            res.value = self.value / other
            return res
