from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from SimulationModules.ParkingArea.ParkingAreaElements import Obstacle, GiniChargingSpot
from SimulationModules.ParkingArea.ParkingAreaElements.ParkingFieldExceptions import FieldAlreadyOccupiedError
from SimulationModules.Enums import GiniModes
from datetime import timedelta
from typing import List
import numpy as np
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

TRAVEL_TIME_PER_FIELD=timedelta(seconds=2)

class GiniMover:
    
    def __init__(self, 
                 parking_area: ParkingArea,
                 step_time: timedelta = None):
        self.parking_area: ParkingArea = parking_area
        self.ginis: List[InterfaceMobileChargingStation] = []
        self.step_time = step_time

    def move_ginis(self):
        self.update_state()
        self.update_position()

    
    
    def add_ginis(self, ginis: List[InterfaceMobileChargingStation]):
        self.ginis.extend(ginis)

    def assign_gini_to_field(self, field_index_list: List[int]):
        for gini, field_index in zip(self.ginis, field_index_list):
            field = self.parking_area._get_field_by_index(field_index)
            gini._current_field = field
            field.place_mobile_charger(gini)
            assert not isinstance(field, GiniChargingSpot)

           

    def set_gini_targets(self, gini_targets: np.array):
        for gini_idx,target_idx in enumerate(gini_targets):
            if target_idx is None:
                target_idx = self.ginis[gini_idx].get_current_field().index
            target_field = self.parking_area._get_field_by_index(target_idx)
            if not isinstance(target_field, Obstacle):
                self.ginis[gini_idx].set_target_field(target_field)
            else:
                self.ginis[gini_idx].set_target_field(self.ginis[gini_idx].get_current_field())
                #raise Exception(f"Obstacle can't be gini target field! Target with index {target_idx} ignored!")
                logger.warning("obstacle can't be gini target field! Target ignored!")

    #TODO: Find a better place for this 
    def set_new_gini_max_limits(self, gini_power_limits: np.array):
        if gini_power_limits is not None:
            for i, gini in enumerate(self.ginis):
                if gini_power_limits[i] is not None:
                    gini.set_target_power(gini_power_limits[i])

    def get_fields_with_gini(self):
        return [field for field in self.parking_area.parking_area_fields if field.has_mobile_charging_station()]


    def update_position(self
                        ):
        """
        this Method moves the Gini if the requested position doesnt 
        equal the actual one and the state is a moving state (1/2)
        untested!
        """
        for gini in self.ginis:
            self.update_travel_time(gini)
            target_field = gini.target_field
            current_field = gini.get_current_field()
                        
            if target_field is current_field:
                continue
            try:
                target_field.place_mobile_charger(gini) 
            except FieldAlreadyOccupiedError as e:
                logger.error(f"{e}, setting target field to current field")
                gini.target_field = gini.get_current_field()
                continue
            current_field.remove_mobile_charger()


    def update_travel_time(self, gini: InterfaceMobileChargingStation):
        """
        if the Gini is in a moving state, this method sets a new travel time. Gini will only be in Moving state for one
        step. Afterwards the travel time will be reduced up to 0 seconds
        """
        if gini.status==GiniModes.MOVING:
            distance=self.parking_area.get_distance_for_fields(gini.get_current_field(), gini.target_field)
            gini.travel_time=distance*TRAVEL_TIME_PER_FIELD
        gini.travel_time=max(gini.travel_time-self.step_time, timedelta(seconds=0))         

        

    
        #TODO: Check if these might be better placed in the GiniMover 
    def update_state(self):
        """
        this Method updates the state of the gini, which is handled by
        the Enum 'GiniModes'
        """
        for gini in self.ginis:
            current_field = gini.get_current_field()
            #at first, we handle the case, that a moving Gini arrives at
            #its requested field:
            gini_at_target: bool = current_field is gini.target_field
            
            if gini.status == GiniModes.IDLE:
                if not gini_at_target:
                    gini.status = GiniModes.MOVING

            if gini.status == GiniModes.MOVING:
                if gini_at_target:
                    gini.status = GiniModes.IDLE
                else:
                    gini.status = GiniModes.MOVING

            if gini.status == GiniModes.INTERRUPTING:
                gini.status = GiniModes.IDLE

            if gini.status == GiniModes.CHARGING:
                if not gini_at_target:
                    gini.status = GiniModes.MOVING

            if gini.status == GiniModes.CHARGING_EV:
                if not gini_at_target:
                    gini.status = GiniModes.MOVING

