from abc import ABC, abstractmethod
import random
from typing import List, Tuple
from datetime import datetime, timedelta
from SimulationModules.ElectricVehicle.EV import EV, InterfaceEV
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class InterfaceParkingSpotAssigner(ABC):
    parking_area: ParkingArea

    @abstractmethod
    def assign_parking_spots(self, evs: List[InterfaceEV]):
        pass

    @abstractmethod
    def assign_parking_spot(self, ev: InterfaceEV):
        pass


class ParkingSpotAssigner(InterfaceParkingSpotAssigner):
    def __init__(self,
                 parking_area:ParkingArea):
        self.parking_area: ParkingArea = parking_area  # Parking area object
        self.random_choice_field_index = None  # Random choice field index


    def assign_parking_spots(self, evs: List[InterfaceEV]):
        raise NotImplementedError



    def assign_parking_spot(self, ev):
        raise NotADirectoryError
    
    def assign_parking_spot_randomly(self):
        # Logic to assign a random free parking spot
        #at first we chose the parkingspot
        
        try:
            logger.debug(f"Available parking spots {len(self.parking_area.parking_spot_not_occupied)}")
            self.random_choice_field_index = random.choice(self.parking_area.parking_spot_not_occupied).index
        except IndexError:
            raise NoParkingSpotAvailableError(f"No free parking spot available {self.parking_area.parking_spot_not_occupied}")



class RandomParkingSpotAssigner(ParkingSpotAssigner):
    def assign_parking_spots(self, evs: List[InterfaceEV]):
        for ev in evs:
            self.assign_parking_spot(ev)

    def assign_parking_spot(self, ev: InterfaceEV) -> Tuple[int , InterfaceEV]:
        # Logic to assign a random free parking spot
        #at first we chose the parkingspot
        try:
            self.assign_parking_spot_randomly()
            self.parking_area.park_new_ev_at_field(ev=ev, 
                                        field_index=self.random_choice_field_index)
        except NoParkingSpotAvailableError as e:
            logger.error(f"Error: {e}. This happened when assigning parking spot to EV {ev}")
        

class ChargingStationParkingSpotAssigner(ParkingSpotAssigner):
    def assign_parking_spots(self, evs: List[InterfaceEV]):
        for ev in evs:
            self.assign_parking_spot(ev)

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
        self.parking_area.park_new_ev_at_field(ev=ev, 
                                      field_index=field_index)
        
class FixedParkingSpotAssigner(InterfaceParkingSpotAssigner):
    def __init__(self,
                 parking_area:ParkingArea):
        self.parking_area: ParkingArea = parking_area  # Parking area object


    def assign_parking_spots(self, evs: List[InterfaceEV]):
        for ev in evs:
            self.assign_parking_spot(ev)

    def assign_parking_spot(self, ev: InterfaceEV):
        field_index_to_park_at: int = ev.parking_spot_index
        if field_index_to_park_at is None:
            raise ValueError("Parking spot index is None, cannot assign with FixedParkingSpotAssigner")
        # Logic to assign a fixed parking spot
        self.parking_area.park_new_ev_at_field(ev=ev, 
                            field_index=field_index_to_park_at)
        


    


class ParkingSpotAssignerBuilder:

    @staticmethod
    def build_assigner(assigner_mode: str, 
                       parking_area:ParkingArea):
        if assigner_mode == "random":
            return RandomParkingSpotAssigner(parking_area=parking_area)
        elif assigner_mode == "charging_station":
            return ChargingStationParkingSpotAssigner(parking_area=parking_area)
        elif assigner_mode == "fixed":
            return FixedParkingSpotAssigner(parking_area=parking_area)
        else:
            raise ValueError("Invalid config parameter")

class NoParkingSpotAvailableError(Exception):
    def __init__(self, message="No free parking spot available"):
        self.message = message
        super().__init__(self.message)
