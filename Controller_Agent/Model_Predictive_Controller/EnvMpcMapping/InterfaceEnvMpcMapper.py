from abc import ABC, abstractmethod
from SimulationModules.Enums import TypeOfField, AgentRequestAnswer
from typing import List

class InterfaceEnvMpcMapper(ABC):
    field_to_parking_spot_mapping: dict

    @abstractmethod
    def create_parking_spot_id_mapping(self, field_kinds: list):
        pass

    @abstractmethod
    def get_parking_spot_id_for_field_index(self, field_index: int):
        pass
    
    @abstractmethod
    def get_field_index_from_parking_spot_id(self, parking_spot_id: int):
        pass

    @abstractmethod
    def check_if_in_parking_spot_list(self, field_index: int):
        pass

    @abstractmethod
    def count_parking_spots(self):
        pass

    @abstractmethod
    def get_num_parking_spots(self):
        pass

    @abstractmethod
    def determine_num_chargers(self, type_of_field: List[TypeOfField]):
        pass

    @abstractmethod
    def get_num_chargers(self):
        pass

    @abstractmethod
    def determine_num_robots(self, robot_states: List[AgentRequestAnswer]):
        pass

    @abstractmethod
    def get_num_robots(self):
        pass

    @abstractmethod
    def create_charging_spot_list(self, type_of_field: List[TypeOfField]):
        pass

    @abstractmethod
    def get_charging_spot_by_index(self, index: int):
        pass

    @abstractmethod
    def get_charging_spot_index_from_field(self, charging_spot_index: int):
        pass
    