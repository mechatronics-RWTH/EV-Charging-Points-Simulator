from config.logger_config import get_module_logger
import json
import pathlib
from config.definitions import MPC_CONFIG_DIR
from SimulationEnvironment.EnvConfig import EnvConfig
from enum import IntEnum
from datetime import datetime
import os


class PredictionMode(IntEnum):
    PERFECT = 0
    SIMPLE = 1
    MODEL = 2
    NOPREDICTION = 3
    LSTM = 4

prediction_mode_map = {"perfect": PredictionMode.PERFECT,
                          "simple": PredictionMode.SIMPLE,
                          "model": PredictionMode.MODEL,
                          "noprediction": PredictionMode.NOPREDICTION,
                          "lstm": PredictionMode.LSTM}


logger = get_module_logger(__name__)

import json
import pathlib
from dataclasses import dataclass

CONFIG_FILE = "mpc_base_config.json"

@dataclass
class MpcConfig:
    config_file: str = CONFIG_FILE
    time_step_size: float = None
    horizon_steps: int = None
    solver: str = "glpk"
    solver_time_limit_in_seconds: int = 90
    number_parking_fields: int = None 
    num_robots: int = None
    num_chargers: int = None
    prediction_mode: PredictionMode = None
    selling_cost_in_euro_per_kwh: float = 0.5
    gini_energy_total_in_kwh: float = 40
    start_time: datetime = None
    prediction_data_path: str = None
    solver_mip_gap: float = 0.05
    show_solver_output: bool = False
    use_slack_weight_end_of_horizon: bool = False
    use_linearized_model: bool = True
    moving_penalty: float = 0.0
    lstm_model_path: str = None 


    @staticmethod
    def load_mpc_config(config_file: str = CONFIG_FILE, time_step_size: float = None) -> 'MpcConfig':
                # Uncommented code to handle relative paths
        # if not pathlib.Path(config_file).is_absolute():
        #     config_file = pathlib.Path(MPC_CONFIG_DIR).joinpath(config_file)
        if os.path.dirname(config_file):
            logger.warn(f"{config_file} is a file path with folder structure.")
        else:
            config_file = pathlib.Path(MPC_CONFIG_DIR).joinpath(config_file)


        with open(config_file, 'r') as f:
            loaded_file = json.load(f)

        mpc_config = MpcConfig()
        mpc_config.horizon_steps = loaded_file["N_pred"]

        #TODO: Add check if traffic data is provided in the config file
        if "prediction_mode" in loaded_file:
            mpc_config.prediction_mode = prediction_mode_map[loaded_file["prediction_mode"]]
        if "solver" in loaded_file:
            mpc_config.solver = loaded_file["solver"]
        if "prediction_data_path" in loaded_file:
            mpc_config.prediction_data_path = loaded_file["prediction_data_path"]
        if "solver_time_limit" in loaded_file:
            mpc_config.solver_time_limit_in_seconds = loaded_file["solver_time_limit"]
        if "solver_mip_gap" in loaded_file:
            mpc_config.solver_mip_gap = loaded_file["solver_mip_gap"]
        if "show_solver_output" in loaded_file:
            mpc_config.show_solver_output = loaded_file["show_solver_output"]
        if "selling_cost_in_euro_per_kwh" in loaded_file:
            mpc_config.selling_cost_in_euro_per_kwh = loaded_file["selling_cost_in_euro_per_kwh"]
        if "use_slack_weight_end_of_horizon" in loaded_file:
            mpc_config.use_slack_weight_end_of_horizon = loaded_file["use_slack_weight_end_of_horizon"]
        if "use_linearized_model" in loaded_file:
            mpc_config.use_linearized_model = loaded_file["use_linearized_model"]
        if "moving_penalty" in loaded_file:
            mpc_config.moving_penalty = loaded_file["moving_penalty"]
        if "lstm_model_path" in loaded_file:
            mpc_config.lstm_model_path = loaded_file["lstm_model_path"]
        
        logger.info(f"Recording data path is {mpc_config.prediction_data_path}")
        return mpc_config
    
    def load_from_env_config(self, env_config: EnvConfig):
        self.time_step_size = env_config.step_time#.total_seconds()/3600
        self.gini_energy_total_in_kwh = env_config.max_gini_energy.get_in_kwh().value
        self.max_charger_power = env_config.max_charging_power.get_in_kw().value
        self.start_time = env_config.start_datetime
    

    



