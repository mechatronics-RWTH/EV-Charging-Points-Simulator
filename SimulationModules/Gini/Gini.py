from enum import Enum
from datetime import timedelta
import numbers
import pathlib
from typing import Union

import numpy as np
from SimulationModules.Batteries.PowerMap import COMPACTEmpriricChargingPowerMap
from config.definitions import ROOT_DIR
from matplotlib import image
import pygame

from SimulationModules.Batteries.Battery import Battery
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ElectricVehicle.EV import InterfaceEV
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.Enums import GiniModes

from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

relative_path_gini =pathlib.Path(r"SimulationEnvironment/image/Gini_pictogram.png")
FILEPATH = pathlib.Path(ROOT_DIR).joinpath(relative_path_gini)
gini_logo = image.imread(FILEPATH)

TRAVEL_TIME_PER_FIELD=timedelta(seconds=2)

class GINI(InterfaceEV, InterfaceChargingStation):
    """
    The GINI class represents the GINI robot. The GINI robot has a
    battery which has some power characteristics. 
    The GINI can be connected via its CCS inlet to a charging station and 
    via its CCS outlet to an EV or potentially even another GINI

    Depending on what the GINI is "doing" the mode changes. 
    """

    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Gini_pictogram.png")))

    def __init__(self,
                 starting_field_index: int,
                 battery: Battery = None,
                 maximum_charging_power: PowerType = PowerType(11, PowerTypeUnit.KW),
                 minimum_charging_power: PowerType = PowerType(-11, PowerTypeUnit.KW),
                 energy_demand: EnergyType = EnergyType(20,EnergyTypeUnit.KWH),
                 my_id_generator: Union[None,  ID_register]= None,
                 logo=gini_logo):
        
        super().__init__(my_id_generator)
        #super().__init__() InterfaceChargingStation has no init atm so we dont need that constr

        self.logo=logo

        #the gini always moves, if the target field is not the actual field
        self.field_index=starting_field_index
        self.target_field_index=starting_field_index
        self.status = GiniModes.IDLE
        self.travel_time=timedelta(seconds=0)

        maximum_power: PowerType = PowerType(power_in_w=50 * 1000), 
        minimum_power: PowerType = PowerType(power_in_w=50 * 1000)
        power_map=COMPACTEmpriricChargingPowerMap(maximum_power=maximum_power,minimum_power=minimum_power)
        self.battery = Battery(power_map=power_map) if battery is None else battery
        self.energy_demand_at_arrival: EnergyType = min(energy_demand,
                                                        self.battery.get_battery_energy_capacity() -
                                                        self.battery.get_present_energy())
        self.current_energy_demand = self.energy_demand_at_arrival
        #self.ID = 100 id is set by grandparent class InterfaceVehicle
        self.requested_EV = None # EV of users that wants to charge with GINI e.g. booked by app
        self.available = False
        self.departure_time = None
        self.maximum_charging_power=maximum_charging_power
        self.minimum_charging_power=minimum_charging_power
        #the actual_charging_power is calculated in the charging_session and then set 
        #using the method set_actual_chargingpower(). Its the power the gini is giving
        self.actual_charging_power = PowerType(power_in_w=0, unit=PowerTypeUnit.KW)
        self.agent_power_limit_max=None
        self.agent_power_limit_min=None


    """
    def process_charge_ev_request(self, EV_with_request: InterfaceEV):
        self._register_request(EV_with_request)
        if not self.available:
            return 
        elif self.available:
            self._drive_to_EV()
            self._connect_ev()
    """
    def _connect_ev(self):
        if self.requested_EV is not None:
            #self.connect_ev = self.requested_EV
            self.status = GiniModes.CHARGING_EV
            logger.info(f"GINI has been connected to EV with ID {self.requested_EV.id}")
        else:
            raise Exception("No requested_EV for connecting")
    
    def _drive_to_ev(self):
        if self.requested_EV is not None:
            self.status =GiniModes.DRIVING_TO_EV
            logger.info(f"GINI is driving towards EV with ID {self.requested_EV.id}")

    def _return_to_cs(self):
        self.mode = GiniModes.RETURNING_TO_CS
        logger.info(f"GINI is returning to charging station")

    def _register_request(self, electric_vehicle: InterfaceEV):
        self._check_availability()
        if self.available:
            self.requested_EV = electric_vehicle
        else:
            logger.info(f"GINI not available")
    
    def _check_availability(self):
        if self.mode.IDLE | self.mode.CHARGING | self.mode.RETURNING_TO_CS:
            if self.battery.SoC > 0.8 | self.battery.current_energy > self.requested_EV.energy_demand_at_arrival:
                self.available = True
        else: 
            self.available = False

    def get_battery_energy(self):
        return self.battery.get_present_energy()
        
    def update_state(self):
        """
        this Method updates the state of the gini, which is handled by
        the Enum 'GiniModes'
        """
        #at first, we handle the case, that a moving Gini arrives at
        #its requested field:
        if self.status == GiniModes.MOVING and self.field_index == self.target_field_index:
            self.status = GiniModes.IDLE
        #in another case, the gini is IDle and starts to move when its target position 
        #tells him so. The Gini can only switch to moving when its in the idle status
        if self.status == GiniModes.IDLE and self.field_index != self.target_field_index:
            self.status = GiniModes.MOVING

        #if the gini gets a new target position but is still charging, the gini switches to 
        #"interrupting". The csmanager notices that, ends the session and sets the gini to
        #idle
        if self.status in [GiniModes.CHARGING, GiniModes.CHARGING_EV] and self.field_index != self.target_field_index:
            self.status = GiniModes.INTERRUPTING

        #the charging-status is set by the cs_manager too
                
    def update_position(self, distances_for_indices:np.array, 
                        step_time: timedelta):
        """
        this Method moves the Gini if the requested position doesnt 
        equal the actual one and the state is a moving state (1/2)
        untested!
        """
        if self.status==GiniModes.MOVING:

            distance=distances_for_indices[self.field_index, self.target_field_index]
            self.travel_time=distance*TRAVEL_TIME_PER_FIELD

            self.field_index=self.target_field_index
        
        if self.status not in [GiniModes.CHARGING, GiniModes.CHARGING_EV]:
            self.travel_time=max(self.travel_time-step_time, timedelta(seconds=0))

    #functions concerning moving the gini
    def set_target_field(self, target_field_index: int):

        self.target_field_index=target_field_index

    # Implement functions inherited from EV
    def charge_ev(self, energy: EnergyType):
        #this method is used, when the gini is charged as an EV
        #even if the gini is interrupting, it continues charging as long 
        #as the cs manager has not stopped the session
        if self.status not in [GiniModes.CONNECTED_TO_CS, GiniModes.CHARGING, GiniModes.INTERRUPTING]:
            raise Exception(f"Charging not possible if {self.__class__.__name__} not connected, actual status: "+str(self.status))
        energy_before_step=self.battery.get_present_energy()
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
        print("Gini "+str(self.id)+" muesste sich jetzt von cs trennen. Status: "+str(self.status))
        if self.status in [GiniModes.CONNECTED_TO_CS, GiniModes.CHARGING, GiniModes.INTERRUPTING]:
            self.status = GiniModes.MOVING
            #self.connected_CS = None
            print("Gini hat sich jetzt von cs getrennt")
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
        if self.status==GiniModes.INTERRUPTING:
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
            raise ValueError(f"GINI is driving")
        else:
            self.status = GiniModes.CONNECTED_TO_EV
        #self.connected_EV.connect_cs(self)

    def disconnect_ev(self):
        #self.connected_EV.disconnect_from_CS()
        #self.connected_EV = None
        self.status = GiniModes.IDLE
        print("Gini "+str(self.id)+" disconnected und auf idle gesetzt.")

    def get_maximum_cs_charging_power(self):
        """
        the ginis max power when acting as a cs is bound physically,
        by the limit, that is given by the agent and by the
        battery
        """
        """

        """
        max_power=0
        #max_battery_power=self.Battery.get_charging_parameters().maximum_discharging_power*-1
        max_battery_power=PowerType(power_in_w=self.battery.get_charging_parameters().maximum_discharging_power.value*-1,
                                    unit=self.battery.get_charging_parameters().maximum_discharging_power.unit)
        """

        """
        if self.agent_power_limit_max is not None:
            max_power= min(self.maximum_charging_power,
                   self.agent_power_limit_max,
                   max_battery_power)
        else:
            max_power=min(self.maximum_charging_power,
                          max_battery_power)
        """

        """
        return max_power

    def get_maximum_cs_feedback_power(self):
        return PowerType(0, PowerTypeUnit.KW) # GINI can not feedback
    
    def get_cs_id(self):
        return self.id
    
    def give_charging_energy(self, energy: EnergyType):
        #this method discharges the Ginis battery
        
        if self.status not in [GiniModes.CHARGING_EV, GiniModes.CONNECTED_TO_EV, GiniModes.INTERRUPTING]:
            raise Exception(f"Charging an EV is not possible if {self.__class__.__name__} not connected, actual status: "+str(self.status))
        energy_before_step=self.battery.get_present_energy()
        self.battery.charge_battery(EnergyType(-energy.value, energy.unit))
        energy_after_step = self.battery.get_present_energy()
        charged_energy = energy_after_step - energy_before_step
        self.current_energy_demand = self.current_energy_demand - charged_energy
        #if self.current_energy_demand < EnergyType(0):
            #logger.info('This is not supposed to happen')

    def set_agent_power_limit_max(self, power_limit: Union[PowerType, numbers.Number]):
        if not isinstance(power_limit, PowerType):
            self.agent_power_limit_max=PowerType(power_limit, PowerTypeUnit.W)
        else:
            self.agent_power_limit_max=power_limit
    
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
        if self.status==GiniModes.INTERRUPTING:
            return True
        else:
            return False
        
    #the following 2 Methods are inherited by InterfaceVehicle
    def park_vehicle(self, parking_spot):
        raise NotImplementedError

    def leave_parking_area(self):
        raise NotImplementedError
