from typing import List
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper
from abc import ABC, abstractmethod
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel

class InterfaceModelEnvTranslator:
    action: dict 
    model: InterfaceOptimizationModel
    charging_spot_list: List[int]
    gini_field_indices: List[int]
    type_of_field: List[int]
    env_mpc_mapper: InterfaceEnvMpcMapper

    @abstractmethod
    def update_translation(self,action: dict):
        pass

    @abstractmethod
    def initialize_observation(self, raw_obs: dict):
        pass

    @abstractmethod
    def initialize_action(self, action_raw_base: dict):
        pass

    @abstractmethod
    def translate_request_gini_field_from_model_to_action(self):
        pass

    @abstractmethod
    def translate_request_gini_power_from_model_to_action(self):
        pass

    @abstractmethod
    def translate_target_charging_power_from_model_to_action(self):
        pass
    
    @abstractmethod
    def translate_target_stat_battery_charging_power_from_model_to_action(self):
        pass

    @abstractmethod
    def get_number_parking_fields(self):
        pass

    @abstractmethod
    def derive_important_fields(self):
        pass

    @abstractmethod
    def initialize_model(self, model: InterfaceOptimizationModel):
        pass

    @abstractmethod
    def move_gini_to_charging_spot(self):
        pass

    @abstractmethod
    def move_gini_to_EV(self):
        pass

    @abstractmethod
    def provide_env_mpc_mapper(self, env_mpc_mapper: InterfaceEnvMpcMapper):
        pass
    
    @abstractmethod
    def update_observation(self, raw_obs: dict):
        pass
    
    @abstractmethod
    def update_e_obs_ev(self):
        pass
    
    @abstractmethod
    def update_e_obs_robot(self):
        pass
    
    @abstractmethod
    def set_model_parameters_from_config(self, envConfigPath: str):
        pass

    @abstractmethod
    def get_translated_action(self):
        pass

    @abstractmethod
    def update_optimization_model_based_on_observation(self, raw_obs: dict):
        pass

    @abstractmethod
    def create_action_based_on_model_output(self):
        pass
    