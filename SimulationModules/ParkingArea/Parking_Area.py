
import numpy as np
import warnings

import copy
import random
import datetime
import pathlib
from config.definitions import ROOT_DIR
from matplotlib import image
from helpers.Diagnosis import timeit
import pygame
from typing import List, Union

from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation, ChargingStation
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle, ConventionalVehicle
from SimulationModules.ElectricVehicle.EV import InterfaceEV, EV, EV_modes
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ParkingArea.ParkingAreaElements import (
    Field, 
    ParkingSpot, 
    Obstacle, 
    GiniChargingSpot, 
    ParkingPath, 
    EntrencePoint, 
    ExitPoint,
    ChargingSpot)
from SimulationModules.ParkingArea import Parking_Area_to_Graph as PAG
from config.logger_config import get_module_logger
from SimulationModules.Gini.Gini import GINI
from SimulationModules.Enums import GiniModes, AgentRequestAnswer, TypeOfField
logger = get_module_logger(__name__)


class ParkingArea():
    """
        This class describes a parking area, which consists of multiple ParkingSpots.
        Vehicles can enter and exit the ParkingArea. The ParkingArea has a specific size.
        It consists of a number of same size quadratic fields. A field can either be a path or
        a ParkingSpot. The ParkingArea further comprises a model that describes the likelihood
        that a new vehicle arrives or departs at a specific time.
    """

    
    def __init__(self,
                 parking_area_x_dir_fields: int = 4,
                 parking_area_y_dir_fields: int = 10,
                 number_parking_spots: int = 18,
                 config: dict =None, 
                 as_graph: bool = False
                 ):
        
        self.config=config

        self.ginis=[]

        if config is not None:

            self.ginis=self.read_gini_config(config)           
            self.amount_ginis=len(self.ginis)

            self.maximum_charging_power_of_installed_chargers = config["max_charging_power"]
            
            if not as_graph:
                path=config["Parking_Lot"]
                lines = self.read_lines_from_file(path)
                self.parking_area_from_txt_non_graph(lines=lines)
        else:
            self.parking_area_fields = None
            self.number_parking_spots = number_parking_spots
            self.parking_area_size = np.array([parking_area_x_dir_fields, parking_area_y_dir_fields])
            self.number_of_fields = self.parking_area_size[0] * self.parking_area_size[1]
            self.maximum_charging_power_of_installed_chargers=PowerType(power_in_w=100,
                                                                        unit=PowerTypeUnit.KW)
            self.arrange_parking_area()

        self.departed_ev_list = []                  
        self.update_field_states()

        self.area_size=len(self.parking_area_fields)
        self.distances_for_indices=self.get_distances_for_indices()
        self.field_kinds=self.get_field_kinds()

    def read_gini_config(self, config: dict):

        gini_starting_fields=config["Gini_starting_fields"]
        gini_battery=Battery(battery_energy=  EnergyType(35, EnergyTypeUnit.KWH),
                            present_energy= EnergyType(35, EnergyTypeUnit.KWH),)
        ginis=[GINI(starting_field_index=field_index, battery=copy.deepcopy(gini_battery)) for field_index in gini_starting_fields]
        
        if not isinstance(ginis, list):
            ginis: List[GINI] =[ginis]
        else:
            ginis: List[GINI]=ginis
        
        return ginis

    def step(self, step_time: datetime.timedelta):

        self.update_field_states()
        self.update_dynamic_elements()


    def parking_area_from_txt_non_graph(self, lines: List[str]):
        '''
        This function takes a txt, where every kind of field is codes as a certain char
        '''        
        self.parking_area_fields = []

        txt_symbol_field_mapping = {    
            "o": ParkingPath,
            "#": ParkingSpot,
            "x": Obstacle,
            "c": GiniChargingSpot,
            "s": ChargingSpot,
        }

        self.parking_area_size = np.array([len(lines[0].strip()), len(lines)])
        counter = 0
        for i, line in enumerate(lines):
            row = []
            for j, char in enumerate(line.strip()):
                position = [j, i]
                selected_class = txt_symbol_field_mapping[char]
                if selected_class is ChargingSpot:
                    field = selected_class(position=position, 
                                           index=counter,
                                           charger=ChargingStation(maximum_charging_power=self.maximum_charging_power_of_installed_chargers))
                elif selected_class is GiniChargingSpot:
                    field = selected_class(position=position, 
                                           index=counter,
                                           charger=ChargingStation(maximum_charging_power=self.maximum_charging_power_of_installed_chargers))
                else:
                    field = selected_class(position=position, 
                                           index=counter)
                self.parking_area_fields.append(field)
                counter += 1

    def read_lines_from_file(self, path: str):

        path = pathlib.Path(path)
        path= pathlib.Path(ROOT_DIR).joinpath(path)

        with open(path, "r") as file:
            lines = file.readlines()
        return lines      
                   
    def arrange_parking_area(self):
        """
        This function takes into account the Number of Parking Spots and the Number of fields
        and assign parkings spots to reasonable fields.
        """
        rowidx = 0
        colidx = 0
        self.parking_area_fields = []
        parking_spot_idx = 0
        self._add_fields_to_parking_area()
        self._add_parking_spots_to_parking_area()
        self._set_entrance_point()
        self._set_exit_point()

        self._set_entrance_point()
        self._set_exit_point()

    def reset(self):
        parking_spot_list = [x for x in self.parking_area_fields if isinstance(x, ParkingSpot)]
        for parking_spot in parking_spot_list:
            parking_spot.remove_vehicle()

        self.ginis=[]
        if self.config is not None:
            gini_starting_fields=self.config["Gini_starting_fields"]
            gini_battery=Battery(battery_energy=  EnergyType(50, EnergyTypeUnit.KWH),
                                present_energy= EnergyType(50, EnergyTypeUnit.KWH),)
            self.ginis=[GINI(starting_field_index=field_index, battery=copy.deepcopy(gini_battery)) for field_index in gini_starting_fields]
        
        self.update_field_states()

    def add_charging_station(self,
                             charger: InterfaceChargingStation,
                             position=None):
        if position is None:
            parking_spot_list = [x for x in self.parking_area_fields if isinstance(x, ParkingSpot)]
            parking_spot_without_charger = [x for x in parking_spot_list if x.charger is None]
            chosen_parking_spot = parking_spot_without_charger[0]
        else:
            chosen_parking_spot = self._get_field_by_position(position)

        self.parking_area_fields.remove(chosen_parking_spot)
        charging_spot = ChargingSpot(position=chosen_parking_spot.position, index=chosen_parking_spot.index)
        self.parking_area_fields.append(charging_spot)

    def update_field_states(self):
        self.parking_spot_list: List[ParkingSpot]= [x for x in self.parking_area_fields if isinstance(x, ParkingSpot)]
        self.parking_spot_not_occupied: List[ParkingSpot] = [parking_spot for parking_spot in self.parking_spot_list if not parking_spot.has_parked_vehicle() ]
        self.parking_spot_with_free_charger: List[ParkingSpot] = [parking_spot for parking_spot in self.parking_spot_not_occupied if parking_spot.has_charging_station()]

    def update_dynamic_elements(self):

            for gini in self.ginis:
                gini.update_state()
                #gini.update_position()

    def park_new_vehicle(self,
                         vehicle: InterfaceVehicle,
                         position: Union[List[int], None] =None):
        if position is None:            
            if isinstance(vehicle, ConventionalVehicle):
                # convential vehicles can only park on parking spots without charging stations
                available_parking_spot = [x for x in  self.parking_spot_not_occupied if not x.has_charging_station()]
            else:
                available_parking_spot = self.parking_spot_not_occupied
            
            if available_parking_spot:
                chosen_parking_spot = self.parking_spot_not_occupied[0]
                chosen_parking_spot.park_vehicle(vehicle)
            else:
                raise Exception(f"All suitable parking spots seem to occupied")
        else:
            chosen_parking_spot: ParkingSpot = self._get_field_by_position(position)
            if not isinstance(chosen_parking_spot, ParkingSpot):
                raise Exception("Field with position "+str(position)+" is not a Parking_Spot")
            if chosen_parking_spot.has_parked_vehicle():
                raise Exception("Field with position "+str(position)+" is already occupied")
            chosen_parking_spot.park_vehicle(vehicle)
        
        # The list is updated to reflect the new state of the parking area
        self.parking_spot_not_occupied.remove(chosen_parking_spot)
        if chosen_parking_spot.has_charging_station():
            self.parking_spot_with_free_charger.remove(chosen_parking_spot)    

    def park_new_ev(self,
                         ev: InterfaceEV = None,
                         field_index: int=None,
                         ):     
        
        
        if field_index is None:
            chosen_parking_spot = random.choice(self.parking_spot_not_occupied)
            logger.warning("No field index was given, so a random field was chosen")
        else:
            chosen_parking_spot: ParkingSpot =self._get_field_by_index(field_index) 
            if not isinstance(chosen_parking_spot, ParkingSpot):
                raise Exception(f"Chosen field is not a Parking_Spot, but {type(chosen_parking_spot)}, field index {field_index}")
            if chosen_parking_spot.has_parked_vehicle():
                raise Exception(f"Chosen field is already occupied, field index {field_index}")             

        chosen_parking_spot.park_vehicle(ev)
        self.parking_spot_not_occupied.remove(chosen_parking_spot)

        if chosen_parking_spot.has_charging_station():            
            self.parking_spot_with_free_charger.remove(chosen_parking_spot)  

    def ev_departures(self, current_time: datetime) -> List[InterfaceEV]:
        """
        This method handles evs, which want to leave. If an ev 
        is still charging at that timethe status changes to interrupting
        and then the cs_manager ends the session.
        """
        self.departed_ev_list = []
        for field in self.parking_spot_list:
            if field.has_parked_vehicle():
                ev=field.vehicle_parked
                if ev.departure_time <= current_time:
                    if ev.status==EV_modes.CHARGING:
                        ev.status=EV_modes.INTERRUPTING
                    else:
                        self.remove_vehicle(ev)
                        self.departed_ev_list.append(ev)
        
    def set_gini_targets(self, gini_targets: np.array):

        for i, gini in enumerate(self.ginis):
            if gini_targets[i] is not None:
                if not isinstance(self._get_field_by_index(gini_targets[i]), Obstacle):
                    gini.set_target_field(gini_targets[i])
                else:
                    gini.set_target_field(gini.field_index)
                    warnings.warn("obstacle can't be gini target field! Target ignored!")

    def set_new_gini_max_limits(self, gini_power_limits: np.array):

        if gini_power_limits is not None:
            for i, gini in enumerate(self.ginis):
                if gini_power_limits[i] is not None:
                    gini.set_agent_power_limit_max(gini_power_limits[i])

    def set_new_cs_max_limits(self, target_charging_powers: np.array):
        
        fields: List[Field]=self.parking_area_fields
        for field in fields:
            if field.has_charging_station():
                if target_charging_powers[field.index] is not None:
                    field.charger.set_target_grid_charging_power(PowerType(
                        target_charging_powers[field.index], 
                        PowerTypeUnit.W)                 
                    )
                else:
                    field.charger.set_target_grid_charging_power()

    def remove_vehicle(self,
                         vehicle: InterfaceVehicle =None,
                         position: List[int]=None,
                         field_index: int =None):
        

        if position is None and vehicle is not None:
            #the following line was changed by Milan, maybe we talk about that before merging to main
            parking_spot_occupied = [x for x in self.parking_spot_list if x.has_parked_vehicle()]
            if isinstance(vehicle, ConventionalVehicle):
                parking_spot_occupied = [x for x in parking_spot_occupied if not x.has_charging_station()]
            if parking_spot_occupied:
                chosen_parking_spot = next((item for i, item in enumerate(parking_spot_occupied) if item.vehicle_parked.id == vehicle.id), None)
            else:
                raise Exception(f"No suitable parking spots seem to be occupied")
        
        if field_index is not None:
            chosen_parking_spot = next((item for i, item in enumerate(self.parking_spot_list) if item.vehicle_parked.id == vehicle.id), None)
        if chosen_parking_spot is None:
            raise Exception("No vehicle with ID "+str(vehicle.id)+" found")
        
        chosen_parking_spot.remove_vehicle()

        self.parking_spot_not_occupied.append(chosen_parking_spot)
        if chosen_parking_spot.has_charging_station():
            self.parking_spot_with_free_charger.append(chosen_parking_spot)

    def _add_fields_to_parking_area(self):
        counter=0
        for row in range(self.parking_area_size[1]):
            for col in range(self.parking_area_size[0]):
                position = [col, row]
                self.parking_area_fields.append(ParkingPath(position=position, index=counter))
                counter+=1

    def _add_parking_spots_to_parking_area(self):
        parking_spot_idx = 0
        rowidx = 0
        colidx = 0
        while rowidx < self.parking_area_size[1] - 1:
            colidx = 0
            while colidx < self.parking_area_size[0]:
                current_position = [colidx, rowidx]
                field = self._get_field_by_position(current_position)
                index=field.index
                self.parking_area_fields.remove(field)
                new_parking_spot = ParkingSpot(position=current_position, index=index)
                self.parking_area_fields.append(new_parking_spot)

                parking_spot_idx += 1
                colidx += 3
            rowidx += 1

    def _set_entrance_point(self):
        for field in self.parking_area_fields:
            if field.position[1] == 0 and isinstance(field, ParkingPath):                
                entrance_point = EntrencePoint(position=field.position, index=field.index)
                self.parking_area_fields.remove(field)
                self.parking_area_fields.append(entrance_point)
                return

    def _set_exit_point(self):
        for field in self.parking_area_fields:
            if field.position[1] == 0 and isinstance(field, ParkingPath):
                exit_point = ExitPoint(position=field.position, index=field.index)
                self.parking_area_fields.remove(field)
                self.parking_area_fields.append(exit_point)
                return

    def _get_field_by_position(self, position: List[int]) -> Field:

        field: Field = next((field for field in self.parking_area_fields if position == field.position), None)
        if field is None:
            raise ValueError(f"Field with position: {position} not found")
        else:
            return field 
        
    def _get_field_by_index(self, index: int):
        field = next((item for item in self.parking_area_fields if item.index == index), None)
        if field is None:
            raise ValueError("No field found with index "+str(index))
        return field
        
    def _get_parking_spot_position(self):
        parking_spot_position = []
        for field in self.parking_area_fields:
            if isinstance(field, ParkingSpot):
                parking_spot_position.append(field.position)
        return parking_spot_position

    def get_gini_by_field_index(self, field_index: int):
        found_gini=None
        for gini in self.ginis:
            if gini.field_index ==field_index:
                found_gini=gini

        return found_gini

    def get_charging_station_list(self):
        """
        this method gives back a list which contains 
        all chargingstations of the area. This method is
        used for example to initialize the local grid
        """
        return [field.charger for field in self.parking_area_fields if field.has_charging_station()]
    
    def get_fields_with_parked_vehicle(self):
        return [field for field in self.parking_area_fields if field.has_parked_vehicle()]
    
    def get_fields_with_gini(self):
        return [field for field in self.parking_area_fields if self.get_gini_by_field_index(field.index) is not None]

    def _check_if_is_type(self, position, type):
        is_parking_spot = position in self._get_parking_spot_position()
        # isParkingSpot = np.apply_along_axis(all, 1, mask).any()
        return is_parking_spot

    def get_field_kinds(self):

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

        field_kinds=np.array(field_kinds)
        return field_kinds
    
    def get_distances_for_indices(self):
      
        self.parking_area_graph=PAG.pa_as_graph(self)

        #distances_for_indexes is an array with all dijkstra distances for all pairs of Fieldindices
        distances_for_fields=[PAG.dijkstra_distances(self.parking_area_graph, self._get_field_by_index(i)) for i in range(self.area_size)]
        distances_for_indices=np.zeros([self.area_size,self.area_size])
        for i in range(self.area_size):
            for j in range(self.area_size):
                list=distances_for_fields[i]
                distances_for_indices[i,j]=list[self._get_field_by_index(j)]

        return distances_for_indices