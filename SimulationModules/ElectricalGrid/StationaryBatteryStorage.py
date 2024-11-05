import numbers
from SimulationModules.Batteries.Battery import Battery 
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.ChargingStation.EfficiencyMap import InterfaceEfficiencyMap, EfficiencyMap, ConstantEfficiencyMap


class StationaryBatteryStorage(Battery, ControlledEletricalGridConsumer):
    def __init__(self, 
                 energy_capacity: EnergyType,
                 present_energy: EnergyType, 
                 maximum_charging_c_rate: numbers.Number = 1.5,
                 minimum_charging_c_rate: numbers.Number = 0.15,
                 maximum_discharging_c_rate: numbers.Number = 1.5,
                 minimum_discharging_c_rate: numbers.Number = 1,
                 efficiency_map: InterfaceEfficiencyMap = ConstantEfficiencyMap(efficiency=0.97)):
        Battery.__init__(self, battery_energy=energy_capacity, 
                         present_energy=present_energy, 
                         maximum_charging_c_rate=maximum_charging_c_rate, 
                         minimum_charging_c_rate=minimum_charging_c_rate, 
                         maximum_discharging_c_rate=maximum_discharging_c_rate, 
                         minimum_discharging_c_rate=minimum_discharging_c_rate)

        ControlledEletricalGridConsumer.__init__(self, name ="StationaryBatteryStorage",
                                                 maximum_charging_power=PowerType(0),
                                                 minimum_charging_power=PowerType(0),
                                                 efficiency_map=efficiency_map)
        self._update_charging_power_limits()


    # def get_power_contribution(self, time):
    #     return self.actual_power
    
    def _update_charging_power_limits(self):
        self._set_charging_parameters()
        chargingParameters = self.get_charging_parameters()
        self.maximum_grid_power = self.efficiency_map.get_input_power(chargingParameters.maximum_charging_power) 
        self.minimum_grid_power = self.efficiency_map.get_input_power(chargingParameters.maximum_discharging_power)
    
    def set_target_grid_charging_power(self, power: PowerType):
        self._update_charging_power_limits()
        super().set_target_grid_charging_power(power)
    

    
