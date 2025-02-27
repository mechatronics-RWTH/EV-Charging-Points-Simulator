from ray.tune.schedulers import ASHAScheduler
from ray import tune
from ray.tune import PlacementGroupFactory
from ray.tune.search.basic_variant import BasicVariantGenerator
from ray.air import session  # Import session for reporting metrics
from ray.air.integrations.wandb import WandbLoggerCallback
from ray import air
from ray.tune.search.bayesopt import BayesOptSearch
from ray.rllib.algorithms.callbacks import DefaultCallbacks
from ray.tune.search.optuna import OptunaSearch
import os
import json
import yaml 
from gymnasium.spaces import Discrete, Box
AMOUNTGINIS = -1

class AlgorithmusTuner():
    def __init__(self):
        pass

    def tuneHyperParam(self, algo):
        global AMOUNTGINIS
        self.defineTuner(algo)
        AMOUNTGINIS = self.AMOUNTGINIS = algo.giniAmount
        self.algo = algo
        scheduler = ASHAScheduler(metric="mean_reward", mode="max") 
        paramset = self.load_optimization_parameters(algo)
        tuner = tune.Tuner(
            self.trainable_with_resources,
            tune_config=tune.TuneConfig(
                search_alg=self.optimizer,
                #scheduler=scheduler,
                metric = "mean_reward",
                mode="max",
                num_samples=self.numSamples,  # Anzahl der Kombinationen
                #.resources(num_gpus=1, num_gpus_per_worker=0)  # Keine GPUs verwenden
            ),
            run_config=air.RunConfig(
                callbacks=[
                    WandbLoggerCallback(
                        project="Tuner",  # Replace with your Wandb project name
                        log_config=True         # Log the config parameters as well
                    )
                ]
            ),
            param_space=paramset
        )
        tuner.fit()

    def defineTuner(self, algo):
        RewardStorage.reset()
        def trainable(config):
            algo = self.algo
            # Konfiguriere die Umgebung
            policies = {}
            # Erstelle dynamisch Policies für alle Gini-Agenten
            for i in range(self.AMOUNTGINIS):
                policy_config = {}

                # Füge nur die Parameter hinzu, die in der Config definiert sind
            # Übernimm die Parameter aus der Konfiguration
                if "learning_rate" in config:
                    policy_config["lr"] = config.get("learning_rate")

                if "discount_factor" in config:
                    policy_config["gamma"] = config.get("discount_factor")

                if "entropy_coeff" in config:  # Entropy Regularization Coefficient
                    policy_config["entropy_coeff"] = config.get("entropy_coeff")

                if "clip_param" in config:  # PPO Clipping Parameter
                    policy_config["clip_param"] = config.get("clip_param")

                if "lambda" in config:  # GAE Lambda
                    policy_config["lambda"] = config.get("lambda")

                if "train_batch_size" in config:  # Training Batch Size
                    policy_config["train_batch_size"] = config.get("train_batch_size")

                if "vf_loss_coeff" in config:  # Value Function Loss Coefficient
                    policy_config["vf_loss_coeff"] = config.get("vf_loss_coeff")

                if "kl_target" in config:  # KL Divergence Target
                    policy_config["kl_target"] = config.get("kl_target")


                # Statische Parameter
                if algo.useActionMask:
                    policy_config.update({
                        #"vf_share_layers": self.share_vf_layers,
                        #"normalize_rewards": self.normalize_rewards,
                        #"grad_clip": self.grad_clip,
                        "model": {"custom_model": "ActionMaskModel"}
                    })

                # Füge die Policy zur Liste hinzu
                policies[f"gini{i}_policy"] = (
                    None,
                    algo.giniObservationSpace,
                    Discrete(3),
                    policy_config,
                )

            # Füge die zentrale Policy hinzu
            central_policy_config = {
                #"vf_share_layers": self.share_vf_layers,
                #"normalize_rewards": self.normalize_rewards,
                #"grad_clip": self.grad_clip,
            }
            policies["central_policy"] = (
                None,
                algo.centralObservationSpace,
                Discrete(2),
                central_policy_config,
            )
            algo_config = (algo.RLconfig.environment(env="Environment", env_config=algo.gym_config, disable_env_checking=True)
            .framework("torch")
            .rollouts(num_rollout_workers=1, rollout_fragment_length="auto")
            .callbacks(CustomMetricsCallback)
            .resources(num_gpus=1)
            .multi_agent(
                policies=policies,
                policy_mapping_fn=algo.config["policy_mapping_fn"],
            ))
            algo = algo_config.build()
            for _ in range(self.numIterations):
                result = algo.train()
                gini_rewards = RewardStorage.load_rewards()
                gini_avg_rewards = [sum(rewards) / len(rewards) if len(rewards) > 0 else 0 for rewards in gini_rewards]
                mean_reward = sum(gini_avg_rewards)  # Gesamter Durchschnitt aller Ginis
                metrics = {f"gini_agent_{i}_avg_reward": avg_reward for i, avg_reward in enumerate(gini_avg_rewards)}
                metrics["mean_reward"] = mean_reward
                session.report({"mean_reward": mean_reward})
                RewardStorage.reset()
            algo.stop()
        resources = tune.PlacementGroupFactory(
            [
                {"CPU": 1, "GPU": 1},  # Resources for the main trial
                {"CPU": 1},            # Resources for rollout worker 1
                {"CPU": 1},             # Resources for rollout worker 2
                {"CPU": 1},             # Resources for rollout worker 2
                {"CPU": 1},             # Resources for rollout worker 2
                {"CPU": 1},             # Resources for rollout worker 2
            ]
        )
        # Wrap the trainable function with the specified resources
        self.trainable_with_resources = tune.with_resources(trainable, resources)


    def load_optimization_parameters(self, algo, config_file="RLconfig_hyperparameter.yaml"):
        # Lade die Konfigurationsdatei
        with open(config_file, "r") as file:
            config_HP = yaml.safe_load(file)

        self.numIterations = config_HP.get("num_iterations", {}).get("value", 3)
        self.numSamples = config_HP.get("num_samples", {}).get("value", 3)

        # Wähle den passenden Parameter-Block basierend auf der Optimierungsstrategie
        if algo.hyperparameter_optimization == 2:  # Bayesian Optimization
            optimization_params = config_HP.get("BayesianOptimizationParameters", {})
            self.optimizer = BayesOptSearch(metric="mean_reward", mode="max")
        elif algo.hyperparameter_optimization in [0, 1]:  # Grid oder Random Search
            optimization_params = config_HP.get("GridRandomSearchParameters", {})
            self.optimizer = BasicVariantGenerator()
        else:
            raise ValueError("Invalid hyperparameter optimization strategy specified!")

        # Filtere nur Parameter, die "optimize: true" sind
        filtered_params = {
            param: settings
            for param, settings in optimization_params.items()
            if settings.get("optimize", False)
        }

        # Debug-Ausgabe: Zeige die gefilterten Parameter
        print(f"Filtered parameters for optimization: {filtered_params}")

        # Erstelle das Parameter-Set für Ray Tune
        tune_param_space = {}
        for param, settings in filtered_params.items():
            param_type = settings.get("type", "uniform")
            param_range = settings.get("range", [])

            # Sicherstellen, dass der Wertebereich korrekt ist
            if not isinstance(param_range, list) or len(param_range) != 2:
                raise ValueError(f"Invalid range for parameter {param}: {param_range}")

            # Konvertiere Bereichswerte in floats, falls sie als Strings angegeben wurden
            lower, upper = float(param_range[0]), float(param_range[1])

            # Je nach Typ den Parameter hinzufügen
            if param_type == "loguniform":
                tune_param_space[param] = tune.loguniform(lower, upper)
            elif param_type == "uniform":
                tune_param_space[param] = tune.uniform(lower, upper)
            elif param_type == "grid":
                tune_param_space[param] = tune.grid_search(param_range)
            else:
                raise ValueError(f"Unknown parameter type for {param}: {param_type}")

        # Debug-Ausgabe: Zeige das endgültige Parameter-Set
        print(f"Tune parameter space: {tune_param_space}")

        return tune_param_space

class CustomMetricsCallback(DefaultCallbacks):
    def on_episode_end(self, *, worker, base_env, policies, episode, **kwargs):
        global AMOUNTGINIS
        # Lade vorhandene Rewards
        gini_rewards = RewardStorage.load_rewards()

        # Rewards initialisieren, falls noch nicht vorhanden
        if len(gini_rewards) < AMOUNTGINIS:
            gini_rewards = [[] for _ in range(AMOUNTGINIS)]

        # Neue Rewards aus der Episode extrahieren
        for agent_id_policy, agent_reward in episode.agent_rewards.items():
            agent_id, policy_id = agent_id_policy
            # Dynamische Verarbeitung der Agenten (z. B. "gini_agent_0", "gini_agent_1", ...)
            if agent_id.startswith("gini_agent_"):
                # Hole die Agenten-ID-Nummer, z. B. "gini_agent_0" -> 0
                gini_index = int(agent_id.split("_")[2])  # Extrahiere die Nummer nach "gini_agent_"
                if gini_index < AMOUNTGINIS:
                    gini_rewards[gini_index].append(agent_reward)

        # Rewards speichern
        RewardStorage.save_rewards(gini_rewards)

        #print(f"Updated rewards: {gini_rewards}")

class RewardStorage:

    FILE_PATH = os.path.join(os.getcwd(), "RLModules", "Logs", "temporary_rewards.json")

    @staticmethod
    def save_rewards(gini_rewards):
        global AMOUNTGINIS
        """Speichert die Rewards für alle Ginis direkt in der JSON-Datei."""
        # Erstelle ein Dictionary, das die Rewards für jede Gini speichert
        rewards_dict = {f"gini_agent_{i}_rewards": gini_rewards[i] for i in range(len(gini_rewards))}

        # Schreibe die Rewards in die Datei
        with open(RewardStorage.FILE_PATH, "w") as f:
            json.dump(rewards_dict, f)
        print("Rewards saved to file.")

    @staticmethod
    def load_rewards():
        global AMOUNTGINIS
        """Lädt die Rewards für alle Ginis direkt aus der JSON-Datei."""
        try:
            with open(RewardStorage.FILE_PATH, "r") as f:
                data = json.load(f)

                # Lade die Rewards für jede Gini
                gini_rewards = [data.get(f"gini_agent_{i}_rewards", []) for i in range(AMOUNTGINIS)]
                print("Rewards loaded from file.")
                return gini_rewards
        except FileNotFoundError:
            print("No rewards file found. Returning empty lists.")
            return [[] for _ in range(AMOUNTGINIS)]  # Leere Listen für alle Ginis zurückgeben

    @staticmethod
    def reset():
        global AMOUNTGINIS
        """Setzt die Rewards in der Datei zurück (leert sie für alle Ginis)."""
        # Erstelle ein leeres Dictionary für alle Ginis
        empty_rewards = {f"gini_agent_{i}_rewards": [] for i in range(AMOUNTGINIS)}

        # Schreibe die leeren Rewards in die Datei
        with open(RewardStorage.FILE_PATH, "w") as f:
            json.dump(empty_rewards, f)
        print("Rewards file has been reset.")
