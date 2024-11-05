from abc import ABC, abstractmethod
import random
from typing import List, Tuple
from datetime import datetime, timedelta
from SimulationModules.ElectricVehicle.EV import EV, InterfaceEV
from SimulationModules.ParkingArea.Parking_Area import ParkingArea
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class ParkingSpotAssigner(ABC):
    def __init__(self,
                 parking_area:ParkingArea):
        self.parking_area: ParkingArea = parking_area  # Parking area object
        self.random_choice_field_index = None  # Random choice field index


    @abstractmethod
    def assign_parking_spot(self, ev):
        pass
    
    def assign_parking_spot_randomly(self):
        # Logic to assign a random free parking spot
        #at first we chose the parkingspot
        
        try:
            logger.debug(f"Available parking spots {len(self.parking_area.parking_spot_not_occupied)}")
            self.random_choice_field_index = random.choice(self.parking_area.parking_spot_not_occupied).index
        except IndexError:
            raise NoParkingSpotAvailableError(f"No free parking spot available {self.parking_area.parking_spot_not_occupied}")



class RandomParkingSpotAssigner(ParkingSpotAssigner):

    def assign_parking_spot(self, ev: InterfaceEV) -> Tuple[int , InterfaceEV]:
        # Logic to assign a random free parking spot
        #at first we chose the parkingspot
        try:
            self.assign_parking_spot_randomly()
            self.parking_area.park_new_ev(ev=ev, 
                                        field_index=self.random_choice_field_index)
        except NoParkingSpotAvailableError as e:
            logger.error(f"{e}")
        

class ChargingStationParkingSpotAssigner(ParkingSpotAssigner):
    def assign_parking_spot(self, ev: InterfaceEV):
        # Logic to assign a free charging station parking spot
        
        if self.parking_area.parking_spot_with_free_charger:
            # If there is a free charging station, park the EV
            field = random.choice(self.parking_area.parking_spot_with_free_charger)
            if not field.has_charging_station():
                raise ValueError("Field appears to have no charging station")
            field_index = field.index
            logger.warning(f"Charging station field index: {field_index}")
        else:
            # If there is no free charging station, park the EV in a random parking spot
            logger.debug(f"length of free chargers {len(self.parking_area.parking_spot_with_free_charger)}")
            self.assign_parking_spot_randomly()
            field_index = self.random_choice_field_index
        self.parking_area.park_new_ev(ev=ev, 
                                      field_index=field_index)

class ParkingSpotAssignerBuilder:

    @staticmethod
    def build_assigner(config: dict,
                       parking_area:ParkingArea):
        if config == "random":
            return RandomParkingSpotAssigner(parking_area=parking_area)
        elif config == "charging_station":
            return ChargingStationParkingSpotAssigner(parking_area=parking_area)
        else:
            raise ValueError("Invalid config parameter")

class NoParkingSpotAvailableError(Exception):
    def __init__(self, message="No free parking spot available"):
        self.message = message
        super().__init__(self.message)
