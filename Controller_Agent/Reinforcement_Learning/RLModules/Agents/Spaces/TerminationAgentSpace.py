from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.AgentSpace import BaseAgentSpace
import numpy as np
from gymnasium.spaces import Dict, Box

class TerminationAgentSpace(BaseAgentSpace):
    def define_observation_space(self):


        # Flattened observation space with test boundaries
        flattened_low = np.full((sum([
            1,  # grid_power
            1,  # building_power
            1,  # el_price
            1,  # pv_power
            self.algo_config.area_size,  # energy_requests
            self.algo_config.area_size,  # ev_energy
            self.algo_config.area_size,  # charging_states
            self.algo_config.amount_ginis,  # field_indices_ginis
            self.algo_config.amount_ginis,  # gini_states
            self.algo_config.amount_ginis,  # soc_ginis
            self.algo_config.amount_ginis,  # gini_energy
            self.algo_config.amount_ginis,  # gini_requested_energy            
            1,  # current_gini
            self.algo_config.amount_ginis  # giniOption (flattened as MultiDiscrete values)
        ])), -50, dtype=np.float32)  # Set all lower bounds to -50

        flattened_high = np.full(flattened_low.shape, 50, dtype=np.float32)  # Set all upper bounds to 50
        #print(f"{self} observation_space: {len(flattened_low)}")
        # Define observation space as a Box
        self.observation_space= Box(low=flattened_low, high=flattened_high, dtype=np.float32)

    def convert_observation(self, observation, 
                            giniOption, 
                            giniIndice):
        giniOption_list =[0]*self.algo_config.amount_ginis
        giniOption_list[giniOption] = 1
        observation_raw = observation
        agent_key = f"termination_agent_{giniIndice}"
        giniIndice_array = np.array([giniIndice], dtype=np.int32)
        giniOption_array = np.array(giniOption_list, dtype=np.int32)

        # Hilfsfunktion, um Werte außerhalb des giniIndice auf 0 zu setzen
        def filter_by_gini_index(array, giniIndice):
            filtered_array = np.zeros_like(array)
            filtered_array[giniIndice] = array[giniIndice]
            return filtered_array

        # Schlüssel, die gefiltert werden sollen
        keys_to_filter = [
            "field_indices_ginis",
            "gini_states",
            "soc_ginis",
            "gini_energy",
            "gini_requested_energy"
        ]

        # Gefilterte Beobachtungen erzeugen
        filtered_observations = []
        for key in keys_to_filter:
            if not self.algo_config.use_global_information:  # Nur filtern, wenn `self.globalInformation` False ist
                filtered_observations.append(filter_by_gini_index(observation_raw[key], giniIndice))
            else:
                filtered_observations.append(observation_raw[key])  # Unveränderte Werte hinzufügen

        # Andere Beobachtungswerte flach hinzufügen
        flattened_observations = np.concatenate([
            observation_raw["grid_power"],
            observation_raw["building_power"],
            observation_raw["el_price"],
            observation_raw["pv_power"],
            observation_raw["energy_requests"].flatten(),
            observation_raw["ev_energy"].flatten(),
            observation_raw["charging_states"].flatten(),
            *filtered_observations,  # Die gefilterten oder originalen Beobachtungen einfügen
            giniIndice_array.flatten(),
            giniOption_array.flatten()
        ])

        # Ergebnis erstellen
        flattened_observations = np.array(flattened_observations, dtype=np.float32)
        transformed_obs = {agent_key: flattened_observations}
        print(f"transformed_obs length: {len(transformed_obs[agent_key])}")
        return transformed_obs



#endregion   