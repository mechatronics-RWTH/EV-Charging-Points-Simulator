import datetime
import pathlib
from typing import Union
from SimulationModules.Enums import Request_state
import pygame
from config.definitions import ROOT_DIR

from abc import ABC, abstractmethod
import copy


from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.ElectricVehicle.id_register import ID_register
from enum import Enum, IntEnum
from SimulationModules.RequestHandling.InterfaceRequester import InterfaceRequester
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle
from SimulationModules.ChargingSession.InterfaceChargingSessionParticipant import InterfaceChargingSessionParticipant

from config.logger_config import get_module_logger

logger = get_module_logger(__name__)





class InterfaceEV(InterfaceChargingSessionParticipant):
    
    def __init__(self,
                 my_id_generator: ID_register= Union[None, ID_register]):
        super().__init__(my_id_generator)
        self.battery: Battery = None 
    

    @abstractmethod
    def charge_ev_with_energy(self, energy: EnergyType):
        raise NotImplementedError

    @abstractmethod
    def connect_cs(self):
        raise NotImplementedError

    @abstractmethod
    def disconnect_from_cs(self):
        raise NotImplementedError

    @abstractmethod
    def get_requested_charging_power(self):
        raise NotImplementedError

    @abstractmethod
    def get_requested_energy(self):
        raise NotImplementedError

    @abstractmethod
    def get_soc(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_to_charging(self):
        raise NotImplementedError
    
    @abstractmethod
    def wants_interruption_ev(self):
        #when an ev wants to end the session for any reasons,
        #this method gives true
        raise NotImplementedError
    
    @abstractmethod
    def get_maximum_receivable_energy(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_maximum_charging_power(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_maximum_discharging_power(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_target_power(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_target_power(self, power: PowerType):
        raise NotImplementedError

    @abstractmethod
    def set_charging_request(self, charging_request: Request):
        raise NotImplementedError
    

class EV_modes(IntEnum):
    """
    The GINI can have operate in different modes
        IDLE -> Doing nothing
        DRIVING_TO_EV -> While GINI is driving to an EV
        RETURNING_TO_CS -> While GINI is driving back to charging station
        CHARGING_EV -> While GINI is connected to an EV
        CHARGING-> While GINI is connected to charging station
    """
    IDLE = 0
    CONNECTED = 1
    CHARGING = 2
    INTERRUPTING=3

class EV(InterfaceVehicle,
        InterfaceEV,
         InterfaceRequester,
         
         ):
    """
    This class represents an electric vehicle (EV). 
    An EV shall have a specific time of arrival and a duration for staying. 
    In the time that it stays the energy_demand should be fullfiled. 

    The EV can be charged by the charge_ev method.

    """

    #pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/EV_pictogram_v2.png")))

    def __init__(self, arrival_time: datetime.datetime,
                 stay_duration: datetime.timedelta,
                 energy_demand: EnergyType,
                 battery: Union[None, Battery] = None,
                 my_id_generator: Union[None,  ID_register]= None,
                 ):
                 
        super().__init__(my_id_generator)
        self.actual_power = PowerType(0)
        self._charging_request: Request = None
        self.battery: Battery = BatteryBuilder().build_battery() if battery is None else battery
        self.arrival_time = arrival_time
        self.stay_duration = stay_duration
        self.departure_time = self.arrival_time + self.stay_duration
        self.energy_demand_at_arrival: EnergyType = min(energy_demand,
                                                        self.battery.get_battery_energy_capacity() -
                                                        self.battery.get_present_energy())
        logger.debug(f"Energy demand at arrival: {self.energy_demand_at_arrival}")
        #TODO: Add setter for the current energy demand with property. current energy demand shall not be greater than
        # difference to max energy
        self.current_energy_demand = copy.deepcopy(self.energy_demand_at_arrival)
            #EnergyType(self.energy_demand_at_arrival.value, self.energy_demand_at_arrival.unit)
        self.status = EV_modes.IDLE
        self.parking_spot_index: int = None
        self.soc_demand=(self.battery.get_present_energy()+self.energy_demand_at_arrival)/self.battery.get_battery_energy_capacity()

    @property
    def charging_request(self) -> Request:
        return self._charging_request

    def set_charging_request(self, charging_request: Request):
        self._charging_request = charging_request


    def charge_ev_with_energy(self, energy: EnergyType):
        """This method is supposed to charge the EV by a certain amout of energy"""
        if self.status not in [EV_modes.CONNECTED, EV_modes.CHARGING]:
            raise Exception("Charging not possible if EV not connected")
        energy_before_step=self.battery.get_present_energy()
        self.battery.charge_battery(energy)
        energy_after_step = self.battery.get_present_energy()
        charged_energy = energy_after_step - energy_before_step
        self.current_energy_demand = self.get_requested_energy() - charged_energy
        

    def connect_cs(self):
        if self.status is EV_modes.IDLE:
            self.status = EV_modes.CONNECTED
            #self.connected_CS = CS
        else:
            Exception("Connecting vehicle not possible.Already connected")

    def disconnect_from_cs(self):
        if self.status is not EV_modes.IDLE:
            self.status = EV_modes.IDLE
            #self.connected_CS = None
        else:
            Exception("Disconnecting vehicle not possible.Not connected")

    def get_departure_time(self):
        return self.departure_time

    def get_requested_charging_power(self):
        return self.battery.get_charging_parameters().maximum_charging_power

    def get_requested_energy(self):
        return self.current_energy_demand

    def get_soc(self):
        return self.battery.get_soc()

    def set_to_charging(self):
        if self.status==EV_modes.INTERRUPTING:
            raise Exception(f"EV {self} is already interrupting")
        self.status=EV_modes.CHARGING
        if self.charging_request is not None:
            self.charging_request.set_to_charge()
        else:
            self._charging_request = Request(Request_state.CHARGING)

    def wants_interruption_ev(self):
        if self.status==EV_modes.INTERRUPTING:
            return True
        else:
            return False

    def get_battery_energy(self):
        return self.battery.get_present_energy()

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id},Status={self.status.name},SoC={self.battery.state_of_charge})"

    #the following 2 Methods are inherited by InterfaceVehicle
    def park_vehicle_at_spot(self, parking_spot):
        self.parking_spot_index = parking_spot.index

    def leave_parking_area(self):
        raise NotImplementedError
    
    def get_request_state(self):

        return self.charging_request.state
    

    def get_maximum_charging_power(self):
        return self.battery.get_charging_parameters().maximum_charging_power
    

    def get_maximum_discharging_power(self):
        return self.battery.get_charging_parameters().maximum_discharging_power
    
    def get_maximum_receivable_energy(self):
        return self.battery.get_battery_energy_capacity()-self.battery.get_present_energy()
    
    def get_target_power(self):
        return None 
    
    def set_target_power(self, power: PowerType):
        pass

    #TODO: Check if it should be only CONFIRMED or both
    def is_ready_start_session(self) -> bool:
        check1 = self.charging_request.state in [Request_state.CONFIRMED, Request_state.REQUESTED]
        check2 = self.status not in [EV_modes.INTERRUPTING]
        return check1 and check2
    
    def set_actual_charging_power(self, power: PowerType):
        self.actual_power = power

