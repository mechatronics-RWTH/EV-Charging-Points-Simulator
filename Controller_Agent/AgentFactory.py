
from typing import Union

from Controller_Agent.InterfaceAgent import InterfaceAgent
from Controller_Agent.Rule_based.RuleBasedAgent import RuleBasedAgent_One
from Controller_Agent.Rule_based.RuleBasedNoGini import RuleBasedAgent_NoGini
from Controller_Agent.Rule_based.RuleBasedNoGiniStatStorage import RuleBasedAgentStatStorage
from SimulationModules.datatypes.PowerType import PowerType


class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str = "rule_based_agent_one",
                     P_grid_max: Union[None, PowerType] = None) -> InterfaceAgent:

        if agent_type == "rule_based_agent_one":
            return RuleBasedAgent_One(P_grid_max=P_grid_max)
        elif agent_type == "rule_based_agent_no_gini":
            return RuleBasedAgent_NoGini(P_grid_max=P_grid_max)
        elif agent_type == "rule_based_stat_storage":
            return RuleBasedAgentStatStorage(P_grid_max=P_grid_max)
        else:       
            raise ValueError("Invalid agent type")
