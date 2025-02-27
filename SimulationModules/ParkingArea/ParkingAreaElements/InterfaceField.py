from abc import ABC, abstractmethod
from typing import List, Union
# from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
# from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
# from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
# from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle


class InterfaceField(ABC):
    """
        This class describes a field that can be either Path, EntrencePoint, ExitPoint or ParkingSpot
        the cost is important in Dijkstra, when the field is visited, color is for graph visualisation
    """
    

    @abstractmethod
    def has_charging_station(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_parked_vehicle(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def has_mobile_charging_station(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def get_mobile_charger(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_parked_vehicle(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_charger(self):
        raise NotImplementedError
    
    @abstractmethod
    def park_vehicle(self, vehicle):
        raise NotImplementedError
    
    @abstractmethod
    def remove_vehicle(self):
        raise NotImplementedError

    @abstractmethod
    def place_mobile_charger(self, mobile_charger):
        raise NotImplementedError

    @abstractmethod
    def remove_mobile_charger(self):
        raise NotImplementedError
