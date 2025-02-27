from typing import Union
from SimulationModules.Batteries.PowerMap import  InterfaceChargingPowerMap
from SimulationModules.Batteries.ChargingParameters import ChargingParameters
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

EPSILON_IN_KWH = 1e-6

class Battery:
    """
    The class battery defines a battery object with th purpose to charge and discharge it

    The only public method it provides is a method to charge the battery. 
    """

    def __init__(self,
                 power_map: InterfaceChargingPowerMap,
                 battery_energy: EnergyType = EnergyType(50, EnergyTypeUnit.KWH),
                 present_energy: EnergyType = EnergyType(30, EnergyTypeUnit.KWH),
                  ):

        self.battery_energy: EnergyType = battery_energy   
        self.present_energy: EnergyType = present_energy
        if self.battery_energy.value < 0:
            raise ValueError("Battery Energy seems to be negative")
        #the soc is first set to zero and then calculated from the present energy
        self.state_of_charge=0
        self._update_soc()
        self.maximum_soc = 1
        self.minimum_soc = 0.6
        self.charging_power_map: InterfaceChargingPowerMap =power_map
            
        # self.maximum_charging_power_actual = self.charging_power_map.get_maximum_charging_power(
        #     self.state_of_charge)
        self._set_charging_parameters()



    def get_present_energy(self):
        if self.present_energy < EnergyType(-EPSILON_IN_KWH, EnergyTypeUnit.KWH):
            raise ValueError("Present battery Energy seems to be negative")
        return EnergyType(self.present_energy.value, self.present_energy.unit)

    def get_battery_energy_capacity(self):
        if self.battery_energy.value < 0:
            raise ValueError("Battery Energy seems to be negative")
        return EnergyType(self.battery_energy.value, self.battery_energy.unit)

    def charge_battery(self, charged_energy: EnergyType) -> bool:
        self.present_energy = self.get_present_energy() + charged_energy
        outOfBounds = False
        if self.get_present_energy() > EnergyType(-EPSILON_IN_KWH, EnergyTypeUnit.KWH) and self.get_present_energy() < EnergyType(0, EnergyTypeUnit.KWH):
            self.present_energy = EnergyType(0)

        if self.get_present_energy() < EnergyType(-EPSILON_IN_KWH, EnergyTypeUnit.KWH):
            logger.warning(f'Not enough energy available to uncharge {charged_energy.value} {charged_energy.unit}')
            self.present_energy = EnergyType(0)
            outOfBounds = True
        elif self.get_present_energy() > self.get_battery_energy_capacity():
            logger.warning(f'Battery too full to charge with {charged_energy.value} {charged_energy.unit}.')
            self.present_energy = self.get_battery_energy_capacity()
            outOfBounds = True
        if self.battery_energy.value < 0:
            raise ValueError(f"Battery Energy seems to be negative with {self.present_energy.get_in_kwh()} and {charged_energy.get_in_kwh()}")
        self._update_soc()
        self._set_charging_parameters()
        return outOfBounds

    def get_charging_parameters(self):
        return self.charging_parameters

    def _update_soc(self):
        self.state_of_charge = self.present_energy / self.battery_energy
        if self.state_of_charge == 1:
            #self.logger.debug(f'Battery SoC is at 1')
            pass
        elif self.state_of_charge > 1:
            too_high_soc_excep_test = "The SoC cannot be higher than 100%"
            raise ValueError(too_high_soc_excep_test)
        elif self.state_of_charge < 0:
            too_low_soc_excep_test = "The SoC cannot be higher than 100%"
            raise ValueError(too_low_soc_excep_test)

    def get_soc(self):

        self._update_soc()
        return self.state_of_charge

    def _set_charging_parameters(self):
        self.charging_parameters = \
            ChargingParameters(
                maximum_charging_power=self.charging_power_map.get_maximum_charging_power(
                    self.state_of_charge),
                maximum_discharging_power=self.charging_power_map.get_minimum_charging_power(
                    self.state_of_charge),
                maximum_energy=self.get_battery_energy_capacity() - self.get_present_energy(),
                minimum_energy=(self.minimum_soc - self.state_of_charge) * self.get_battery_energy_capacity())
        
    def __str__(self):
        return f"Present energy: {self.present_energy}, Battery energy: {self.battery_energy}, SoC: {self.state_of_charge},  Charging power map: {self.charging_power_map}, Charging parameters: {self.charging_parameters}"
