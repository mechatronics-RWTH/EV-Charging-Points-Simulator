from SimulationModules.Batteries.Battery import Battery
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.Batteries.ChargingParameters import ChargingParameters
from SimulationModules.Batteries.PowerMap import InterfaceChargingPowerMap, TypeOfChargingCurve, EmpiricPowerMapFactory


class BatteryBuilder:
    maximum_charging_power: PowerType
    maximum_discharging_power: PowerType
    battery_energy: EnergyType
    present_energy: EnergyType
    charging_power_map: InterfaceChargingPowerMap


    def build_battery(self,
                      power_map_type:TypeOfChargingCurve = TypeOfChargingCurve.LIMOUSINE,
                      battery_energy: EnergyType = EnergyType(50, EnergyTypeUnit.KWH),
                      present_energy: EnergyType = EnergyType(30, EnergyTypeUnit.KWH),
                        maximum_charging_c_rate: float = 1.5,
                        maximum_discharging_c_rate: float = 1.5,

                      ) -> Battery: 
        self.battery_energy: EnergyType = battery_energy
        self.present_energy: EnergyType = present_energy
        if present_energy > battery_energy:
            raise ValueError("Present energy cannot be greater than battery energy")
        self.set_maximum_power_limits_by_c_rate(battery_energy=battery_energy,
                                                maximum_charging_c_rate=maximum_charging_c_rate,
                                        maximum_discharging_c_rate=maximum_discharging_c_rate)
        self.derive_power_map(power_map_type=power_map_type)
        return self.create_battery()
    

    def set_maximum_power_limits_by_c_rate(self, 
                                 battery_energy: EnergyType,
                                 maximum_charging_c_rate: float, 
                                maximum_discharging_c_rate: float):
    
        self.maximum_charging_power: PowerType = PowerType(power_in_w=battery_energy.get_in_kwh().value*maximum_charging_c_rate, 
                                                                unit=PowerTypeUnit.KW)  # kW
        self.maximum_discharging_power: PowerType = PowerType(power_in_w=battery_energy.get_in_kwh().value*maximum_discharging_c_rate, 
                                                                   unit=PowerTypeUnit.KW)  # kW

    def derive_power_map(self, power_map_type:TypeOfChargingCurve):
        
        power_map_factory=EmpiricPowerMapFactory()
        self.charging_power_map: InterfaceChargingPowerMap = power_map_factory.get_power_map_by_type(
                                                    type=power_map_type,
                                                    maximum_power=self.maximum_charging_power,
                                                    minimum_power=self.maximum_discharging_power)
    
    def create_battery(self,):
        return Battery(battery_energy=self.battery_energy,
                       present_energy=self.present_energy,
                       power_map=self.charging_power_map)