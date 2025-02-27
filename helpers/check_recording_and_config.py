from SimulationEnvironment.EnvConfig import EnvConfig
from config.logger_config import get_module_logger
import json
import pathlib

logger = get_module_logger(__name__)


def check_recording_and_config(config: EnvConfig):
    recording_path = config.recording_data_path
    if recording_path is None:
        logger.warning("No recording_data_path defined in config file. Using default value None")
        return 
    with open(recording_path, 'r') as file: 
        file_data = json.load(file)     
    try:
        metadata = file_data["metadata"]
    except KeyError as e:
        raise(e)
    if metadata["start_date"] != config.start_datetime.strftime("%Y-%m-%d %H:%M:%S"):
        raise ValueError(f"Start date in recording ({metadata['start_date']}) and config file ({config.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}) do not match")
    if metadata["sim_duration"] != config.sim_duration.total_seconds():
        raise ValueError(f"Simulation duration in recording ({metadata['sim_duration']}) and config file ({config.sim_duration.total_seconds()}) do not match")
    if metadata["step_time"] != config.step_time.total_seconds():
        raise ValueError(f"Step time in recording ({metadata['step_time']}) and config file ({config.step_time.total_seconds()}) do not match")
    if metadata["customers_per_hour"] != config.customers_per_hour:
        logger.error("Customers per hour in recording and config file do not match")
    if metadata["assigner_mode"] != config.assigner_mode:
       logger.error("Assigner mode in recording and config file do not match")
    if metadata["max_parking_time"] != config.max_parking_time.total_seconds():
        logger.error("Max parking time in recording and config file do not match")
    if pathlib.Path(metadata["parking_lot_path"]) != pathlib.Path(config.parking_lot_path):
        raise ValueError(f"Parking lot path in recording ({metadata['parking_lot_path']}) and config file ({config.parking_lot_path}) do not match")
    if config.assigner_mode != "fixed":
        raise ValueError(f"Assigner mode in config is {config.assigner_mode} but recording makes only really sense with fixed assigner mode")
    
