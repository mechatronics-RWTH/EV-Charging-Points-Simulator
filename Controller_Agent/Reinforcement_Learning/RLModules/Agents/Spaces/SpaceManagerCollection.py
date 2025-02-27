
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.CentralAgentSpace import CentralAgentSpace
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.GiniPowerAgentSpace import GiniPowerAgentSpace
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.GiniAgentSpace import GiniAgentSpace
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.TerminationAgentSpace import TerminationAgentSpace

from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig



class SpaceManagerCollection:
    central_agent_space: CentralAgentSpace
    gini_power_agent_space: GiniPowerAgentSpace
    gini_agent_space: GiniAgentSpace
    termination_agent_space: TerminationAgentSpace

    def __init__(self,
                 algo_config: RLAlgoConfig, 
                 help_managers: HelpManagers):
        self.central_agent_space = CentralAgentSpace(algo_config=algo_config, help_managers=help_managers)
        self.central_agent_space.define_observation_space()
        self.gini_power_agent_space = GiniPowerAgentSpace(algo_config=algo_config,
                                                        help_managers=help_managers)
        self.gini_power_agent_space.define_observation_space()
        self.gini_agent_space = GiniAgentSpace(algo_config=algo_config, help_managers=help_managers)
        self.gini_agent_space.define_observation_space()
        self.termination_agent_space = TerminationAgentSpace(algo_config=algo_config,help_managers=help_managers)
        self.termination_agent_space.define_observation_space()

    

