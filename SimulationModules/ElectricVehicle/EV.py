import datetime
import pathlib
from typing import Union
from SimulationModules.Enums import Request_state
import pygame
from config.definitions import ROOT_DIR
from matplotlib import image
from abc import ABC, abstractmethod


from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.ElectricVehicle.id_register import ID_register
from enum import Enum, IntEnum
# from ChargingStation.ChargingStation import ChargingStation
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle


relativePathCar =pathlib.Path(r"SimulationEnvironment/image/EV_pictogram.png")
FILEPATH = pathlib.Path(ROOT_DIR).joinpath(relativePathCar)
car_logo = image.imread(FILEPATH)


class InterfaceEV(InterfaceVehicle):
    
    def __init__(self,
                 my_id_generator: ID_register= Union[None, ID_register]):
        super().__init__(my_id_generator)
        self.battery: Battery = None 
    
    # @abstractmethod
    # def confirm(self):        
    #     raise NotImplementedError
    
    # @abstractmethod
    # def deny(self):    
    #     raise NotImplementedError

    @abstractmethod
    def charge_ev(self):
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

class EV(InterfaceEV):
    """
    This class represents an electric vehicle (EV). 
    An EV shall have a specific time of arrival and a duration for staying. 
    In the time that it stays the energy_demand should be fullfiled. 

    The EV can be charged by the charge_ev method.

    """

    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/EV_pictogram_v2.png")))

    def __init__(self, arrival_time: datetime.datetime,
                 stay_duration: datetime.timedelta,
                 energy_demand: EnergyType,
                 battery: Union[None, Battery] = None,
                 my_id_generator: Union[None,  ID_register]= None,
                 logo =car_logo):
                 
        super().__init__(my_id_generator)

        self.initial_request_state=Request_state.REQUESTED
        self.logo=logo
        self.battery: Battery = Battery() if battery is None else battery
        self.arrival_time = arrival_time
        self.stay_duration = stay_duration
        self.departure_time = self.arrival_time + self.stay_duration
        self.energy_demand_at_arrival: EnergyType = min(energy_demand,
                                                        self.battery.get_battery_energy_capacity() -
                                                        self.battery.get_present_energy())
        #TODO: Add setter for the current energy demand with property. current energy demand shall not be greater than
        # difference to max energy
        self.current_energy_demand = \
            EnergyType(self.energy_demand_at_arrival.value, self.energy_demand_at_arrival.unit)
        self.status = EV_modes.IDLE



    def charge_ev(self, energy: EnergyType):
        """This method is supposed to charge the EV by a certain amout of energy"""
        if self.status not in [EV_modes.CONNECTED, EV_modes.CHARGING, EV_modes.INTERRUPTING]:
            raise Exception("Charging not possible if EV not connected")
        energy_before_step=self.battery.get_present_energy()
        self.battery.charge_battery(energy)
        energy_after_step = self.battery.get_present_energy()
        charged_energy = energy_after_step - energy_before_step
        self.current_energy_demand = self.get_requested_energy() - charged_energy
        
        if self.current_energy_demand <= EnergyType(0):
            self.current_energy_demand = EnergyType(0)

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
        self.status=EV_modes.CHARGING

    def wants_interruption_ev(self):
        if self.status==EV_modes.INTERRUPTING:
            return True
        else:
            return False

    def get_battery_energy(self):
        return self.battery.get_present_energy()

    def __repr__(self):
        return f"\n{self.__class__.__name__} {self.id} \n" \
               f"Status: {self.status} \nSoC: {self.battery.state_of_charge}\n"

    #the following 2 Methods are inherited by InterfaceVehicle
    def park_vehicle(self, parking_spot):
        raise NotImplementedError

    def leave_parking_area(self):
        raise NotImplementedError
    
    def get_initial_request_state(self):

        return self.initial_request_state