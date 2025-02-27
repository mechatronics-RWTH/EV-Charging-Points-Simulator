import pathlib

from matplotlib import image
import numpy as np

from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingSession.InterfaceChargingSessionParticipant import InterfaceChargingSessionParticipant
from enum import Enum
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from datetime import timedelta
from abc import ABC, abstractmethod

from config.definitions import ROOT_DIR

from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

# relativePathCS = pathlib.Path(r"SimulationEnvironment/image/ChargingStation/Charging_Station_MMP.png")
# FILEPATH = pathlib.Path(ROOT_DIR).joinpath(relativePathCS)
# charging_station_logo = image.imread(FILEPATH)

class InterfaceChargingStation(ABC,
                               InterfaceChargingSessionParticipant):

    @abstractmethod
    def connect_ev(self):
        raise NotImplementedError

    @abstractmethod
    def disconnect_ev(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_to_charging_ev(self):
        raise NotImplementedError

    @abstractmethod
    def get_maximum_cs_charging_power(self) -> PowerType:
        raise NotImplementedError

    @abstractmethod
    def get_maximum_cs_feedback_power(self):
        raise NotImplementedError

    @abstractmethod
    def get_cs_id():
        raise NotImplementedError

    @abstractmethod
    def give_charging_energy_over_time(self, energy: EnergyType, delta_time: timedelta):
        #this method discharges the Ginis battery and maybe will do sth with conv 
        #chargingstations
        raise NotImplementedError
    
    @abstractmethod
    def wants_interruption_cs(self):
        #when an cs wants to end the session for any reasons,
        #this method gives true
        raise NotImplementedError
    
    @abstractmethod
    def get_maximum_transferable_energy(self):
        raise NotImplementedError
    
   
    @abstractmethod
    def get_target_power(self):
        raise NotImplementedError
    



class CS_modes(Enum):
    """
    The GINI can have operate in different modes
        IDLE -> Doing nothing 
        DRIVING_TO_EV -> While GINI is driving to an EV
        RETURNING_TO_CS -> While GINI is driving back to charging station            
        CHARGING_EV -> While GINI is connected to an EV
        CHARGING-> While GINI is connected to charging station
    """
    IDLE = 0
    CONNECTED_TO_EV = 1
    CHARGING_EV = 2


class ChargingStation(InterfaceChargingStation,
                      ControlledEletricalGridConsumer,
                      ):

    def __init__(self,
                 maximum_charging_power: PowerType = PowerType(11, PowerTypeUnit.KW),
                 minimum_charging_power: PowerType = PowerType(-11, PowerTypeUnit.KW),
                 my_id_generator: ID_register = ID_register(),
                 ):
        self.id = my_id_generator.get_id()
        ControlledEletricalGridConsumer.__init__(self, 
                                                 name="charging_station_"+str(self.id),
                                                 maximum_charging_power=maximum_charging_power,
                                                 minimum_charging_power=minimum_charging_power)
        

        #the actual_charging_power is calculated in the charging_session and then set 
        #using the method set_actual_chargingpower()
        self.actual_charging_power = PowerType(power_in_w=0, unit=PowerTypeUnit.KW)
        self.status = CS_modes.IDLE
        #self.logo = charging_station_logo
        #the agentpowerlimit is set by the agent as a command. It exists parallel 
        #to the max- and minimumchargingpower, which iare the physical limits of 
        #the charger and is set by the constructor
        self.agent_power_limit_max=None
        self.agent_power_limit_min=None

        #in the next line, we call the init of the ElectricalGridConsumer,
        #InterfaceChargingStation hasnt an init, thats why python knows its
        #the second parent class
        

    def get_cs_id(self):
        return self.id

    def connect_ev(self):
        if self.status in [CS_modes.CONNECTED_TO_EV, CS_modes.CHARGING_EV]:
            logger.info(f"{self.__class__.__name__} already connected to EV")
        else:
            self.status = CS_modes.CONNECTED_TO_EV

    def disconnect_ev(self):
        self.connected_ev = None
        self.status = CS_modes.IDLE
    
    def set_actual_charging_power(self, power: PowerType):
        
        self.set_actual_consumer_charging_power(-power)

    def get_maximum_cs_charging_power(self) -> PowerType:
        #the stations max power is bound physically and 
        #by the limit, that is given by the agent
        max_power=0
        if self.target_grid_power is not None:
            max_grid_power: PowerType = min(self.maximum_grid_power,
                   self.target_grid_power)
            max_power:PowerType = self.efficiency_map.get_output_power(max_grid_power)
            
        else:
            max_power=self.efficiency_map.get_output_power(self.maximum_grid_power)
        return max_power

    def set_agent_power_limit_max(self, power_limit):
        raise NotImplementedError

        
    def set_to_charging_ev(self):

        self.status=CS_modes.CHARGING_EV

    def wants_interruption_cs(self):
        return False

    def get_maximum_cs_feedback_power(self):
        return self.efficiency_map.get_output_power(self.minimum_grid_power)
    
    def get_maximum_transferable_energy(self):
        # the maximum energy is not limited for a conventional charging station, therefore we return a high value
        return EnergyType(10000, EnergyTypeUnit.KWH)


    def __repr__(self):
        return f"{self.__class__.__name__} {self.id} and status: {self.status} "
    
    def give_charging_energy_over_time(self, energy: EnergyType, delta_time: timedelta):
        
        pass

    def get_target_power(self):
        return self.get_target_consumer_charging_power()
    
    def is_ready_start_session(self):
        return self.status == CS_modes.IDLE
    
