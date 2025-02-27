from SimulationModules.EvBuilder.InterfaceEvData import InterfaceEvData
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from typing import List, Callable
from datetime import timedelta
import random 
import numpy as np
import copy
from dataclasses import dataclass
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


@dataclass
class EvDataParamerters:
    BATTERY_ENERGY_CAPACITY_DIST_START = 30
    BATTERY_ENERGY_CAPACITY_DIST_STOP = 100
    BATTERY_ENERGY_CAPACITY_DIST_STEP = 5

    MEAN_DEMAND_IN_KWH=28248.67/1000 #These parameters are taken from data, that Stawag gave to us
    STDDEV_DEMANDS_IN_KWH=17082.99/1000 #These parameters are taken from data, that Stawag gave to us


    START_SOC_MIN = 0.1
    START_SOC_MAX = 0.9



class EvData(InterfaceEvData):

    def __init__(self,
                 ) -> None:

        self.ev_data_parameters = EvDataParamerters()
        self.current_battery_capacity: EnergyType = None
        self.energy_demand: EnergyType = None
        self.start_soc: Callable[[],float] = lambda: random.uniform(self.ev_data_parameters.START_SOC_MIN,self.ev_data_parameters.START_SOC_MAX)
        self.max_soc = 0.8
        self.min_soc = 0.05

    def determine_battery_capacity(self) -> EnergyType:
        self.battery_capacity = random.choice([EnergyType(i, EnergyTypeUnit.KWH) for i in range(self.ev_data_parameters.BATTERY_ENERGY_CAPACITY_DIST_START, self.ev_data_parameters.BATTERY_ENERGY_CAPACITY_DIST_STOP, self.ev_data_parameters.BATTERY_ENERGY_CAPACITY_DIST_STEP)])
        return self.battery_capacity
    
    def determine_energy_demand(self) -> EnergyType:
        if self.battery_capacity is None:
            raise ValueError("Battery capacity not set.")
        raw_energy_demand = EnergyType(np.random.normal(self.ev_data_parameters.MEAN_DEMAND_IN_KWH, self.ev_data_parameters.STDDEV_DEMANDS_IN_KWH), EnergyTypeUnit.KWH)
        self.energy_demand = max(EnergyType(0,EnergyTypeUnit.J), min(raw_energy_demand, copy.deepcopy(self.battery_capacity)*(1-self.min_soc)))
        return self.energy_demand
    
    def determine_present_energy(self) -> EnergyType:
        if self.battery_capacity is None:
            raise ValueError("Battery capacity not set.")
        if self.energy_demand is None:
            raise ValueError("Energy demand not set.")
        copy_battery_capacity = copy.deepcopy(self.battery_capacity)
        random_present_energy = self.start_soc()*copy_battery_capacity
        
        present_energy= max(min(random_present_energy,copy_battery_capacity*self.max_soc-self.energy_demand), self.battery_capacity*self.min_soc)
        if present_energy < self.battery_capacity*self.min_soc:
            logger.warning(f"Present energy is below minimum SOC. SOC: {present_energy/copy_battery_capacity}")
        if present_energy > copy_battery_capacity*self.max_soc:
            logger.warning(f"Present energy is above maximum SOC. SOC: {present_energy/copy_battery_capacity}")
        return present_energy
    
    
    def reset_data(self):
        self.current_battery_capacity = None
        self.energy_demand = None                                                                                          
    
    