# import pathlib
# from abc import abstractmethod, ABC
# import pygame
# from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation, ChargingStation
# from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle, ConventionalVehicle
# from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
# from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
# from config.definitions import ROOT_DIR
# from typing import List, Union

# # #TODO: Cleanup needs to happen here
# # class Field():
# #     """
# #         This class describes a field that can be either Path, EntrencePoint, ExitPoint or ParkingSpot
# #         the cost is important in Dijkstra, when the field is visited, color is for graph visualisation
# #     """
    

# #     def __init__(self,
# #                 index: int,
# #                 position: List[int],
# #                 ):
# #         self.index=index
# #         self.position = position
# #         #self.cost=cost
# #         #self.color='#000000'
# #         self.vehicle_parked=None
# #         self.logo = None
# #         self.charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = None

# #     @abstractmethod
# #     def has_charging_station(self) -> bool:
# #         raise NotImplementedError

# #     def has_parked_vehicle(self) -> bool:
# #         return False
    
# #     @abstractmethod
# #     def has_mobile_charging_station(self) -> bool:
# #         raise NotImplementedError
    
# #     @abstractmethod
# #     def get_mobile_charger(self) -> InterfaceMobileChargingStation:
# #         raise NotImplementedError
    
# #     @abstractmethod
# #     def get_parked_vehicle(self) -> InterfaceVehicle:
# #         raise NotImplementedError
    
# #     @abstractmethod
# #     def get_charger(self) -> Union[ControlledEletricalGridConsumer, InterfaceChargingStation]:
# #         raise NotImplementedError
    
# #     @abstractmethod
# #     def park_vehicle(self, vehicle: InterfaceVehicle):
# #         raise NotImplementedError
    
# #     @abstractmethod
# #     def remove_vehicle(self):
# #         raise NotImplementedError

# #     @abstractmethod
# #     def place_mobile_charger(self, mobile_charger: InterfaceMobileChargingStation):
# #         raise NotImplementedError

# #     @abstractmethod
# #     def remove_mobile_charger(self):
# #         raise NotImplementedError

    
    









