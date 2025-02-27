from dataclasses import dataclass
import yaml
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.Enums import AgentType
from SimulationEnvironment.EnvConfig import EnvConfig


@dataclass
class RLAlgoConfig:
    agent_id: AgentType  = 0
    rl_algorithm: int = 0
    share_vf_layers: bool = False 
    use_multi_termination_agents: bool = False
    use_multi_gini_agents: bool = True
    use_global_information: bool = False
    use_action_mask: bool = True
    amount_ginis: int = 0
    max_grid_power: float = 0
    max_gini_power: float = 0
    max_building_power: float = 0
    max_price: float = 0
    max_pv_power: float = 0
    area_size: int = 0
    max_energy_request: float = 0
    horizon: int = 96
    reward_cost_weight: float = 0.125
    gini_power_agent_active: bool = False
    termination_agent_active: bool = False
    logging_enabled: bool = False
    include_estimated_parking_time_in_observations: bool = True


    @staticmethod
    def load_from_yaml(yaml_file_path: str):
        with open(yaml_file_path, "r") as file:
            config = yaml.safe_load(file)

        algo_config = RLAlgoConfig(
            agent_id=AgentType(config.get("algorithm_structure", {}).get("value", 0)),
            rl_algorithm=config.get("rl_algorithm", {}).get("value", 0),
            share_vf_layers=config.get("use_share_vf_layers", False),
            use_multi_termination_agents=config.get("useMultiTerminationAgents", False),
            use_multi_gini_agents=config.get("useMultiGiniAgents", True),
            use_global_information=config.get("useGlobalInformation", False),
            use_action_mask=config.get("useActionMask", True),
            logging_enabled=config.get("loggingEnabled", False),
            include_estimated_parking_time_in_observations=config.get("includeEstimatedParkingTimeInObservations", True)
        )

        if algo_config.agent_id == AgentType(1) or algo_config.agent_id ==AgentType(3):
            algo_config.gini_power_agent_active = True
        if algo_config.agent_id == AgentType(2) or algo_config.agent_id == AgentType(3):
            algo_config.termination_agent_active = True
            #self.TerminationInstance = self.TerminationAgent
        return algo_config

    def load_from_env(self,
                      env_config: EnvConfig):
        self.amount_ginis = len(env_config.gini_starting_fields)
        self.area_size = 35

