import os
from typing import Union


import numpy as np
from datetime import datetime, timedelta
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager

from SimulationModules.ElectricalGrid.ElectricalGridConsumer import UncontrolledElectricalGridConsumer
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory, TimeOutOfRangeErrorHigh
from typing import List
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from config.logger_config import get_module_logger
from SimulationModules.ElectricalGrid.FuturePowerMapCreator import InterfaceFuturePowerMap

logger = get_module_logger(__name__)

class PhotovoltaicArray(UncontrolledElectricalGridConsumer):
    
    def __init__(self,
                 name: str,
                future_power_map: InterfaceFuturePowerMap= None,
                 ):
        super().__init__(name)
        self.future_power_map:InterfaceFuturePowerMap = future_power_map
        
    def get_power_contribution(self) -> PowerType:
        power = self.future_power_map.get_power_for_time()
        return power 

    def get_power_future(self):
        return self.future_power_map.get_future_power_for_time()
    
