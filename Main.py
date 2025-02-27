from SimulationEnvironment.GymEnvironment import CustomEnv
from Controller_Agent.AgentFactory import AgentFactory
from Controller_Agent.InterfaceAgent import InterfaceAgent
from SimulationEnvironment.EnvConfig import EnvConfig
import time
from config.logger_config import get_module_logger
from helpers.JSONSaver import JSONSaver
from helpers.Plotting.Plot_json_logs import plot_and_save_small
import os
import json
# Set log level for the logger
logger = get_module_logger(__name__)

with open('main_config.json', 'r') as f:
    config = json.load(f)

RENDER = config['RENDER']
SAVE_JSON = config['SAVE_JSON']
OUTPUT_GRAPHS = config['OUTPUT_GRAPHS']
FOLDERPATH =config['FOLDERPATH']
LOOP = config['LOOP']

FILE_NAME =r"config\env_config\Benchmark\comparison_summer.json"

def run_main(fullfilename):
        start_time = time.time()  # Start the timer
        config_path = fullfilename #"config\env_config_stationary_storage_one.json"
        gym_config = EnvConfig.load_env_config(config_file=config_path)
        env = CustomEnv(config=gym_config)
        agent: InterfaceAgent = AgentFactory.create_agent(agent_type=gym_config.control_agent,
                                                        P_grid_max=gym_config.max_grid_power) # the agent type should later be defined in the config file

        jsonsaver = JSONSaver()

        
        while env.time_manager.get_current_time() < env.time_manager.get_stop_time():
                action = agent.calculate_action(env.observation_raw, env.action_raw_base)
                observation, step_reward, terminated, truncated, info= env.step(action)
                jsonsaver.add_data_comp(env.observation_raw, action)
                logger.info(f"Current time: {env.time_manager.get_current_time()}")
                if RENDER:
                        env.render()
                        time.sleep(0.01)
        logger.info(f"Simulation finished, info: {info}")
        if RENDER:
                env.render(close=True)

        end_time = time.time()  # Stop the timer
        if SAVE_JSON:
                jsonsaver.save_to_json()
                jsonsaver.save_config_in_output_folder(config_path)
                if OUTPUT_GRAPHS:
                        plot_and_save_small(json_path=jsonsaver.file_name)




        elapsed_time = end_time - start_time
        logger.info(f"Elapsed time: {elapsed_time} seconds")
        profit = info["charging_revenue"] - info["energy_cost"]
        logger.info(f"Profit of {profit} Euro with energy purchasing cost of {info['energy_cost']} and energy sales of {info['charging_revenue']}")

def run_main_loop():
        for filename in os.listdir(FOLDERPATH):
                fullfilename = os.path.join(FOLDERPATH, filename)
                logger.info(fullfilename)
                if not os.path.isfile(fullfilename):
                        logger.error(f"File {fullfilename} does not exist")
                        continue
                run_main(fullfilename)


if __name__ == "__main__":
        if LOOP:
                run_main_loop()
        else:
                run_main(fullfilename=FILE_NAME)



        
