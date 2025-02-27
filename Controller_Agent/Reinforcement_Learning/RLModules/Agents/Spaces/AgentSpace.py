from gymnasium.spaces import Dict, Box
import numpy as np
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
import copy
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

class BaseAgentSpace(InterfaceAgentSpaces):

    def __init__(self, algo_config: RLAlgoConfig,
                 help_managers: HelpManagers):
        self.algo_config: RLAlgoConfig = algo_config
        self.observation_space = None
        self.observation_manager: ObservationManager = help_managers.observation_manager
        self.id_manager: IDManager = help_managers.id_manager

    def define_observation_space(self):  
        # Flattened observation space with test boundaries
        observation_elements = [
            1,  # num week in year
            1,  # num day in week
            1,  # num second in day
            1,  # grid_power
            1,  # building_power
            1,  # el_price
            1,  # pv_power
            self.algo_config.area_size,  # energy_requests
            self.algo_config.area_size,  # ev_energy
            self.algo_config.amount_ginis,  # field_indices_ginis
            self.algo_config.amount_ginis,  # gini_states
            self.algo_config.amount_ginis,  # soc_ginis
            self.algo_config.amount_ginis,  # gini_energy
            self.algo_config.amount_ginis,  # gini_requested_energy
            self.algo_config.area_size,  # charging_states
            1,  # requests_left
            1,  # current_field
            self.algo_config.horizon,  # price_table
            self.algo_config.horizon,  # pred_pv_power
        ]
        
        if self.algo_config.include_estimated_parking_time_in_observations:
            observation_elements.append(self.algo_config.area_size)  # estimated_parking_time

        flattened_low = np.full((sum(observation_elements)), -50, dtype=np.float32)  # Set all lower bounds to -50
        flattened_high = np.full(flattened_low.shape, 50, dtype=np.float32)  # Set all upper bounds to 50

        # Define observation space as a Box
        self.observation_space = Box(low=flattened_low, high=flattened_high, dtype=np.float32)

    def convert_observation(self,
                            observation, 
                            num_accepted_requests, 
                            field_index_of_request,):
        requests_left = np.array([num_accepted_requests], dtype=np.int8)  
        if field_index_of_request:
            current_field =  np.array([field_index_of_request], dtype=np.int32) 
        else:
            current_field =  np.array([0], dtype=np.int32) 
            Warning(f"Field index of request is not set: {field_index_of_request}")
        observation_raw = copy.deepcopy(observation)

        # Flatten observations
        flattened_observations = [
            observation_raw["num_week_in_year"],
            observation_raw["num_day_in_week"],
            observation_raw["num_seconds_in_day"],
            observation_raw["grid_power"],
            observation_raw["building_power"],
            observation_raw["el_price"],
            observation_raw["pv_power"],
            observation_raw["energy_requests"].flatten(),
            observation_raw["ev_energy"].flatten(),
            observation_raw["field_indices_ginis"].flatten(),
            observation_raw["gini_states"].flatten(),
            observation_raw["soc_ginis"].flatten(),
            observation_raw["gini_energy"].flatten(),
            observation_raw["gini_requested_energy"].flatten(),
            observation_raw["charging_states"].flatten(),
            requests_left.flatten(),
            current_field.flatten(),
            observation_raw["price_table"].flatten(),
            observation_raw["pred_pv_power"].flatten(),
        ]

        if self.algo_config.include_estimated_parking_time_in_observations:
            flattened_observations.append(observation_raw["estimated_parking_time"].flatten())

        flattened_observations = np.concatenate(flattened_observations)

        # Bestimme den Schlüssel basierend auf current_field
        agent_key = f"central_agent_{int(current_field)}"
        self.id_manager.agent_ids.append(agent_key)
        self.id_manager.set_agent_ids()
        self.observation_manager.info = {agent_key: {"test": 1}}
        flattened_observations = np.array(flattened_observations, dtype=np.float32)
        
        # Erstelle das Ergebnis-Dictionary mit dem spezifischen Schlüssel und der formatierten Observation
        transformed_obs = {agent_key: flattened_observations}    
        return transformed_obs
    
class BaseGiniAgentSpace(BaseAgentSpace):
    
    def define_observation_space(self):
        observation_elements = [
            1, # num week in year
            1,  # num day in week
            1,  # num second in day
            1,  # grid_power
            1,  # building_power
            1,  # el_price
            1,  # pv_power
            self.algo_config.area_size,  # energy_requests
            self.algo_config.area_size,  # ev_energy
            self.algo_config.amount_ginis,  # field_indices_ginis
            self.algo_config.amount_ginis,  # gini_states
            self.algo_config.amount_ginis,  # soc_ginis
            self.algo_config.amount_ginis,  # gini_energy
            self.algo_config.amount_ginis,  # gini_requested_energy
            self.algo_config.area_size,  # charging_states
            1,  # requests_left
            self.algo_config.horizon,  # price_table
            self.algo_config.horizon,  # pred_pv_power
        ]
        
        if self.algo_config.include_estimated_parking_time_in_observations:
            observation_elements.append(self.algo_config.area_size)  # estimated_parking_time
        
        observation_space_flat = Box(
            low=np.full((sum(observation_elements) + 3), -50, dtype=np.float32),  # Set all lower bounds to -50
            high=np.full((sum(observation_elements) + 3), 50, dtype=np.float32),  # Set all upper bounds to 50
            dtype=np.float32
        )
        
        self.observation_space = observation_space_flat

    def convert_observation(self, global_observation, giniIndice, Mask, accepted_requests, agent_prefix):
        logger.info(f"Mask: {Mask}, giniIndice: {giniIndice}, accepted_requests: {accepted_requests}")
        observation_raw = copy.deepcopy(global_observation)
        
        if observation_raw["soc_ginis"][giniIndice] == 0:
            Mask[2] = 0
        
        requests_left = np.array([len(accepted_requests)], dtype=np.int8)  
        agent_key = f"{agent_prefix}_{giniIndice}"

        if not self.algo_config.use_global_information:
            keys_to_zero_out = ["field_indices_ginis", "gini_states", "gini_requested_energy"]
            for key in keys_to_zero_out:
                array = observation_raw[key]
                for i in range(self.algo_config.amount_ginis):
                    if i != giniIndice:
                        array[i] = 0
                observation_raw[key] = array

        def flatten_observations(obs_dict):
            try:
                return np.concatenate([np.array(obs_dict[key], dtype=np.float32) for key in obs_dict.keys()])
            except Exception as e:
                raise RuntimeError(f"Error while flattening observations: {e}")

        obs_dict = {
            "num_week_in_year": observation_raw["num_week_in_year"],
            "num_day_in_week": observation_raw["num_day_in_week"],
            "num_seconds_in_day": observation_raw["num_seconds_in_day"],
            "grid_power": observation_raw["grid_power"],
            "building_power": observation_raw["building_power"],
            "el_price": observation_raw["el_price"],
            "pv_power": observation_raw["pv_power"],
            "energy_requests": observation_raw["energy_requests"],
            "ev_energy": observation_raw["ev_energy"],
            "field_indices_ginis": observation_raw["field_indices_ginis"],
            "gini_states": observation_raw["gini_states"],
            "soc_ginis": observation_raw["soc_ginis"],
            "gini_energy": observation_raw["gini_energy"],
            "gini_requested_energy": observation_raw["gini_requested_energy"],
            "charging_states": observation_raw["charging_states"],
            "requests_left": requests_left,
            "price_table": observation_raw["price_table"],
            "pred_pv_power": observation_raw["pred_pv_power"],
        }
        
        if self.algo_config.include_estimated_parking_time_in_observations:
            obs_dict["estimated_parking_time"] = observation_raw["estimated_parking_time"]

        flattened_observations = flatten_observations(obs_dict)
        flattened_observations = np.concatenate([flattened_observations, Mask])

        transformed_obs = {agent_key: flattened_observations}
        self.observation_manager.info = {agent_key: {}}

        return transformed_obs
