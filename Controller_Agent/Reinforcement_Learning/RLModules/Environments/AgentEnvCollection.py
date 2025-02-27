from Controller_Agent.Reinforcement_Learning.RLModules.Environments.CentralAgentEnv import CentralAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.PowerAgentEnv import PowerAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.TerminationAgentEnv import TerminationAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.GiniAgentEnv import GiniAgentEnv

from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.SpaceManagerCollection import SpaceManagerCollection
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.AgentStructure import AgentStructure
from typing import List



class AgentEnvCollection:

    central_agent_env: CentralAgentEnv
    power_agent_env: PowerAgentEnv
    termination_agent_env: TerminationAgentEnv
    gini_agent_env: GiniAgentEnv
    agent_structure: AgentStructure

    def __init__(self, algo_config, 
                 help_managers: HelpManagers,
                 space_manager_collection: SpaceManagerCollection):
        
        self.agent_structure = AgentStructure(algo_config=algo_config,
                                            help_managers=help_managers,
                                            space_manager_collection=space_manager_collection)
        self.agent_structure.create_agent_structure_from_config()
        central_agents = [agent for agent in self.agent_structure.agent_list if agent.agent_id.startswith("central_agent")]
        assert len(central_agents) == algo_config.area_size
        self.central_agent_env = CentralAgentEnv(algo_config=algo_config,
                                                 observation_manager=help_managers.observation_manager,
                                                 space_manager=space_manager_collection.central_agent_space, 
                                                 agents= central_agents)
        self.central_agent_env.create_agent_mapping()
        self.power_agent_env = PowerAgentEnv(algo_config=algo_config,
                                             observation_manager=help_managers.observation_manager,
                                             space_manager=space_manager_collection.gini_power_agent_space,
                                             id_manager=help_managers.id_manager,                                             
                                             )

        self.termination_agent_env = TerminationAgentEnv(algo_config=algo_config,
                                                         observation_manager=help_managers.observation_manager,
                                                         id_manager=help_managers.id_manager,
                                                         space_manager=space_manager_collection.termination_agent_space)
        gini_agents = [agent for agent in self.agent_structure.agent_list if agent.agent_id.startswith("gini_agent")]
        self.gini_agent_env = GiniAgentEnv(algo_config=algo_config,
                                           observation_manager=help_managers.observation_manager,                                           
                                           space_manager=space_manager_collection.gini_agent_space,
                                           agents= gini_agents)
        self.gini_agent_env.create_agent_mapping()