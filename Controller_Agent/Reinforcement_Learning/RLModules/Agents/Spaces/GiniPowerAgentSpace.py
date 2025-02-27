from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.AgentSpace import BaseAgentSpace
from gymnasium.spaces import Dict, Box
import numpy as np

class GiniPowerAgentSpace(BaseAgentSpace):
            
    def define_observation_space(self):
        # Flattened observation space with test boundaries
        flattened_low = np.full((sum([
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
            1,  # current_field
            self.algo_config.horizon,  # price_table
            self.algo_config.horizon,  # pred_pv_power
            self.algo_config.area_size  # estimated_parking_time
        ])), -50, dtype=np.float32)  # Set all lower bounds to -50

        flattened_high = np.full(flattened_low.shape, 50, dtype=np.float32)  # Set all upper bounds to 50

        # Define observation space as a Box
        self.observation_space= Box(low=flattened_low, high=flattened_high, dtype=np.float32)

    def convert_observation(self,
                            observation,
                            num_accepted_requests,
                            giniIndice):
        requests_left = np.array([num_accepted_requests], dtype=np.int8)

        giniIndice = np.array([giniIndice], dtype=np.int8)


        observation_raw = observation

        # Funktion zum Filtern von Beobachtungen basierend auf giniIndice
        def filter_by_gini_index(array, giniIndice):
            filtered_array = np.zeros_like(array)
            filtered_array[giniIndice] = array[giniIndice]
            return filtered_array

        # Schlüssel, die gefiltert werden sollen, wenn self.globalInformation False ist
        keys_to_filter = [
            "field_indices_ginis",
            "gini_states",
            "soc_ginis",
            "gini_energy",
            "gini_requested_energy"
        ]

        # Beobachtungen filtern, wenn self.globalInformation False ist
        filtered_observations = []
        for key in keys_to_filter:
            if not self.algo_config.use_global_information:  # Nur filtern, wenn self.globalInformation False ist
                filtered_observations.append(filter_by_gini_index(observation_raw[key], giniIndice))
            else:
                filtered_observations.append(observation_raw[key])  # Unveränderte Werte hinzufügen

        # Flatten observations
        flattened_observations = np.concatenate([
            observation_raw["num_week_in_year"],
            observation_raw["num_day_in_week"],
            observation_raw["num_seconds_in_day"],
            observation_raw["grid_power"],
            observation_raw["building_power"],
            observation_raw["el_price"],
            observation_raw["pv_power"],
            observation_raw["energy_requests"].flatten(),
            observation_raw["ev_energy"].flatten(),
            *filtered_observations,  # Die gefilterten oder originalen Beobachtungen einfügen
            observation_raw["charging_states"].flatten(),
            requests_left.flatten(),
            giniIndice.flatten(),
            observation_raw["price_table"].flatten(),
            observation_raw["pred_pv_power"].flatten(),
            observation_raw["estimated_parking_time"].flatten()
        ])

        # Determine the agent key based on giniIndice
        # if giniOption[int(giniIndice)] == 2:
        agent_key = f"gini_power_agent_{int(giniIndice)}"
        # else:
        #     agent_key = f"cs_power_agent_{int(giniIndice)}"

        self.id_manager.agent_ids.append(agent_key)
        self.id_manager.set_agent_ids()
        self.observation_manager.info = {agent_key: {}}
        flattened_observations = np.array(flattened_observations, dtype=np.float32)

        # Create the result dictionary with the specific key and formatted observation
        transformed_obs = {agent_key: flattened_observations}
        return transformed_obs

