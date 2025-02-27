import os
import pathlib

#ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = pathlib.Path.cwd()
CONFIG_DIR = ROOT_DIR / 'config'
ENV_CONFIG_DIR = CONFIG_DIR / 'env_config'
PARKING_LOT_CONFIG_DIR = CONFIG_DIR / 'parking_lot_config'
TRAFFIC_SIM_CONFIG_DIR = CONFIG_DIR / 'traffic_sim_config'
OUTPUT_DIR = ROOT_DIR / 'OutputData'
PLOTS_DIR = OUTPUT_DIR / 'plots'
LOG_DIR = OUTPUT_DIR / 'logs'
DATA_DIR = OUTPUT_DIR / 'data'
VIDEO_DIR = OUTPUT_DIR / 'videos'
CONTROL_DIR = ROOT_DIR / 'Controller_Agent'
MPC_CONFIG_DIR = CONTROL_DIR / 'Model_Predictive_Controller/config'