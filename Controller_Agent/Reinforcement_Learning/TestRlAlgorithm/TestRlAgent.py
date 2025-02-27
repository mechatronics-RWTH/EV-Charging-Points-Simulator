from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARLEnvironment import HMARLEnvironment
import os
from Controller_Agent.Reinforcement_Learning.TestRlAlgorithm.TrainedRlAgent import TrainedRlAgent
from pathlib import Path
from config.logger_config import get_module_logger
from helpers.JSONSaver import JSONSaver
from helpers.Plotting.Plot_json_logs import plot_and_save_small
import time
import re
from dataclasses import dataclass
import json
from typing import List
logger = get_module_logger(__name__)

@dataclass
class TrainingProfit:
    iteration: int
    profit: float
    cost: float
    revenue: float

class TestRlAgent:
    def __init__(self, 
                 trained_agent_path = None, 
                 env_config_path = None,
                 save_plots = False,
                 output_graph = False,
                 save_json_active = False,
                 saving_path = None,):
        self.trained_agent_path = trained_agent_path
        self.env_config_path = env_config_path
        self.env = None
        self.agent = None
        self.save_json_active = save_json_active
        self.jsonsaver = None
        self.hmarl_env = None
        self.env = None
        self.save_plots = save_plots
        self.iteration = None
        self.output_graph = output_graph
        self.training_profit_infos: List[TrainingProfit] = None
        self.list_of_agent_checkpoints = []
        self.saving_path = Path("OutputData/summary_data") if saving_path is None else path(saving_path)
        self.summary_data_file_name = None 
        self.file_created = False

    def load_new_agent(self, trained_agent_path=None, 
                       env_config_path= None):
        if trained_agent_path is not None:
            self.trained_agent_path = trained_agent_path
        if env_config_path is not None:
            self.env_config_path = env_config_path
        self.get_iteration_from_filename()
        self.agent = TrainedRlAgent(trained_agent_path=self.trained_agent_path,
                                    env_config_path=self.env_config_path)
        self.agent.rebuild_env()
        self.agent.load_from_checkpoint()
        self.env = self.agent.hmarl_env.raw_env
    
    def get_iteration_from_filename(self):
        path_str_to_extract_from = str(self.trained_agent_path)
        self.iteration = int(path_str_to_extract_from.split("_")[-1])

    def add_jsonsaver(self):
        if self.save_json_active:
            self.jsonsaver = JSONSaver()

    def run_single_env_loop(self):
        self.env.reset()
        while self.env.time_manager.get_current_time() < self.env.time_manager.get_stop_time():
            action = self.agent.compute_sarl_action(self.env.observation_raw)
            observation, step_reward, terminated, truncated, info = self.env.step(action)
            if self.jsonsaver is not None:
                self.jsonsaver.add_data_comp(self.env.observation_raw, action)
            logger.info(f"Current time: {self.env.time_manager.get_current_time()}")
        logger.info(f"Simulation finished, info: {info}")
        self.final_info = info
        self.get_key_infos_from_final_info()

    def save_json(self,
                  filepath = None):
        saving_file_name = None
        if self.jsonsaver is not None:
            saving_file_name = self.get_training_path_file_name(path=filepath)
            self.jsonsaver.save_to_json(file_name=saving_file_name)
            self.jsonsaver.save_config_in_output_folder(self.env_config_path)

    def get_training_path_file_name(self, path):
        if isinstance(path, Path):
            path = str(path)
        match = re.search(r'checkpoint_(\d{8})_(\d{6}).*checkpoint_(\d+)', path)

        if match:
            date = match.group(1)  # "20250210"
            time = match.group(2)  # "203111"
            checkpoint_number = match.group(3)  # "000044"
            print(f"Date: {date}, Time: {time}, Checkpoint: {checkpoint_number}")
        else:
            raise Exception(f"No match found for {path}")
        my_file_name = f"run_with_checkpoint_{date}_{time}_{checkpoint_number}"
        return my_file_name
        

    def plot_and_save(self):
        if self.output_graph and self.jsonsaver is not None:
            plot_and_save_small(json_path=self.jsonsaver.file_name)

    def get_key_infos_from_final_info(self):
        if self.training_profit_infos is None:
            self.training_profit_infos = []
        profit = self.final_info["charging_revenue"] - self.final_info["energy_cost"]
        self.training_profit_infos.append(TrainingProfit(iteration=self.iteration,
                                        profit=profit,
                                        cost=self.final_info['energy_cost'],
                                        revenue=self.final_info['charging_revenue']))
        
    def get_checkpoints_from_folder(self):
        self.list_of_agent_checkpoints = []
        folder_path: Path = Path(self.folder_with_checkpoints)
        for file in os.listdir(self.folder_with_checkpoints):
            if "checkpoint" in file:
                full_filename = folder_path / file
                self.list_of_agent_checkpoints.append(full_filename)


    def get_summary_data_file_name(self):
        if not self.file_created:
            if self.trained_agent_path is not None:
                fileending = Path(self.trained_agent_path).parent.name
            else:
                fileending = "default"  # Provide a fallback if `trained_agent_path` is None

            self.summary_data_file_name = self.saving_path / f"summary_data_{fileending}.json"
            ending_count = 1

            while self.summary_data_file_name.exists():  # Corrected file existence check
                self.summary_data_file_name = self.saving_path / f"summary_data_{fileending}_{ending_count}.json"
                ending_count += 1  # Increment count to avoid infinite loop
            self.file_created = True


    def save_key_infos(self):
        # Ensure summary file name is set
        if not self.summary_data_file_name:
            self.get_summary_data_file_name()

        # Try to load existing data if the file exists
        if self.summary_data_file_name.exists():
            with open(self.summary_data_file_name, "r") as f:
                try:
                    key_info_dicts = json.load(f)
                    if not isinstance(key_info_dicts, list):  # Ensure it's a list
                        key_info_dicts = []
                except json.JSONDecodeError:
                    key_info_dicts = []  # If JSON is corrupted, start fresh
        else:
            key_info_dicts = []

        # Convert new entries to dictionaries
        try:
            new_entries = [
                {
                    "iteration": key_info.iteration,
                    "profit": key_info.profit,
                    "cost": key_info.cost,
                    "revenue": key_info.revenue
                }
                for key_info in self.training_profit_infos
            ]
        except AttributeError as e:
            raise ValueError(f"Raised {e} for {self.training_profit_infos}")
        except TypeError as e:
            raise ValueError(f"Raised {e} for {self.training_profit_infos}")


        # Append new data
        key_info_dicts.extend(new_entries)

        # Write the updated list back to the file
        with open(self.summary_data_file_name, "w") as f:
            json.dump(key_info_dicts, f, indent=4)

    def run_with_multiple_agents(self, 
                                 folder_with_checkpoints:str = None,
                                 list_of_agent_checkpoints:str = None):
        errors_during_loop =[]
        if folder_with_checkpoints is not None:
            self.folder_with_checkpoints = folder_with_checkpoints
            self.get_checkpoints_from_folder()  
        elif list_of_agent_checkpoints is not None:
            self.list_of_agent_checkpoints = list_of_agent_checkpoints
        else:
            raise ValueError("No checkpoints provided") 
        #self.training_profit_infos = []
        for trained_agent_path in self.list_of_agent_checkpoints:
            self.load_new_agent(trained_agent_path=trained_agent_path,
                                env_config_path=None)
            self.get_summary_data_file_name()
            self.add_jsonsaver()

            try:
                self.run_single_env_loop()
            except Exception as e:
                errors_during_loop.append(e)
                logger.error(f"Error in run_single_env_loop: {e}")
                raise e
            self.save_json(filepath=trained_agent_path)
            self.plot_and_save()
            #self.get_key_infos_from_final_info()
            self.save_key_infos()
        if len(errors_during_loop) > 0:
            logger.error(f"Errors in {len(errors_during_loop)} out of {len(self.list_of_agent_checkpoints)} runs")


class TestRl_HMARL(TestRlAgent):

    def run_single_env_loop(self):
        
        self.env = self.agent.hmarl_env.raw_env
        obs,_ = self.env.reset()
        while self.env.time_manager.get_current_time() < self.env.time_manager.get_stop_time():
            actions = {}
            for agent_id, agent_obs in obs.items():
                policy_id = self.agent.policy_mapping_fn(agent_id)
                actions[agent_id] = self.agent.rllib_algorithm.compute_single_action(agent_obs, policy_id=policy_id, explore=False)
            obs, rewards, terminated, truncated, infos = self.agent.hmarl_env.step(actions)

            logger.info(f"Simulation finished, info: {self.agent.hmarl_env.raw_env.info}")
        self.final_info = self.agent.hmarl_env.raw_env.info
        self.get_key_infos_from_final_info()


    
# trained_agent_path = "Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250207_141617/checkpoint_000100"
# env_config_path = "config/env_config/Benchmark/comparison_fall.json"
# RENDER = False#config['RENDER']
# SAVE_JSON = True# config['SAVE_JSON']
# OUTPUT_GRAPHS = True#config['OUTPUT_GRAPHS']
# FOLDERPATH = None #config['FOLDERPATH']
# LOOP = False #config['LOOP']
# def test_with_env():
#         agent = TrainedRlAgent(trained_agent_path=trained_agent_path,
#                                    env_config_path=env_config_path,)
#         agent.rebuild_env()
#         agent.load_from_checkpoint()
#         env = agent.hmarl_env.raw_env
#         obs = env.reset()
#         done = False

#         jsonsaver = JSONSaver()

#         start_time = time.time()  # Start the timer
#         while env.time_manager.get_current_time() < env.time_manager.get_stop_time():
#                 action = agent.compute_sarl_action(env.observation_raw)
#                 observation, step_reward, terminated, truncated, info= env.step(action)
#                 jsonsaver.add_data_comp(env.observation_raw, action)
#                 logger.info(f"Current time: {env.time_manager.get_current_time()}")
#                 if RENDER:
#                         env.render()
#                         time.sleep(0.01)
#         logger.info(f"Simulation finished, info: {info}")
#         if RENDER:
#                 env.render(close=True)

#         end_time = time.time()  # Stop the timer
#         if SAVE_JSON:
#                 jsonsaver.save_to_json()
#                 jsonsaver.save_config_in_output_folder(env_config_path)
#                 if OUTPUT_GRAPHS:
#                         plot_and_save_small(json_path=jsonsaver.file_name)

#         elapsed_time = end_time - start_time
#         logger.info(f"Elapsed time: {elapsed_time} seconds")
#         profit = info["charging_revenue"] - info["energy_cost"]
#         logger.info(f"Profit of {profit} Euro with energy purchasing cost of {info['energy_cost']} and energy sales of {info['charging_revenue']}")
       
# def test_with_hmarl():
#         agent = TrainedRlAgent(trained_agent_path=trained_agent_path,
#                                    env_config_path=env_config_path,)
#         agent.rebuild_env()
#         agent.load_from_checkpoint()
#         env = agent.hmarl_env
#         obs,_ = env.reset()
#         done = False

#         jsonsaver = JSONSaver()

#         start_time = time.time()  # Start the timer
#         while agent.hmarl_env.raw_env.time_manager.get_current_time() < agent.hmarl_env.raw_env.time_manager.get_stop_time():
#                 actions = {}
#                 for agent_id, agent_obs in obs.items():
#                         policy_id = agent.policy_mapping_fn(agent_id)
#                         actions[agent_id] = agent.rllib_algorithm.compute_single_action(agent_obs, policy_id=policy_id, explore=False)
#                 obs, rewards, terminated, truncated, infos = agent.hmarl_env.step(actions)

#                 logger.info(f"Simulation finished, info: {agent.hmarl_env.raw_env.info}")
