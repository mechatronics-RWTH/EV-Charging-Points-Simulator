from enum import Enum
from datetime import timedelta
import numbers
import pathlib
from typing import Union

import numpy as np
from SimulationModules.Batteries.PowerMap import COMPACTEmpriricChargingPowerMap
from config.definitions import ROOT_DIR
from matplotlib import image

from SimulationModules.Batteries.Battery import Battery
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ElectricVehicle.EV import InterfaceEV
from SimulationModules.Enums import GiniModes
from SimulationModules.ChargingStation.EfficiencyMap import InterfaceEfficiencyMap, ConstantEfficiencyMap
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from SimulationModules.ChargingSession.InterfaceChargingSessionParticipant import InterfaceChargingSessionParticipant
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField

from config.logger_config import get_module_logger
logger = get_module_logger(__name__)



class GINI(InterfaceEV, 
           InterfaceChargingStation,
           InterfaceMobileChargingStation,
           ):
    """
    The GINI class represents the GINI robot. The GINI robot has a
    battery which has some power characteristics. 
    The GINI can be connected via its CCS inlet to a charging station and 
    via its CCS outlet to an EV or potentially even another GINI

    Depending on what the GINI is "doing" the mode changes. 
    """

    def __init__(self,
                 starting_field: InterfaceField = None,
                 battery: Battery = None,
                 energy_demand: EnergyType = EnergyType(20,EnergyTypeUnit.KWH),
                 assigned_id: int= None,
                 ):
        
        self.id = assigned_id
        self._current_field=starting_field
        self.target_field: InterfaceField =starting_field
        self.status = GiniModes.IDLE
        self.travel_time=timedelta(seconds=0)
        self.time_step_remainder=timedelta(seconds=0)

        maximum_power: PowerType = PowerType(power_in_w=50 * 1000), 
        minimum_power: PowerType = PowerType(power_in_w=50 * 1000)
        power_map=COMPACTEmpriricChargingPowerMap(maximum_power=maximum_power,minimum_power=minimum_power)

        self.battery = Battery(power_map=power_map) if battery is None else battery
        self.efficiency_map = ConstantEfficiencyMap(efficiency=0.94)
        self.energy_demand_at_arrival: EnergyType = min(energy_demand,
                                                        self.battery.get_battery_energy_capacity() -
                                                        self.battery.get_present_energy())
        self.current_energy_demand = self.energy_demand_at_arrival
        self.requested_EV = None # EV of users that wants to charge with GINI e.g. booked by app
        self.available = False
        self.departure_time = None
        self.actual_charging_power = PowerType(power_in_w=0, unit=PowerTypeUnit.KW)
        self.target_power: PowerType = None
        self.parking_spot_index=None

    def _connect_ev(self):
        if self.requested_EV is not None:
            #self.connect_ev = self.requested_EV
            self.status = GiniModes.CHARGING_EV
            logger.info(f"GINI has been connected to EV with ID {self.requested_EV.id}")
        else:
            raise Exception("No requested_EV for connecting")
    

    def get_battery_energy(self):
        return self.battery.get_present_energy()

    #functions concerning moving the gini
    def set_target_field(self, field: InterfaceField):
        self.target_field=field

    # Implement functions inherited from EV
    def charge_ev_with_energy(self, energy: EnergyType):
        #this method is used, when the gini is charged as an EV
        #even if the gini is interrupting, it continues charging as long 
        #as the cs manager has not stopped the session
        if self.status not in [GiniModes.CONNECTED_TO_CS, GiniModes.CHARGING, GiniModes.INTERRUPTING]:
            raise Exception(f"Charging not possible if {self.__class__.__name__} not connected, actual status: "+str(self.status))
        energy_before_step=self.battery.get_present_energy()
        soc_before = self.battery.get_soc()
        self.battery.charge_battery(energy)
        energy_after_step = self.battery.get_present_energy()
        charged_energy = energy_after_step - energy_before_step
        self.current_energy_demand = self.current_energy_demand - charged_energy
        #if self.current_energy_demand < EnergyType(0):
            #logger.info('This is not supposed to happen')

    def connect_cs(self):
        if self.status is GiniModes.IDLE:
            self.status = GiniModes.CONNECTED_TO_CS
            #self.connected_CS = CS
        else:
            Exception("Connecting vehicle not possible.Already connected")

    def disconnect_from_cs(self):
        if self.status in [GiniModes.CONNECTED_TO_CS, GiniModes.CHARGING, GiniModes.INTERRUPTING]:
            self.status = GiniModes.IDLE
            #self.connected_CS = None
        else:
            Exception(f"Disconnecting {self.__class__.__name__} not possible.Not connected")

    def get_soc(self):
        return self.battery.get_soc()

    def get_departure_time(self):
        return self.departure_time

    def get_requested_charging_power(self,
                                     agent_charging_power: PowerType = None):
        if agent_charging_power is None:
            return self.battery.get_charging_parameters().maximum_charging_power
        elif isinstance(agent_charging_power,PowerType):
            return self._calc_requested_power(agent_charging_power)
        else:
            raise ValueError(f"Method expected {type(agent_charging_power)} as input")

    def _calc_requested_power(self,agent_charging_power: PowerType):
        min_val = max([agent_charging_power,
                      self.battery.get_charging_parameters().maximum_discharging_power])
        power_val = min([min_val,
                        self.battery.get_charging_parameters().maximum_charging_power])
        return power_val

    def get_requested_energy(self):
        return self.current_energy_demand

    def set_to_charging(self):
        """
        this method is exclusively used by the csmanager to set the gini to charging
        when the session starts
        """
        self.status = GiniModes.CHARGING

    def wants_interruption_ev(self):
        if self.status in [GiniModes.INTERRUPTING, GiniModes.MOVING]:
            return True
        else:
            return False
        
    # Implement methodes inherited from ChargingStation
    def set_actual_charging_power(self, p: PowerType):
        self.actual_charging_power=p

    def connect_ev(self):
        #self.connected_EV = EV
        if self.status in [GiniModes.CONNECTED_TO_EV, GiniModes.CHARGING_EV]:
            logger.info(f"{self.__class__.__name__} already connected to EV")
        elif self.status in [GiniModes.MOVING]:
            raise Exception(f"GINI is driving")
        else:
            self.status = GiniModes.CONNECTED_TO_EV

    def disconnect_ev(self):
        #self.connected_EV.disconnect_from_CS()
        #self.connected_EV = None
        self.status = GiniModes.IDLE

    def get_maximum_cs_charging_power(self):
        """
        the ginis max power when acting as a cs is bound physically,
        by the limit, that is given by the agent and by the
        battery
        """
        max_power=0
        max_battery_power=abs(self.battery.get_charging_parameters().maximum_discharging_power)
        max_power=max_battery_power
        return max_power
    

    def get_maximum_cs_feedback_power(self):
        return PowerType(0, PowerTypeUnit.KW) # GINI can not feedback
    
    def get_cs_id(self):
        return self.id
    
    def give_charging_energy_over_time(self, energy: EnergyType, delta_time: timedelta):
        #this method discharges the Ginis battery
        if self.status not in [GiniModes.CHARGING_EV, GiniModes.CONNECTED_TO_EV, GiniModes.INTERRUPTING]:
            raise Exception(f"Charging an EV is not possible in stats {self.status.name}, with current field {self.get_current_field()} and target field {self.target_field} " )
        
        energy_with_considered_efficiecy=EnergyType(energy.value*1/self.efficiency_map.get_efficiency(input_power=None), energy.unit)
        energy_before_step=self.battery.get_present_energy()
        self.battery.charge_battery(EnergyType(-energy_with_considered_efficiecy.value, energy.unit))
        energy_after_step = self.battery.get_present_energy()
        charged_energy = energy_after_step - energy_before_step
        self.current_energy_demand = self.current_energy_demand - charged_energy

    def set_target_power(self, power_limit: Union[PowerType, numbers.Number]):
        if power_limit is None:
            self.target_power = None
            return
        if not isinstance(power_limit, PowerType):
            self.target_power=PowerType(power_limit, PowerTypeUnit.W)
        else:
            self.target_power=power_limit
    
    def set_to_charging_ev(self):
        """
        this method is exclusively used by the csmanager to set the gini to charging an ev
        when the session starts
        """
        self.status = GiniModes.CHARGING_EV

    def wants_interruption_cs(self):
        """
        when the gini wants to leave the field, its state changes to interrupting.
        the cs_manager recognizes that and ends the session, so that the gini can move.
        """
        if self.status in [GiniModes.INTERRUPTING, GiniModes.MOVING]:
            return True
        else:
            return False
        
    
    def get_maximum_transferable_energy(self):
        #TODO: this might need to be done in a smarter way for non-constant efficiency
        return self.battery.get_present_energy() * self.efficiency_map.get_efficiency(input_power=None)
    
    def get_maximum_charging_power(self):
        return self.battery.get_charging_parameters().maximum_charging_power
    

    def get_maximum_discharging_power(self):
        return self.battery.get_charging_parameters().maximum_discharging_power


    def update_remaining_travel_time(self, step_time: timedelta):
        self.time_step_remainder = step_time
        if self.is_traveling():
            if step_time > self.travel_time:
                self.time_step_remainder = step_time - self.travel_time
                self.travel_time = timedelta(seconds=0)
                
            else:
                self.travel_time -= step_time
                self.time_step_remainder = timedelta(seconds=0)

            
        
    def get_remaining_travel_time(self):
        return self.travel_time

    def is_traveling(self):
        return self.travel_time > timedelta(seconds=0)       
    

    def get_time_step_remainder(self):
        return self.time_step_remainder
    
    def get_maximum_receivable_energy(self):
        logger.info(f"Battery capacity : {self.battery.get_battery_energy_capacity().get_in_kwh().value} kWh and present energy: {self.battery.get_present_energy().get_in_kwh().value} kWh")
        return self.battery.get_battery_energy_capacity() - self.battery.get_present_energy()

    def get_target_power(self):
        return self.target_power
    
    def is_ready_start_session(self) -> bool:
        return self.status in [GiniModes.IDLE]


    def get_current_field(self):
        return self._current_field
    
    def set_current_field(self, field: InterfaceField):
        self._current_field = field
    
    def __str__(self):
        return f"Gini (id={self.id}, status={self.status.name},field={self._current_field})"