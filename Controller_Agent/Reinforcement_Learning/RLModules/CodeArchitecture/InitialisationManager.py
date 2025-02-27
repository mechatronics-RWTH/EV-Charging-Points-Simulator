import os
import yaml
from ray.tune.registry import register_env
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARLEnvironment import HMARLEnvironment
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.ActionMask import ActionMaskedModel
import shutil

class AlgorithmusInitialiser:
    def __init__(self, algo):
        self.algo = algo

    def initialise1(self):
        self.initYAML()
        self.initLogPaths()

    def initialise2(self):
        self.defineEnvironmentParameters()
        self.initTrainingsLog()
        self.executeRegistrations()

    def initYAML(self):
        with open("RLconfig.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.algo.AgentID = config.get("algorithm_structure", {}).get("value", 0)
        self.algo.agentMode = config.get("agent_mode", {}).get("value", 0)
        self.algo.save_model = config.get("save_model", False)
        self.algo.config_path = config.get("config_path", "config/env_config/env_config_Milan_Dev.json")
        self.algo.rl_algorithm = config.get("rl_algorithm", {}).get("value", 0)
        self.algo.share_vf_layers = config.get("use_share_vf_layers", False)
        self.algo.normalize_rewards = config.get("normalize_rewards", False)
        self.algo.hyperparameter_optimization = config.get("HyperparameterOptimization", {}).get("value", 0)
        self.algo.useMultiTerminationAgents = config.get("useMultiTerminationAgents", False)
        self.algo.useMultiGiniAgents = config.get("useMultiGiniAgents", True)

        if self.algo.agentMode == 1:
            self.algo.bench_season = config.get("BenchSzenario", {}).get("value", 0)
            if self.algo.bench_season == 0:
                self.algo.config_path = "config/env_config/Benchmark/comparison_fall.json"
            if self.algo.bench_season == 1:
                self.algo.config_path = "config/env_config/Benchmark/comparison_spring.json"
            if self.algo.bench_season == 2:
                self.algo.config_path = "config/env_config/Benchmark/comparison_summer.json"
            if self.algo.bench_season == 3:
                self.algo.config_path = "config/env_config/Benchmark/comparison_winter.json"


    def initLogPaths(self):
        current_working_dir = os.getcwd()
        self.algo.txt_file_path = os.path.join(current_working_dir, "RLModules", "Logs", "training_log.txt")
        self.algo.model_save_path = os.path.join(current_working_dir, "RLModules", "Logs", f"savedModel_{self.algo.AgentID}{self.algo.rl_algorithm}")
        os.makedirs(os.path.dirname(self.algo.txt_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.algo.model_save_path), exist_ok=True)
        if self.algo.agentMode == 0 and self.algo.save_model:
            self.clearOldModel(self.algo)

    def initTrainingsLog(self):
        os.makedirs(os.path.dirname(self.algo.txt_file_path), exist_ok=True)
        with open(self.algo.txt_file_path, 'w') as f:
            f.write('Training-Log initialized.\n')

    def executeRegistrations(self):
        register_env("Environment", lambda config: HMARLEnvironment(self.algo.gym_config))
        ModelCatalog.register_custom_model("ActionMaskModel", ActionMaskedModel)

    def defineEnvironmentParameters(self):
        self.algo.env = HMARLEnvironment(self.algo.gym_config)
        if self.algo.AgentID == 0:
            self.algo.centralObservationSpace, self.algo.giniObservationSpace = self.algo.env.SpaceCreator.defineObservationSpaces()
        elif self.algo.AgentID == 1:
            self.algo.centralObservationSpace, self.algo.giniObservationSpace, self.algo.giniPowerObservationSpace = self.algo.env.SpaceCreator.defineObservationSpaces()
        elif self.algo.AgentID == 2:
            self.algo.centralObservationSpace, self.algo.giniObservationSpace, self.algo.terminationObservationSpace = self.algo.env.SpaceCreator.defineObservationSpaces()
        elif self.algo.AgentID == 3:
            self.algo.centralObservationSpace, self.algo.giniObservationSpace, self.algo.terminationObservationSpace, self.algo.giniPowerObservationSpace = self.algo.env.SpaceCreator.defineObservationSpaces()
        self.algo.giniAmount = self.algo.env.raw_env.raw_env_space_manager.amount_ginis
        self.algo.useActionMask = self.algo.env.useActionMask
        if self.algo.useMultiGiniAgents:
            self.algo.amountGiniActor = self.algo.giniAmount
        else:
            self.algo.amountGiniActor = 1
        if self.algo.useMultiTerminationAgents:
            self.algo.amountTerminators = self.algo.giniAmount
        else:
            self.algo.amountTerminators = 1

    def clearOldModel(self, algo):
        if algo.save_model and os.path.exists(algo.model_save_path):
            for file_name in os.listdir(algo.model_save_path):
                file_path = os.path.join(algo.model_save_path, file_name)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path) 
                except Exception as e:
                    print(f"Error deleting: {file_path}: {e}")
