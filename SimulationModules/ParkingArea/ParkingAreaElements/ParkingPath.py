from SimulationModules.ParkingArea.ParkingAreaElements.Field import Field
from SimulationModules.ParkingArea.ParkingAreaElements.ParkingFieldExceptions import FieldAlreadyOccupiedError
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from typing import List


class ParkingPath(Field):
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
        super().__init__(position=position, index=index)
        self._mobile_charger = None


    def has_charging_station(self) -> bool:
        return False
    
    def has_mobile_charging_station(self) -> bool:
        return False
    
    def get_mobile_charger(self):
        return self._mobile_charger
    
    def get_charger(self):
        raise ValueError(f"{self} does not have a charger")
    
    def has_parked_vehicle(self) -> bool:
        return False
    
    def get_parked_vehicle(self):
        raise ValueError(f"{self} does not have a vehicle parked")

    def park_vehicle(self, vehicle):
        raise ValueError(f"{self} is not a parking spot")
    
    def remove_vehicle(self):
        raise ValueError(f"{self} is not a parking spot")
    
    def place_mobile_charger(self, mobile_charger: InterfaceMobileChargingStation):
        if self._mobile_charger is not None:
            raise FieldAlreadyOccupiedError(f"{self} already has a mobile charger")
        self._mobile_charger = mobile_charger
        mobile_charger.set_current_field(self)

    def remove_mobile_charger(self):
        self._mobile_charger = None
