from SimulationModules.ElectricVehicle.EV import InterfaceEV
from datetime import datetime, timedelta
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from typing import Union

from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation, ChargingStation
from SimulationModules.Gini.Gini import GINI
from abc import ABC, abstractmethod

class IChargingSession(ABC):
    @abstractmethod
    def step(self, step_time: timedelta, agent_power_setpoint: PowerType = None, current_time: datetime=None):
        raise NotImplementedError

    @abstractmethod
    def end_session(self):
        raise NotImplementedError

    @abstractmethod
    def _calculate_charging_power(self, agent_power_setpoint: PowerType = None):
        raise NotImplementedError

class ChargingSession(IChargingSession):
    """
    This class represents a charging session between a charging station and an 
    electric vehicle (or in this context charging robot GInI). A charging session
    is composed of an EV/Gini, a charging station (CS) and (optionally) a charging controller. 

    The delivered power is calculated based on the capabilities of the EV that is being charged
    (or discharged in case of bidi charging) and the capabilities of the charging station. 
    In case a charging controller is present, it can provide a setpoint within the limits of the 
    CS and the EV.

    Since multiple charging session can run in parallel in one environment it makes sense to define 
    asynchronous methods for it

    """

    def __init__(self,
                 ev: InterfaceEV,
                 charging_station: InterfaceChargingStation,
                 departure_time: datetime,
                 global_time: datetime,
                 field_index: int,

                 ):

        # self.controller = controller
        self.ev : InterfaceEV= ev
        self.field_index=field_index
        self.charging_station : Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charging_station
        self.ev.connect_cs()
        self.charging_station.connect_ev()
        self.departure_time = departure_time if departure_time is not None else ev.get_departure_time()
        self.time = global_time
        self.start_time=global_time
        self.session_id = self.time.strftime("%Y%m%d%H%M") + "EV" + \
                         str(self.ev.id) + "CS" + \
                         str(self.charging_station.get_cs_id())
        self.actual_charging_power = PowerType(0)
        charging_station.set_to_charging_ev()
        ev.set_to_charging()

    def step(self, step_time: timedelta, 
             agent_power_setpoint: PowerType = None,
             current_time: datetime=None):
        

        self._calculate_charging_power(agent_power_setpoint)
        delta_energy=EnergyType(energy_amount_in_j=0)
        #we differentiate between an EV charged by aGini an charged by a station
        time_to_charge=step_time
        if isinstance(self.charging_station, GINI):            

            
            if self.charging_station.travel_time > step_time:
                self.charging_station.travel_time-=step_time
                time_to_charge=timedelta(seconds=0)
            else:
                time_to_charge = step_time - self.charging_station.travel_time
                self.charging_station.travel_time=timedelta(seconds=0)

            delta_energy = min([self.actual_charging_power * time_to_charge,
                               self.ev.battery.get_battery_energy_capacity()-
                               self.ev.battery.get_present_energy(),
                               self.charging_station.battery.get_present_energy()]
            )

        
        elif isinstance(self.ev, GINI):

            if self.ev.travel_time > step_time:
                self.ev.travel_time-=step_time
                time_to_charge=timedelta(seconds=0)
            else:
                time_to_charge = step_time - self.ev.travel_time
                self.ev.travel_time = timedelta(seconds=0)

            delta_energy = min([self.actual_charging_power * time_to_charge,
                               self.ev.battery.get_battery_energy_capacity()-
                               self.ev.battery.get_present_energy()]
            )

        else:
            delta_energy = min([self.actual_charging_power * time_to_charge,
                               self.ev.battery.get_battery_energy_capacity()-
                               self.ev.battery.get_present_energy()]
            )
                   
        self.ev.charge_ev(delta_energy)
        self.charging_station.give_charging_energy(delta_energy)   
        
        self.actual_charging_power=PowerType(power_in_w=delta_energy.get_in_j().value/step_time.total_seconds(), unit=PowerTypeUnit.W)
        self.charging_station.set_actual_charging_power(self.actual_charging_power)
        self.time = self.time + step_time

    def end_session(self):
        #here happens everything that has to be done when the session ends.
        self.ev.disconnect_from_cs()
        self.charging_station.set_actual_charging_power(PowerType(power_in_w=0, unit=PowerTypeUnit.W))
        self.charging_station.disconnect_ev()

    def _calculate_charging_power(self, agent_power_setpoint: Union[PowerType, None] = None):
        
        if agent_power_setpoint is not None:
            #logger.info("vorhandener agent_power_setpoint")
            # if agent_power_setpoint is between the limits of the battery and the charging station, take this one
            self.actual_charging_power = min(
                [max([self.ev.battery.charging_parameters.maximum_discharging_power,
                      self.charging_station.get_maximum_cs_feedback_power(),
                      agent_power_setpoint]),
                 self.ev.battery.charging_parameters.maximum_charging_power,
                 self.charging_station.get_maximum_cs_charging_power()])
        else:
            self.actual_charging_power = min([self.ev.battery.charging_parameters.maximum_charging_power,
                                              self.charging_station.get_maximum_cs_charging_power()])
            
    def get_charging_session_status(self):
        return {
                "requested_energy":  self.ev.get_requested_energy(),
                "time_to_departure": self.departure_time - self.time,
                "charging_power": self.actual_charging_power
                }


class StationaryStorageChargingSession(IChargingSession):

    def __init__(self, 
                 battery_storage: StationaryBatteryStorage,
                 global_time: datetime):
        self.battery_storage = battery_storage
        self.time = global_time
        self.actual_charging_power = PowerType(0)
        self.field_index = None 
        self.session_id = self.time.strftime("%Y%m%d%H%M") + "_StatStorage"

    def step(self, step_time: timedelta, 
             agent_power_setpoint: PowerType = None,
             ):
        #self._calculate_charging_power(agent_power_setpoint)
        target_power = self.battery_storage.get_target_consumer_charging_power()
        if target_power is None:
            target_power = self.battery_storage.get_maximum_consumer_power()
        delta_energy = min([target_power * step_time,
                            self.battery_storage.get_battery_energy_capacity()-
                            self.battery_storage.get_present_energy()]
                            )
        delta_energy = max([delta_energy, self.battery_storage.get_present_energy()*(-1)])
        self.battery_storage.charge_battery(delta_energy)
        self.actual_charging_power=PowerType(power_in_w=delta_energy.get_in_j().value/step_time.total_seconds(), unit=PowerTypeUnit.W)
        self.battery_storage.set_actual_consumer_charging_power(self.actual_charging_power)
        self.time = self.time + step_time

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
