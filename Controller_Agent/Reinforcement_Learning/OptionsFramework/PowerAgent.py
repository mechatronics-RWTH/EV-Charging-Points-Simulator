from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfacePowerAgent import InterfacePowerAgent
from enum import IntEnum
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.GiniPowerAgentSpace import GiniPowerAgentSpace
from SimulationModules.datatypes.EnergyType import EnergyType,EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType,PowerTypeUnit
from config.logger_config import get_module_logger
import copy

logger = get_module_logger(__name__)


class PowerAgent(InterfacePowerAgent):
    def __init__(self,
                 agent_id: str,
                 policy: tuple,
                 space_manager: GiniPowerAgentSpace,
                 observation_manager: ObservationManager
                 ):
        super().__init__()
        self.observation_manager: ObservationManager = observation_manager
        self.space_manager: GiniPowerAgentSpace = space_manager
        self.agent_id = agent_id
        self.index = None
        self.policy = policy
        self.reward = None
        self.action = None
        self.current_energy = None
        self.previous_energy = None
        self.step_cost = None
        self.previous_cost = 0
        self.assumed_selling_price = 0.5
        self.max_power = PowerType(50,PowerTypeUnit.KW)
        self.accepted_requests =[]

    def get_index(self):
        self.index = int(self.agent_id.split("_")[-1])

    def get_observation(self, option=1):
        obs = copy.deepcopy(self.observation_manager.observation)
        num_accepted_requests = len(self.accepted_requests)
        return self.space_manager.convert_observation(observation=obs,
                                               num_accepted_requests=num_accepted_requests,
                                               giniIndice = self.index) 

    def update_energy(self, current_energy_in_J: float):
        self.previous_energy = copy.deepcopy(self.current_energy)
        self.current_energy = EnergyType(current_energy_in_J,EnergyTypeUnit.J)

    def update_step_cost(self, step_cost_in_euro: float):
        self.step_cost = step_cost_in_euro - self.previous_cost
        self.previous_cost = step_cost_in_euro

    def set_reward(self):
        try:        
            assumed_selling_revenue = self.get_assumed_selling_revenue()
            self.reward = assumed_selling_revenue - self.step_cost
        except ValueError as e:
            logger.error(e)
            self.reward = 0

    def get_assumed_selling_revenue(self):
        if self.previous_energy is None:
            delta_energy_in_kwh = 0
        else:
            delta_energy_in_kwh= self.current_energy.get_in_kwh().value - self.previous_energy.get_in_kwh().value
        if delta_energy_in_kwh < 0:
            raise ValueError(f"Current energy ({self.current_energy}) should be larger then previous energy{self.previous_energy}, since reward only calculated during charging session")
        return delta_energy_in_kwh *self.assumed_selling_price

    def set_action(self, action):
        self.action = action[0]*self.max_power.get_in_w().value
        logger.debug(f"Agent {self.agent_id} has taken action {self.action} Watt")

    def get_action(self):
        #self.action= 0.5
        return self.action
    
    def get_reward(self):
        return self.reward
    
    def get_reward_dict(self):
        reward_dict = {self.agent_id: self.reward}
        logger.info(f"Agent {self.agent_id} has received reward {self.reward}")
        return reward_dict
    
    def reset_reward(self):
        self.reward = None

    def reset_action(self):
        self.action = None

    









