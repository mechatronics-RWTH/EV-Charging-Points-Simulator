from abc import ABC, abstractmethod
from SimulationModules.datatypes.EnergyType import EnergyType
from typing import List, Callable
from datetime import timedelta



class InterfaceEvData(ABC):
    max_parking_time: timedelta
    current_battery_capacity: EnergyType
    energy_demand: EnergyType
    start_soc: Callable[[],float] 



    @abstractmethod
    def determine_battery_capacity(self):
        raise NotImplementedError
    
    @abstractmethod
    def determine_energy_demand(self):
        raise NotImplementedError
    
    @abstractmethod
    def determine_present_energy(self):
        raise NotImplementedError
    
    @abstractmethod
    def reset_data(self):
        raise NotImplementedError

    

    

    
