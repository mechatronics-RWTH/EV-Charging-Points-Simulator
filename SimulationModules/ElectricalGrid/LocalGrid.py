from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ElectricalGridConsumer
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.datatypes.PowerType import PowerType
from typing import List
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
import numpy as np

from helpers.Diagnosis import timeit

class LocalGrid(InterfaceTimeDependent):
    """
    A class to represent the local grid

    """

    def __init__(self,
                 time_manager,
                 connected_consumers: List[ElectricalGridConsumer]=[]
                 ):
        self._time_manager: InterfaceTimeManager = time_manager
        self.stationary_battery: StationaryBatteryStorage = None
        self.PV: PhotovoltaicArray = None
        self.building: Building = None 
        self.connected_consumers: List[ElectricalGridConsumer] = []
        if len(connected_consumers)>0:
            for consumer in connected_consumers:
                self.add_consumers(consumer) 
        self.power_trajectory:PowerTrajectory = PowerTrajectory()

    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager
       

    def get_current_connection_load(self) -> PowerType:        
        #self.calculate_connection_point_load()
        return self.power_trajectory.get_power_at_time(self.time_manager.get_current_time())

    def add_consumers(self, consumer_to_add: ElectricalGridConsumer):
        if consumer_to_add in self.connected_consumers:
            raise ValueError(f"Consumer {consumer_to_add} already in connected consumers {self.connected_consumers}")
            
        self.connected_consumers.append(consumer_to_add)
        self.add_PV_system(consumer_to_add)
        self.add_building_system(consumer_to_add)
        self.add_ESS_system(consumer_to_add)

    def add_PV_system(self,
                      consumer:ElectricalGridConsumer):
        if isinstance(consumer, PhotovoltaicArray):
            self.PV = consumer
    
    def add_building_system(self,
                            consumer: ElectricalGridConsumer):
        if isinstance(consumer, Building):
            self.building = consumer

    def add_ESS_system(self, 
                       consumer: ElectricalGridConsumer):
        if isinstance(consumer, StationaryBatteryStorage):
            self.stationary_battery = consumer

    def calculate_connection_point_load(self) -> PowerType:
        """
        this method sums up allpower contributions in th grid.
        that for pushing energy in the grid is counted positive
        """  
        powersum: PowerType = sum([consumer.get_power_contribution() for consumer in self.connected_consumers])
        self.power_trajectory.add_power_value(powersum, self.time_manager.get_current_time())
        

    def get_total_power_drawn(self) -> PowerType:
        powersum: PowerType = sum([consumer.get_power_contribution() for consumer in self.connected_consumers if consumer.get_power_contribution() < PowerType(0)])
        return powersum

    def get_total_power_provided(self) -> PowerType:
        powersum: PowerType = sum([consumer.get_power_contribution() for consumer in self.connected_consumers if consumer.get_power_contribution() > PowerType(0)])
        return powersum


    def get_pv_power_future(self):
        if self.PV is None:
            raise ValueError("No PV system connected to the grid")
        #self.PV.update_horizon()
        future_power_trajectory: PowerTrajectory =self.PV.get_power_future()       
        return future_power_trajectory.get_power_list() 
    
    def get_building_power_future(self):
        if self.building is None:
            raise ValueError("No building connected to the grid")
        #self.building.update_horizon()
        future_power_trajectory: PowerTrajectory=self.building.get_power_future()      
        return future_power_trajectory.get_power_list() 


        
        