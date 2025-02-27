import argparse
import os
import sys
from config.definitions import MPC_CONFIG_DIR

# Add the current working directory to the Python path
current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.append(current_working_directory)


import pathlib
# Rest of your script
from SimulationEnvironment.GymEnvironment import CustomEnv
from Controller_Agent.AgentFactory import AgentFactory
from Controller_Agent.InterfaceAgent import TemplateAgent
from SimulationEnvironment.EnvConfig import EnvConfig
import time
from config.logger_config import get_module_logger
from helpers.JSONSaver import JSONSaver
#from helpers.Plotting.Plot_json_logs import plot_and_save, plot_and_save_small
from Controller_Agent.Model_Predictive_Controller.MpcFactory import MPCFactory
from Controller_Agent.Model_Predictive_Controller.Model_Predictive_Controller import Model_Predictive_Controller
from Controller_Agent.Model_Predictive_Controller.MPC_Config import MpcConfig

# Set log level for the logger
logger = get_module_logger(__name__)

RENDER = False #config['RENDER']
SAVE_JSON = True#config['SAVE_JSON']
OUTPUT_GRAPHS = False #config['OUTPUT_GRAPHS']
#FOLDERPATH = #config['FOLDERPATH']
LOOP = False #config['LOOP']

ENVIRONMENT_CONFIG = "config/env_config/env_config_MPC_test.json" #"config/env_config/Benchmark/comparison_summer.json"
MPC_CONFIG="Controller_Agent/Model_Predictive_Controller/config/mpc_lstm_24_no_slack_move_penalty.json"#"Controller_Agent/Model_Predictive_Controller/config/mpc_slack_10.json"#"Controller_Agent/Model_Predictive_Controller/config/Benchmark/mpc_perfect_96.json" #"Controller_Agent/Model_Predictive_Controller/config/Benchmark/mpc_perfect_24.json"#Controller_Agent/Model_Predictive_Controller/config/mpc_no_slack_no_prediction.json"#"Controller_Agent/Model_Predictive_Controller/config/Benchmark/mpc_lstm_24_no_slack.json"

def run_main(environment_config_json=ENVIRONMENT_CONFIG,
             mpc_config_file="mpc_base_config.json"):
    #fullfilename =pathlib.Path(fullfilename).as_posix()
    gym_config = EnvConfig.load_env_config(config_file=environment_config_json)
    env = CustomEnv(config=gym_config)
    env.reset()
    #num_parking_fields = env.parking_area.get_number_of_fields_with_type()
    mpc_config = MpcConfig.load_mpc_config(config_file=mpc_config_file,
                                            )
    mpc_config.load_from_env_config(env_config=gym_config)
    MPC_Builder = MPCFactory(mpc_config=mpc_config,
                                env_config=gym_config)
    agent: Model_Predictive_Controller = MPC_Builder.create(observation=env.observation_raw, 
                                                            action=env.action_raw_base)

    jsonsaver = JSONSaver()

    start_time = time.time()  # Start the timer

    while env.time_manager.get_current_time() < gym_config.start_datetime + gym_config.sim_duration:
        action = agent.calculate_action(env.observation_raw, env.action_raw_base)
        
        env.step(action)
        logger.debug(f'current time: {env.observation_raw["current_time"] }, USER_req: {env.observation_raw["user_requests"]}, E_req {env.observation_raw["energy_requests"]}')
        jsonsaver.add_data_comp(env.observation_raw, action)
        logger.info(f"Current time: {env.time_manager.get_current_time()}")
        if RENDER:
            env.render()
            time.sleep(0.01)

    if RENDER:
            env.render(close=True)


    end_time = time.time()  # Stop the timer
    if SAVE_JSON:
        jsonsaver.save_to_json()
        jsonsaver.save_config_in_output_folder(environment_config_json)
        # if OUTPUT_GRAPHS:
        #         plot_and_save_small(json_path=jsonsaver.file_name)
        
        #mpc_config_file = pathlib.Path(MPC_CONFIG_DIR)/ pathlib.Path(mpc_config_file).name
        jsonsaver.save_config_in_output_folder(mpc_config_file,
                                                copy_file_name="mpc_config.json")


    elapsed_time = end_time - start_time
    logger.info(f"Elapsed time: {elapsed_time} seconds")

def run_main_in_loop(config_folder="Controller_Agent/Model_Predictive_Controller/config/Benchmark",
                     environment_config_json = "config/env_config/env_config_MPC_test.json"
             ):
    # List all files in the folder
    files = os.listdir(config_folder)

    # Filter out the config files
    config_files = [file for file in files if file.endswith(".json")]

    # Get the full path of each config file
    full_paths = [os.path.join(config_folder, file) for file in config_files]

    # Iterate over the config files and run run_main with each file
    for config_file in config_files:
        logger.info(f"Running {config_file}")
        fullfilename = pathlib.Path(config_folder).joinpath(config_file)
        #try:
        run_main(environment_config_json=environment_config_json,
                mpc_config_file=fullfilename)
        # except Exception as e:
        #     # Log a simple error message
        #     logger.error(f"Error occurred while running {fullfilename}")            
        #     # Log the exception message
        #     logger.error(e)            
        #     # Log the traceback details for more insight into where the error occurred
        #     tb_str = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        #     logger.error(f"Traceback details:\n{tb_str}")


if __name__ == "__main__":
    if LOOP:           
        # Get the folder path containing the config files
        config_folder = "Controller_Agent/Model_Predictive_Controller/config/Benchmark" # relative to MPC config folder
        run_main_in_loop(config_folder=config_folder,
                         environment_config_json=ENVIRONMENT_CONFIG)

    else:
        run_main(environment_config_json=ENVIRONMENT_CONFIG,
                 mpc_config_file=MPC_CONFIG)



        
