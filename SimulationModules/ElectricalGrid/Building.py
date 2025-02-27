import os

from SimulationModules.ElectricalGrid.ElectricalGridConsumer import UncontrolledElectricalGridConsumer
from SimulationModules.ElectricalGrid.FuturePowerMapCreator import InterfaceFuturePowerMap
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from config.logger_config import get_module_logger
from config.definitions import ROOT_DIR


logger = get_module_logger(__name__)


class Building(UncontrolledElectricalGridConsumer
               ):

    
    def __init__(self, 
                 name: str,
                 future_power_map: InterfaceFuturePowerMap= None,):
        super().__init__(name)
        self.future_power_map:InterfaceFuturePowerMap = future_power_map
        

    def get_power_contribution(self) -> PowerType:
        power = self.future_power_map.get_power_for_time()
        return -power

    def get_power_future(self)-> PowerTrajectory:
        return self.future_power_map.get_future_power_for_time()


