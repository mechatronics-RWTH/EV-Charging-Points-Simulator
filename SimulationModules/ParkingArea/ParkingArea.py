
import numpy as np
import random
from typing import List, Union
from SimulationModules.ParkingArea.Parking_Area_to_Graph import determine_distances_for_indices
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle, ConventionalVehicle
from SimulationModules.ElectricVehicle.EV import InterfaceEV
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.ParkingArea.ParkingAreaElements import *


from config.logger_config import get_module_logger

from SimulationModules.Enums import  TypeOfField
from SimulationModules.RequestHandling.RequestCollector import RequestCollector


logger = get_module_logger(__name__)

class ParkingSpotAlreadyOccupiedError(Exception):
    pass


class ParkingArea():
    """
        This class describes a parking area, which consists of multiple ParkingSpots.
        Vehicles can enter and exit the ParkingArea. The ParkingArea has a specific size.
        It consists of a number of same size quadratic fields. A field can either be a path or
        a ParkingSpot. The ParkingArea further comprises a model that describes the likelihood
        that a new vehicle arrives or departs at a specific time.
    """

    
    def __init__(self,
                 parking_area_fields: List[InterfaceField]=[],
                 request_collector: RequestCollector=None):
        self.parking_area_fields: List[InterfaceField] = parking_area_fields
        self.parking_spot_list: List[ParkingSpot] = []
        self.parking_spot_occupied: List[InterfaceField] = []
        self.parking_spot_not_occupied: List[ParkingSpot] = []
        self.parking_spot_with_free_charger: List[ParkingSpot] = []
        self.number_parking_spots = None 
        self.parking_area_size: List[int,int] = None
        self.fields_with_chargers: List[InterfaceField] = []
        self.fields_with_ev: List[InterfaceField] = []
        self.request_collector: RequestCollector = request_collector
        self.departed_ev_list = []
        self.distances_for_indices = None 
        self.field_kinds=None


    def initialize_parking_area(self):
        if self.parking_area_fields is None or len(self.parking_area_fields) == 0:
            raise ValueError("No parking area fields are given")
        self.distances_for_indices = determine_distances_for_indices(self)
        self.determine_parking_spots()
        self.determine_number_parking_spots()
        self.determine_fields_with_chargers()
        self.update_field_states()
        self.determine_field_kinds()

    def get_distance_for_fields(self, start_field, end_field):
        distance = self.distances_for_indices[start_field.index, end_field.index]
        if distance is None:
            raise ValueError(f"No distance found for fields {start_field} and {end_field}")
        if distance < 0:
            raise ValueError(f"Negative distance found for fields {start_field} and {end_field}")
        if distance > 1e6: 
            raise ValueError(f"Distance is infinite for fields {start_field} and {end_field}")
        return distance
        
      

    def determine_fields_with_chargers(self):
        self.fields_with_chargers = [field for field in self.parking_area_fields if field.has_charging_station()]
        
    def determine_parking_spots(self):
        self.parking_spot_list: List[ParkingSpot]= [x for x in self.parking_area_fields if isinstance(x, ParkingSpot)]


    def determine_number_parking_spots(self):
        self.number_parking_spots = len(self.parking_spot_list)

    def update_parking_area(self):
        
        self.update_field_states()
        #self.update_dynamic_elements()

    def update_field_states(self):
        self.parking_spot_occupied: List[ParkingSpot] = [x for x in self.parking_spot_list if x.has_parked_vehicle()]
        
        self.parking_spot_not_occupied: List[ParkingSpot] = [parking_spot for parking_spot in self.parking_spot_list if not parking_spot.has_parked_vehicle() ]
        # Find the intersection
        self.parking_spot_with_free_charger: List[ParkingSpot] = list(set(self.parking_spot_not_occupied) & set(self.fields_with_chargers))



    def park_new_ev_at_field(self,
                         ev: InterfaceEV = None,
                         field_index: int=None,
                         ):     
        
        
        if field_index is None:
            chosen_parking_spot = random.choice(self.parking_spot_not_occupied)
            logger.warning("No field index was given, so a random field was chosen")
        else:
            chosen_parking_spot: ParkingSpot =self.get_parking_spot_by_index(field_index) 
            
            if chosen_parking_spot.has_parked_vehicle():
                raise ParkingSpotAlreadyOccupiedError(f"Chosen field is already occupied, field index {field_index} and by " 
                                                      f"{chosen_parking_spot.vehicle_parked} with arrival time {chosen_parking_spot.vehicle_parked.arrival_time} " 
                                                      f"and departure {chosen_parking_spot.vehicle_parked.get_departure_time()}")           

        chosen_parking_spot.park_vehicle(ev)
        #TODO: Having this whole requests here coupled is not so nice - maybe observer pattern?
        ev.set_charging_request(charging_request= Request(field_index=chosen_parking_spot.index),
                                )
        current_request = ev.charging_request
        self.request_collector.add_request(current_request)
        self.parking_spot_not_occupied.remove(chosen_parking_spot)
        if chosen_parking_spot.has_charging_station():            
            self.parking_spot_with_free_charger.remove(chosen_parking_spot) 

    
    def remove_vehicle(self,
                         vehicle: InterfaceVehicle):
        parking_spot_to_remove_vehicle_from: ParkingSpot = next((x for x in self.parking_spot_occupied if x.vehicle_parked == vehicle), None)
        if parking_spot_to_remove_vehicle_from is None:
            raise Exception(f"vehicle {vehicle} not found with ocupied parking spots {self.parking_spot_occupied}")
        parking_spot_to_remove_vehicle_from.remove_vehicle()
        self.request_collector.remove_request(vehicle.charging_request)
        self.parking_spot_occupied.remove(parking_spot_to_remove_vehicle_from)
        self.parking_spot_not_occupied.append(parking_spot_to_remove_vehicle_from)
        if parking_spot_to_remove_vehicle_from.has_charging_station():
            self.parking_spot_with_free_charger.append(parking_spot_to_remove_vehicle_from)
      
    #TODO: This should not be here
    def set_new_cs_max_limits(self, 
                              target_charging_powers: np.array):
        
        for field in self.fields_with_chargers:
            if target_charging_powers[field.index] is not None:
                charger = field.get_charger()
                charger.set_target_grid_charging_power(PowerType(
                    target_charging_powers[field.index], 
                    PowerTypeUnit.W)                 
                )
            else:
                charger = field.get_charger()
                charger.set_target_grid_charging_power()


    def _get_field_by_index(self, index: int):
        field = next((item for item in self.parking_area_fields if item.index == index), None)
        if field is None:
            raise ValueError("No field found with index "+str(index))
        return field

    def get_parking_spot_by_index(self, index: int):
        field = next((item for item in self.parking_spot_list if item.index == index), None)
        if field is None: 
            raise ValueError(f"No field found with index {index} in parking spot list {self.parking_spot_list}")
        return field

    def get_charging_station_list(self):
        """
        this method gives back a list which contains 
        all chargingstations of the area. This method is
        used for example to initialize the local grid
        """
        return [field.get_charger() for field in self.fields_with_chargers]
    
    def get_fields_with_parked_vehicle(self):
        return [field for field in self.parking_area_fields if field.has_parked_vehicle()]  

    def determine_field_kinds(self):

        #the following describes, which kind of fields there are
        #0=path, 1=normal parkingspot, 2=parkingspot with chargingstation, 3=obstacle
        field_kinds=[]
        for field in self.parking_area_fields:
            if isinstance(field, ParkingPath):
                field_kinds.append(TypeOfField.ParkingPath.value)
            elif isinstance(field, GiniChargingSpot) or isinstance(field, ChargingSpot):
                field_kinds.append(TypeOfField.GiniChargingSpot.value)
            elif isinstance(field, ParkingSpot):
                field_kinds.append(TypeOfField.ParkingSpot.value)

            elif isinstance(field, Obstacle):
                field_kinds.append(TypeOfField.Obstacle.value)

        self.field_kinds=np.array(field_kinds)
        
    


    
