from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Reward import RewardManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Requests import RequestManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.Logging import LoggingManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Terminations import RLTerminationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Actions import ActionManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Terminations import EpisodeTerminationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.CentralAgentEnv import CentralAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.TerminationAgentEnv import TerminationAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.GiniAgentEnv import GiniAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.PowerAgentEnv import PowerAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.AgentEnvCollection import AgentEnvCollection
from typing import List



class HMARL_EnvConfig:

    def __init__(self, 
                 env_config: EnvConfig,
                 help_managers: HelpManagers,
                 env_collection: AgentEnvCollection,
                 agent_name_list: List[str] = None):
        self.env_config = env_config
        self.observation_manager: ObservationManager = help_managers.observation_manager
        self.reward_manager: RewardManager = help_managers.reward_manager
        self.id_manager: IDManager = help_managers.id_manager
        #self.termination_manager: RLTerminationManager = help_managers.termination_manager
        #self.request_manager: RequestManager = help_managers.request_manager
        self.central_agent_env: CentralAgentEnv = env_collection.central_agent_env
        self.termination_agent_env: TerminationAgentEnv = env_collection.termination_agent_env
        self.gini_agent_env: GiniAgentEnv = env_collection.gini_agent_env
        self.gini_power_agent_env:PowerAgentEnv = env_collection.power_agent_env
        #self.action_manager: ActionManager = help_managers.action_manager
        #self.episode_termination_manager: EpisodeTerminationManager = help_managers.episode_termination_manager
        self.logging_manager: LoggingManager = help_managers.logging_manager
        self.agent_list = agent_name_list

    def to_dict(self):
        return {
            "env_config": self.env_config,
            "observation_manager": self.observation_manager,
            "reward_manager": self.reward_manager,
            "id_manager": self.id_manager,
            "central_agent_env": self.central_agent_env,
            "termination_agent_env": self.termination_agent_env,
            "gini_agent_env": self.gini_agent_env,
            "gini_power_agent_env": self.gini_power_agent_env,
            "agent_list": self.agent_list
        }
        