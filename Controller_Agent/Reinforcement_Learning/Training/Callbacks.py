from ray.rllib.algorithms.callbacks import DefaultCallbacks
from config.logger_config import get_module_logger
from collections import defaultdict
import os 
import json
import pathlib
import datetime
import random

logger = get_module_logger(__name__)

class RewardLoggingCallback(DefaultCallbacks):
    def on_episode_end(self, *, worker, base_env, policies, episode, **kwargs):
        """Logs episode rewards for each agent at the end of an episode."""
        rewards = episode.agent_rewards  # Dictionary: {(agent_id, policy_id): total_reward}
        logger.info(f"Episode {episode.episode_id} rewards: {rewards}")
        print(f"Episode {episode.episode_id} rewards: {rewards}")
        
        # # Optional: Store it in custom_metrics for RLlib’s logger
        # for (agent_id, _), reward in rewards.items():
        #     episode.custom_metrics[f"reward_{agent_id}"] = reward

class RewardSavingToFileCallback(DefaultCallbacks):
    def __init__(self, logdir=None):
        super().__init__()
        self.logdir = logdir  # Use provided logdir if given

    def on_train_result(self, *, algorithm, result, **kwargs):
        """Retrieve logdir dynamically or use the provided one."""
        if self.logdir is None:
            self.logdir = algorithm.logdir  # Default to RLlib log directory

        # Ensure directory exists
        os.makedirs(self.logdir, exist_ok=True)

        # Define the reward log file path
        reward_log_file = os.path.join(self.logdir, "rewards_log.json")

        # Read existing data
        if os.path.exists(reward_log_file):
            with open(reward_log_file, "r") as f:
                reward_data = json.load(f)
        else:
            reward_data = []

        # Create agent rewards dictionary in the new format
        agent_rewards = defaultdict(lambda: {"policies": {}})
        for key, values in result.get("hist_stats", {}).items():
            if "reward" in key:
                policy_name = key.split("/")[0].replace("policy_", "")  # Extract policy name
                agent_name = policy_name.split('_')[0]  # Extract agent name from policy name

                for i, reward in enumerate(values):  # Log rewards for each agent
                    if agent_name not in agent_rewards:
                        agent_rewards[agent_name] = {"policies": {}}
                    agent_rewards[agent_name]["policies"][policy_name] = reward

        # Append new reward info
        reward_data.append({
            "iteration": result["training_iteration"],
            "mean_reward": result.get("episode_reward_mean", "N/A"),
            "agent_rewards": dict(agent_rewards)  # Convert defaultdict to regular dict
        })

        # Write to file
        with open(reward_log_file, "w") as f:
            json.dump(reward_data, f, indent=4)

        print(f"Rewards saved in {reward_log_file}")



class RewardSavingEpisodeCallback(DefaultCallbacks):
    def __init__(self, logdir=None):
        super().__init__()
        self.file_name_determined = False  # Allow custom log directory
        self.file_base_name = None 

    def on_episode_end(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        """Save the rewards at the end of each episode."""
        reward_log_folder = pathlib.Path("Controller_Agent/Reinforcement_Learning/trained_models/reward_logs")
        if not self.file_name_determined:
            datestr = datetime.datetime.now().strftime("%Y-%m-%d")  # Get current date
            timestr = datetime.datetime.now().strftime("%H-%M-%S")  # Get current time
            self.file_base_name = f"rewards_log_{datestr}_{timestr}.txt"
            self.file_name_determined = True
        #     # Get all subdirectories and sort them by modification time (newest first)
        #     base_path = "Controller_Agent/Reinforcement_Learning/trained_models"
        #     folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
        #     # Get the newest folder name
        #     newest_folder_name = max(folders, key=lambda f: os.path.getmtime(os.path.join(base_path, f)))
        #     self.file_base_name = f"rewards_log_{newest_folder_name}" 
        #     self.file_name_determined = True

        
        
        #reward_log_path = checkpoint_path.parent / "reward_logs"
        file_base_name = self.file_base_name
        FILE_EXTENSION = ".json"
        # Construct the output file name with checkpoint info
        output_plot_file_name = reward_log_folder/f"{file_base_name}{FILE_EXTENSION}" #reward_log_path / 
        if not os.path.exists(reward_log_folder):
            os.makedirs(reward_log_folder, exist_ok=True)

        # Define the reward log file path
        reward_log_file = output_plot_file_name#"rewards_log.json"#os.path.join(self.logdir, "rewards_log.json")

        # Read existing data
        if os.path.exists(reward_log_file):
            with open(reward_log_file, "r") as f:
                reward_data = json.load(f)
        else:
            reward_data = []

        # Create agent rewards dictionary in the new format
        agent_rewards = defaultdict()
        for agent_id, agent_info in episode.agent_rewards.items():
            agent_name = agent_id[0]
            policy = agent_id[1]
            total_agent_reward = agent_info
            agent_rewards[agent_name] = {"policy": None, "reward": None}
            agent_rewards[agent_name]["policy"] = policy
            agent_rewards[agent_name]["reward"] = total_agent_reward
            logger.info(f"{agent_id},{policy}: {total_agent_reward}")

        # Append new reward info for this episode
        reward_data.append({
            "episode": episode.episode_id,
            "episode_length": episode.length,
            "mean_reward": episode.total_reward / episode.length if episode.length > 0 else 0,
            "agent_rewards": dict(agent_rewards)  # Convert defaultdict to regular dict
        })

        # Write to file
        with open(reward_log_file, "w") as f:
            json.dump(reward_data, f, indent=4)

        print(f"Episode rewards saved in {reward_log_file}")


class AgentRewardPrintCallback(DefaultCallbacks):
    def on_episode_end(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        """Print the reward for each agent at the end of the episode."""
        
        # Optionally, log the rewards if needed
        logger.info(f"Episode {episode.episode_id} ended with the following agent rewards:")
        reward_dict = {}
        for agent_id, agent_info in episode.agent_rewards.items():
            total_agent_reward = agent_info  # Sum up rewards for each policy of the agent
            agent_name = agent_id[0]
            policy = agent_id[1]
            logger.info(f"  {agent_id},{policy}: {total_agent_reward}")

        # If needed, also print the overall episode reward
        logger.info(f"Total episode reward: {episode.total_reward}")


class CustomResetCallback(DefaultCallbacks):
    def __init__(self, env_config_collection):
        super().__init__()
        self.env_config_collection = env_config_collection

    def on_episode_end(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        # Access and use env_config_collection here
        if self.env_config_collection:
            # Example of selecting a new config (you might want more sophisticated logic)
            new_env_config = random.choice(self.env_config_collection)
            
            # Get actual environment instance
            env = base_env.get_sub_environments()[env_index]
            
            if hasattr(env, 'reset'):
                # Reset with new configuration options if applicable
                reset_options = {
                    "new_config": new_env_config  # Pass whatever makes sense for your environment
                }
                env.reset(options=reset_options)

        print(f"Episode {episode.episode_id}: rewards = {episode.custom_metrics}")