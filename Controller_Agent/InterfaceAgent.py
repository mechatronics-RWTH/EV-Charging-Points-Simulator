from abc import ABC, abstractmethod

from gymnasium.spaces import Dict

from SimulationModules.Enums import TypeOfField

def ensure_positive(value):
        if value < 0:
                return value*(-1)
        return value

class InterfaceAgent(ABC):

    @abstractmethod
    def calculate_action(self, raw_obs: Dict):
        pass

    # @abstractmethod
    # def initialize_observation(self, raw_obs: Dict):
    #     pass

    # @abstractmethod
    # def initialize_action(self, action_raw_base: Dict):
    #     pass


class TemplateAgent(InterfaceAgent):

    def __init__(self):
        self.initialized = False
        self.occupied_charging_spot_index = []


    def calculate_action(self, raw_obs: Dict, action_raw_base: Dict):
        """
        this method calculates a very simple agents 
        action, whose rewards can be compared to
        a learning agent
        """
        if not self.initialized:
            self.initialize_observation_once(raw_obs)
            self._initialize_stationary_battery_controller()                
        self.initialize_action(action_raw_base)
        self.initialize_observation(raw_obs)                
        self.handle_unanswered_requests()
        self.determine_occupied_charging_spots()
        self.request_moving_ginis()
        self.calculate_action_stationary_battery_controller(raw_obs)
        self.limit_charging_power_if_required(raw_obs)
        return self.action
    
    def initialize_observation_once(self, raw_obs: Dict):
        self.type_of_field = raw_obs["field_kinds"]
        self.charging_spot_list = [j for j,field_kind in enumerate(self.type_of_field) if field_kind==TypeOfField.GiniChargingSpot.value]
        self.initialized = True

    
    def initialize_action(self, action_raw_base: Dict):
        self.action=action_raw_base

    def initialize_observation(self, raw_obs: Dict): 
        self.user_request = raw_obs["user_requests"]
        self.gini_field_indices = raw_obs["field_indices_ginis"]        
        self.gini_soc = raw_obs["soc_ginis"]
        self.charging_soc_state = raw_obs["charging_states"]        
        self.gini_states = raw_obs["gini_states"]

    def determine_occupied_charging_spots(self):
        self.occupied_charging_spot_index= []
        for charging_spot_index in self.charging_spot_list:
            if self.is_spot_occupied(charging_spot_index):
                self.occupied_charging_spot_index.append(charging_spot_index)



    @abstractmethod
    def handle_unanswered_requests(self):
        pass

    @abstractmethod
    def request_moving_ginis(self):
        pass

    @abstractmethod
    def limit_charging_power_if_required(self, raw_obs: Dict):
        pass

    def _initialize_stationary_battery_controller(self):
        pass

    def is_spot_occupied(self,charging_spot_index: int)-> bool:
        return self.is_occupied_by_gini(charging_spot_index) or self.is_vehicle_at_charging_spot(charging_spot_index)

    def is_occupied_by_gini(self, charging_spot_index)-> bool:
        return False

    def is_vehicle_at_charging_spot(self, charging_spot_index: int)-> bool:
        return self.charging_soc_state[charging_spot_index] is not None 
    
    def calculate_action_stationary_battery_controller(self, raw_obs: Dict):
        pass