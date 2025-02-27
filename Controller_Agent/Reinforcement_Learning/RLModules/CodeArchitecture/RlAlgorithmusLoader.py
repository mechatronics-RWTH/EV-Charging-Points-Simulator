import os
from helpers.JSONSaver import JSONSaver
import time
from helpers.Plot_json_logs import plot_and_save_small
import shutil


class RlAlgorithmusLoader():
    def __init__(self):
        self.current_working_dir = os.getcwd()
        self.file_path = os.path.join(self.current_working_dir, "RLModules", "Logs", "bench_algos_noAM.txt")
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def bench_model(self, algo): #bench a trained agent by loading a model
        algo.readJson()
        # Finde den letzten Checkpoint im Ordner
        checkpoints = [f for f in os.listdir(algo.model_save_path) if f.startswith("checkpoint_")]
        checkpoints.sort()  # Sortiere nach Namen (z.B. checkpoint_0005, checkpoint_0010)
        last_checkpoint = os.path.join(algo.model_save_path, checkpoints[-1])  # Nimm den letzten Checkpoint
        algo.model_save_path=last_checkpoint
        self.trainer = algo.config.build()
        algo.logger.info("loading agent")
        model_save_path = os.path.join(self.current_working_dir, "RLModules", "Logs", f"savedModel_{algo.AgentID}{algo.rl_algorithm}")
        checkpoints = [f for f in os.listdir(model_save_path) if f.startswith("checkpoint_")]
        checkpoints.sort()
        self.selected_checkpoint = os.path.join(model_save_path, checkpoints[-1])
        try:
            self.trainer.restore(self.selected_checkpoint)
        except Exception as e:
            raise Exception(
                            "You are in the agent loading mode. The agent could not be restored. "
                            "Make sure you have trained an agent for at least 5 iterations (about 3 minutes). "
                            "The trainings mode can be set in the RLconfig file."
            ) from e
        self.doEnvironmentIteration(algo)

    def doEnvironmentIteration(self, algo):
        episode_rewards = []
        jsonsaver = JSONSaver()     
        state, _ = algo.env.reset()
        while algo.env.raw_env.time_manager.get_current_time() < algo.env.raw_env.time_manager.get_stop_time():
                actions = {}
                for agent_id, agent_obs in state.items():
                    policy_id = self.policy_mapping_fn(agent_id, algo)
                    actions[agent_id] = self.trainer.compute_single_action(agent_obs, policy_id=policy_id, explore=False)
                state, rewards, terminated, truncated, infos = algo.env.step(actions)
                #if algo.env.action:
                #    jsonsaver.add_data_comp(algo.env.raw_env.observation_raw, algo.env.action)
                #if algo.RENDER:
                #    algo.env.render()
                #    time.sleep(0.01)
        algo.logger.info(f"Simulation finished, info: {algo.env.raw_env.info}")
        with open(self.file_path, 'a') as f:  # 'a' für Append-Modus
            f.write(self.selected_checkpoint + '\n')
            f.write(str(algo.env.raw_env.info["charging_revenue"] - algo.env.raw_env.info["energy_cost"]) + '\n')
            f.write(str(algo.env.raw_env.info["user_satisfaction"]) + '\n')
            f.write('\n')  # Leere Zeile am Ende

    def policy_mapping_fn(self, agent_id, algo): 
            # Maps agent_id to a policy based on its prefix and self.AgentID
            if agent_id.startswith("central_agent"):
                return "central_policy"
            elif agent_id.startswith("gini_agent_"):
                gini_number = int(agent_id.split("_")[-1]) 
                if algo.useMultiGiniAgents: 
                    return f"gini{gini_number}_policy"
                else: 
                    return f"gini{0}_policy"
            elif algo.AgentID == 1:
                if agent_id.startswith("gini_power_agent"):
                    return "gini_power_policy" 
                if agent_id.startswith("cs_power_agent"):
                    return "cs_power_policy"
            elif algo.AgentID == 2:
                if agent_id.startswith("termination_agent_"):
                    gini_number = int(agent_id.split("_")[-1]) 
                    if algo.useMultiTerminationAgents: 
                        return f"termination_policy_{gini_number}"
                    else: 
                        return f"termination_policy_{0}"
            elif algo.AgentID == 3:
                if agent_id.startswith("termination_agent_"):
                    gini_number = int(agent_id.split("_")[-1]) 
                    if algo.useMultiTerminationAgents: 
                        return f"termination_policy_{gini_number}"
                    else: 
                        return f"termination_policy_{0}"
                if agent_id.startswith("gini_power_agent"):
                    return "gini_power_policy" 
                if agent_id.startswith("cs_power_agent"):
                    return "cs_power_policy"
            else:
                raise ValueError(f"Unknown agent_id: {agent_id}. No matching policy found.")