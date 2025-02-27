from SimulationModules.ParkingArea.ParkingAreaElements.Field import Field
from typing import List

class Obstacle(Field):
    """
        This class describes an unmovable obstacle on the parking lot. This might be a tree,
        a streetlight, a green space or sth like that. In pathfinding, it has to be friven around
    """

    #pygame_logo=


    def __init__(self,
                 index: int,
                 position: List[int]):
        super().__init__(position=position, index=index)


    def has_charging_station(self) -> bool:
        return False

    def has_parked_vehicle(self) -> bool:
        return False
    
    def has_mobile_charging_station(self) -> bool:
        return False
    
    def get_mobile_charger(self):
        raise ValueError(f"{self} does not have a mobile charger")
    
    def get_charger(self):
        raise ValueError(f"{self} does not have a charger")
    
    def get_parked_vehicle(self):
        raise ValueError(f"{self} does not have a vehicle parked")
    
    def park_vehicle(self, vehicle):
        raise ValueError(f"{self} is not a parking spot")
    
    def remove_vehicle(self):
        raise ValueError(f"{self} is not a parking spot")
    
    def place_mobile_charger(self, mobile_charger):
        raise ValueError(f"{self} is not a parking spot")
    
    def remove_mobile_charger(self):
        raise ValueError(f"{self} is not a parking spot")
    
    def __str__(self):
        return f"Obstacle at {self.position} with {self.index}"