from SimulationModules.Enums import TypeOfField, AgentRequestAnswer

from typing import List
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceEnvMpcMapper import InterfaceEnvMpcMapper
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class EnvMpcMapper(InterfaceEnvMpcMapper):
    def __init__(self,
                 type_of_fields: List[TypeOfField] = None) -> None:
        
        self.type_of_field = type_of_fields
        if self.type_of_field is not None:
            self.create_parking_spot_id_mapping(self.type_of_field)
        else:
            self.field_to_parking_spot_mapping: dict = None
        self.charging_spot_list = None
        self.num_parking_spots = 0
        self.num_chargers = 0
        self.num_robots = 0
    

    def create_parking_spot_id_mapping(self, type_of_field: List[TypeOfField]):
        if self.type_of_field is None:
            self.type_of_field = type_of_field
        self.field_to_parking_spot_mapping = {}
        for index, field_kind in enumerate(self.type_of_field):
            if field_kind == TypeOfField.ParkingSpot.value:
                self.field_to_parking_spot_mapping[index] = len(self.field_to_parking_spot_mapping)

    def count_parking_spots(self):
        logger.debug(self.type_of_field)
        self.num_parking_spots = 0
        for field_kind in self.type_of_field:
            if field_kind == TypeOfField.ParkingSpot.value:
                self.num_parking_spots += 1
    
    def get_num_parking_spots(self):
        return self.num_parking_spots
    
    def determine_num_chargers(self, type_of_field: List[TypeOfField]):
        self.num_chargers = 0
        for field_kind in type_of_field:
            if field_kind == TypeOfField.GiniChargingSpot.value:
                self.num_chargers += 1
        

    def get_num_chargers(self):
        return self.num_chargers
    
    def determine_num_robots(self, robot_states: List[AgentRequestAnswer]):
        self.num_robots = 0
        self.num_robots = len(robot_states)

    def get_num_robots(self):
        return self.num_robots


    def get_parking_spot_id_for_field_index(self, field_index: int):
        try: 
            parking_spot_id = self.field_to_parking_spot_mapping[field_index]
        except KeyError as e:
            raise KeyError(f"Field index {field_index} not in mapping {self.field_to_parking_spot_mapping}: {e}") 
        return parking_spot_id
    
    def get_field_index_from_parking_spot_id(self, parking_spot_id: int):
        return next(index for index, id in self.field_to_parking_spot_mapping.items() if id == parking_spot_id)
    
    def check_if_in_parking_spot_list(self, field_index: int):
        return field_index in self.field_to_parking_spot_mapping.keys()
    
    def create_charging_spot_list(self, type_of_field: List[TypeOfField]):
        self.charging_spot_list = [j for j,field_kind in enumerate(type_of_field) if field_kind==TypeOfField.GiniChargingSpot.value]

    def get_charging_spot_by_index(self, index: int):
        return self.charging_spot_list[index]
    
    def get_charging_spot_index_from_field(self, charging_spot_index: int):
        return next(index for index, id in enumerate(self.charging_spot_list) if id == charging_spot_index)
    
    

    
    



    

    