from typing import List
import copy
from SimulationModules.Gini.Gini import GINI
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.Batteries.PowerMap import TypeOfChargingCurve

class GiniBuilder:
    @staticmethod
    def build( 
              gini_starting_fields: List[int],
              battery_energy: EnergyType = EnergyType(35, EnergyTypeUnit.KWH),
                present_energy: EnergyType = EnergyType(35, EnergyTypeUnit.KWH),
              ) -> List[GINI]:
        battery_energy = battery_energy
        present_energy = present_energy
        battery_builder = BatteryBuilder()
        gini_battery= battery_builder.build_battery(battery_energy=battery_energy,
                                      present_energy=present_energy,
                                      power_map_type=TypeOfChargingCurve.LIMOUSINE,
                                      maximum_charging_c_rate=1.5,
                                      maximum_discharging_c_rate=1.5)
        gini_list = []
        gini_list=[GINI(battery=copy.deepcopy(gini_battery)) for _ in gini_starting_fields]
        
        return gini_list           
