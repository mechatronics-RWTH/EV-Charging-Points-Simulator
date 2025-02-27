

from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARLEnvironment import HMARLEnvironment

from Controller_Agent.Reinforcement_Learning.TestRlAlgorithm.TrainedRlAgent import TrainedRlAgent
from config.logger_config import get_module_logger
from Controller_Agent.Reinforcement_Learning.TestRlAlgorithm.TestRlAgent import TestRlAgent, TestRl_HMARL

logger = get_module_logger(__name__)

RENDER = False#config['RENDER']
SAVE_JSON = True# config['SAVE_JSON']
OUTPUT_GRAPHS = True#config['OUTPUT_GRAPHS']
FOLDERPATH = None #config['FOLDERPATH']
LOOP = False #config['LOOP']

USE_HMARL_ENV = False

trained_agent_path = "Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250209_152944/checkpoint_000250"
env_config_path = r"config\env_config\comparison_fall_3MCR.json"#"config/env_config/Benchmark/comparison_fall.json"

list_of_agent_checkpoints = ["Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250209_152944/checkpoint_0000064" ]

if __name__ == "__main__":
    if USE_HMARL_ENV:
        test_rl_agent = TestRl_HMARL(env_config_path=env_config_path,
                                    save_json_active=SAVE_JSON,
                                    output_graph=OUTPUT_GRAPHS)
    else:
        test_rl_agent = TestRlAgent(env_config_path=env_config_path,
                                    save_json_active=SAVE_JSON,
                                    output_graph=OUTPUT_GRAPHS)
    test_rl_agent.run_with_multiple_agents(list_of_agent_checkpoints= [r"Controller_Agent\Reinforcement_Learning\trained_models\checkpoint_20250212_223601\checkpoint_000084",])#"Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250214_105702/checkpoint_000054"])# ="Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250212_223601")
