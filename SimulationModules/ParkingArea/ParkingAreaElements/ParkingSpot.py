from typing import List, Union
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from SimulationModules.ParkingArea.ParkingAreaElements.Field import Field
from SimulationModules.ParkingArea.ParkingAreaElements.ParkingFieldExceptions import FieldAlreadyOccupiedError

from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class ParkingSpot(Field):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """
    #pygame_logo=

    def __init__(self,
                 index: int,
                 position: List[int]):
        super(ParkingSpot, self).__init__(position=position, index=index)
        self.vehicle_parked: InterfaceVehicle = None
        self._mobile_charger: InterfaceMobileChargingStation = None

    def remove_vehicle(self):
        self.vehicle_parked = None

    def park_vehicle(self, vehicle: InterfaceVehicle):
        self.vehicle_parked = vehicle
        self.vehicle_parked.park_vehicle_at_spot(self)

    def remove_charger(self):
        raise TypeError("This is a parking spot, it cannot have a charger")

    def add_charger(self, charger: InterfaceChargingStation):
        raise TypeError("This is a parking spot, it cannot have a charger")

    def has_charging_station(self) -> bool:
        return False

    def has_parked_vehicle(self) -> bool:
        return self.vehicle_parked is not None
    
    def get_parked_vehicle(self) -> InterfaceVehicle:
        return self.vehicle_parked
    
    def get_charger(self) -> InterfaceChargingStation:
        return None

    def get_mobile_charger(self) -> InterfaceMobileChargingStation:
        return self._mobile_charger

    def has_mobile_charging_station(self) -> bool:
        #logger.info(f"Checking if {self} has a mobile charger")        
        return self._mobile_charger is not None
        
    def place_mobile_charger(self, mobile_charger: InterfaceMobileChargingStation):
        if self._mobile_charger is not None:
            raise FieldAlreadyOccupiedError(f"{self} already has a mobile charger: {self._mobile_charger}")
        self._mobile_charger = mobile_charger
        mobile_charger.set_current_field(self)
    
    def remove_mobile_charger(self):
        if self._mobile_charger is None:
            raise TypeError(f"{self} does not have a mobile charger allocated")            
        self._mobile_charger = None

    def __str__(self):
        return f"ParkingSpot at {self.position} with index {self.index}"
        
    


