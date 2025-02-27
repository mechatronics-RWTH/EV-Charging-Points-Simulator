from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.ChargingSession.ChargingSession import IChargingSession
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from datetime import datetime, timedelta
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit


class StationaryStorageChargingSession(IChargingSession,
                                       InterfaceTimeDependent):

    def __init__(self, 
                 battery_storage: StationaryBatteryStorage,
                 time_manager: InterfaceTimeManager):
        self.battery_storage = battery_storage
        self._time_manager = time_manager
        self.actual_charging_power = PowerType(0)
        self.field_index = None 
        self.session_id = self.time_manager.get_current_time().strftime("%Y%m%d%H%M") + "_StatStorage"

    @property
    def time_manager(self)->InterfaceTimeManager:
        return self._time_manager

    def step(self, 
             ):
        #self._calculate_charging_power(agent_power_setpoint)
        target_power = self.battery_storage.get_target_consumer_charging_power()
        if target_power is None:
            target_power = PowerType(0) #self.battery_storage.get_maximum_consumer_power()
        delta_energy = min([target_power * self.time_manager.get_step_time(),
                            self.battery_storage.get_battery_energy_capacity()-
                            self.battery_storage.get_present_energy()]
                            )
        delta_energy = max([delta_energy, self.battery_storage.get_present_energy()*(-1)])
        self.battery_storage.charge_battery(delta_energy)
        self.actual_charging_power=PowerType(power_in_w=delta_energy.get_in_j().value/self.time_manager.get_step_time().total_seconds(), unit=PowerTypeUnit.W)
        self.battery_storage.set_actual_consumer_charging_power(self.actual_charging_power)
       

    def _calculate_charging_power(self, agent_power_setpoint: PowerType = None):
        if agent_power_setpoint is not None:
            self.actual_charging_power = min(
                [max([self.battery_storage.get_charging_parameters().maximum_discharging_power,
                      agent_power_setpoint]),
                 self.battery_storage.get_charging_parameters().maximum_charging_power])
        else:
            self.actual_charging_power = PowerType(0)

    def end_session(self):
        raise Exception("The charging session with the stationary storage should always be active")
