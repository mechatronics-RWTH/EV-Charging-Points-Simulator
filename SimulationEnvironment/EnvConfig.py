import json
from datetime import timedelta, datetime
import pathlib
import random

from SimulationEnvironment.Settings.SimSettings import SimSettings
from SimulationModules.ElectricityCost.ElectricyPrice import PriceTable, StockPriceTable
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
from dataclasses import dataclass


logger = get_module_logger(__name__)
HORIZON=96

   


def print_config(config: dict):
    for key, value in config.items():
        if (isinstance(value, list)):
            if len(value)>10:
                continue
        logger.info(f"{key:30}: {value}")

CONFIG_FILE = "config/env_config/env_config.json"
@dataclass
class EnvConfig:
    step_time: timedelta = timedelta(seconds=900)
    sim_duration: timedelta = timedelta(days=1)
    start_datetime: datetime = datetime(year=2021, month=1, day=1, hour=0)
    horizon: int = 96
    price_table: PriceTable = None #StockPriceTable()
    max_building_power: PowerType = PowerType(100, PowerTypeUnit.KW)
    max_grid_power: PowerType = PowerType(100, PowerTypeUnit.KW)
    #pred_building_power: list = [PowerType(random.randint(0,100),PowerTypeUnit.KW) for i in range(96)]
    max_pv_power: PowerType = PowerType(100, PowerTypeUnit.KW)
    pv_area_in_m2: int = 75
    max_charging_power: PowerType = PowerType(100, PowerTypeUnit.KW)
    #pred_pv_power: list = [PowerType(random.randint(0,100),PowerTypeUnit.KW) for i in range(96)]
    max_parking_time: timedelta = timedelta(hours=8)
    max_energy_request: EnergyType = EnergyType(100, EnergyTypeUnit.KWH)
    max_ev_energy: EnergyType = EnergyType(100, EnergyTypeUnit.KWH)
    max_gini_energy: EnergyType = EnergyType(100, EnergyTypeUnit.KWH)
    customers_per_hour: int = 1
    assigner_mode: str = "random"
    stationary_batteries: StationaryBatteryStorage = None
    control_agent: str = "random"
    recording_data_path: str = None
    weights_for_reward: dict = None 
    gini_starting_fields: list = None
    parking_lot_path: str = None
    yearly_building_consumption_in_kWh: EnergyType = None #EnergyType(100, EnergyTypeUnit.KWH)


    @staticmethod
    def load_env_config(config_file: str=CONFIG_FILE,
                        check_config:bool = True):
        



        config_file = pathlib.Path(str(config_file).replace("\\", "/"))
        config_file= pathlib.Path(ROOT_DIR).joinpath(config_file)
        
        with open(config_file, 'r') as f:
            config = json.load(f)

        try:
            stationary_batteries_settings = config["stationary_batteries"]
            stationary_batteries = StationaryBatteryStorage(
                                            energy_capacity=EnergyType(stationary_batteries_settings["energy_capacity_in_kWh"], EnergyTypeUnit.KWH),
                                            present_energy=EnergyType(stationary_batteries_settings["present_energy_in_kWh"], EnergyTypeUnit.KWH),
                                            maximum_charging_c_rate=stationary_batteries_settings["max_charging_c_rate"],
                                            maximum_discharging_c_rate=stationary_batteries_settings["max_discharging_c_rate"],
                                            )
        except KeyError as e:
            stationary_batteries = None
            logger.warning(f"KeyError: {e} in config file. Apparently no stationary batteries are defined.")

        step_time = timedelta(seconds=config["step_time"])
        sim_duration = timedelta(days=config['sim_duration']['days'],
                                 hours=config['sim_duration']['hours'],
                                 minutes=config['sim_duration']['minutes'],
                                 seconds=config['sim_duration']['seconds'])
        start_datetime = datetime(year=config['starttime']['year'],
                                  month=config['starttime']['month'],
                                  day=config['starttime']['day'],
                                  hour=config['starttime']['hour'],)
        price_table = StockPriceTable(start_time=start_datetime,
                                        end_time=start_datetime+sim_duration,
                                        step_time=step_time,
                                        horizon=HORIZON)
        if "recording_data_path" in config:
            recording_data_path=config["recording_data_path"]
        else:
            recording_data_path=None
        logger.info(f"Recording data path in {config_file} is {recording_data_path}")
        

        return EnvConfig(step_time=step_time,
                    sim_duration=sim_duration,
                    start_datetime=start_datetime,
                    horizon=HORIZON,
                    price_table=price_table,
                    max_building_power=PowerType(config["max_building_power_in_kW"], PowerTypeUnit.KW),
                    max_grid_power=PowerType(config["max_grid_power_in_kW"], PowerTypeUnit.KW),
                    max_pv_power=PowerType(config["max_pv_power_in_kW"], PowerTypeUnit.KW),
                    pv_area_in_m2=75, #TODO !!!still not implemented in env!!!
                    max_charging_power=PowerType(config["max_charging_power_in_kW"], PowerTypeUnit.KW),
                    max_parking_time=timedelta(hours=config["max_parking_time"]["hours"]),
                    max_energy_request=EnergyType(config["max_energy_request_in_kWh"], EnergyTypeUnit.KWH),
                    max_ev_energy=EnergyType(config["max_ev_energy_in_kWh"], EnergyTypeUnit.KWH),
                    max_gini_energy=EnergyType(config["max_gini_energy_in_kWh"], EnergyTypeUnit.KWH),
                    customers_per_hour=config["customers_per_hour"],
                    assigner_mode=config["assigner_mode"],
                    stationary_batteries=stationary_batteries,
                    control_agent=config["control_agent"],
                    gini_starting_fields=config["gini_starting_fields"],
                    parking_lot_path=config["parking_lot_path"],
                    yearly_building_consumption_in_kWh=EnergyType(
                        energy_amount_in_j=config["yearly_building_consumption_in_kWh"],
                        unit=EnergyTypeUnit.KWH
                    ),
                    weights_for_reward=config["weights_for reward"],
                    recording_data_path=recording_data_path,
                    )





