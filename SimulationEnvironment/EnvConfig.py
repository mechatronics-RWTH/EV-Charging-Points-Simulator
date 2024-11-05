import json
from datetime import timedelta, datetime
import pathlib
import random

from SimulationEnvironment.Settings.SimSettings import SimSettings
from SimulationModules.ElectricitiyCost.ElectricyPrice import PriceTable, StockPriceTable
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger


logger = get_module_logger(__name__)
HORIZON=96

def print_config(config: dict):
    for key, value in config.items():
        if (isinstance(value, list)):
            if len(value)>10:
                continue
        logger.info(f"{key:30}: {value}")

CONFIG_FILE = "config/env_config.json"
class EnvConfig:
    @staticmethod
    def load_env_config(config_file: str=CONFIG_FILE):

        config_file = pathlib.Path(config_file)
        config_file= pathlib.Path(ROOT_DIR).joinpath(config_file)
        
        with open(config_file, 'r') as f:
            config = json.load(f)

        settings = SimSettings(step_time=timedelta(seconds=config["step_time"]),
                                    sim_duration=timedelta(days=config['sim_duration']['days'],
                                                           hours=config['sim_duration']['hours'],
                                                           minutes=config['sim_duration']['minutes'],
                                                           seconds=config['sim_duration']['seconds']),
                                    start_datetime=datetime(year=config['starttime']['year'],
                                                            month=config['starttime']['month'],
                                                            day=config['starttime']['day'],
                                                            hour=config['starttime']['hour'],))
        start_time = settings.start_datetime
        horizon=HORIZON
        if 'horizon' in config:
            horizon = config['horizon']
        price_table = StockPriceTable(start_time=start_time,
                                      end_time=start_time+settings.sim_duration,
                                      step_time=settings.step_time,
                                      horizon=horizon)
        max_building_power=PowerType(config["max_building_power_in_kW"], PowerTypeUnit.KW)
        max_grid_power=PowerType(config["max_grid_power_in_kW"], PowerTypeUnit.KW)
        pred_building_power=[PowerType(random.randint(0,max_building_power.value),PowerTypeUnit.KW)
                            for i in range(96)]
        max_pv_power=PowerType(config["max_pv_power_in_kW"], PowerTypeUnit.KW)
        pv_area_in_m2=75 #TODO !!!still not implemented in env!!!
        max_charging_power=PowerType(config["max_charging_power_in_kW"], PowerTypeUnit.KW)
        pred_pv_power=[PowerType(random.randint(0,max_pv_power.value),PowerTypeUnit.KW)
                            for i in range(96)]
        max_parking_time=timedelta(hours=config["max_parking_time"]["hours"])
        max_energy_request=EnergyType(config["max_energy_request_in_kWh"], EnergyTypeUnit.KWH)
        max_ev_energy=EnergyType(config["max_ev_energy_in_kWh"], EnergyTypeUnit.KWH)
        max_gini_energy=EnergyType(config["max_gini_energy_in_kWh"], EnergyTypeUnit.KWH)

        try: 
            parking_lot_path = config["parking_lot_path"].replace("\\", "/")
        except KeyError as e:
            parking_lot_path = "test/Parking_lot_test_smart.txt"
            logger.error(f"KeyError: {e} in config file. Using default value {parking_lot_path} for parking_lot_path")

        try:
            assigner_mode=config["assigner_mode"]
        except KeyError as e:
            assigner_mode = "random"
            logger.error(f"KeyError: {e} in config file. Using default value {assigner_mode} for assigner_mode")

        
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

        gini_starting_fields = config["gini_starting_fields"]
        yearly_building_consumption_in_kWh=EnergyType(
            energy_amount_in_j=config["yearly_building_consumption_in_kWh"],
            unit=EnergyTypeUnit.KWH
        )
    

        gym_config={"price_table": price_table,
                    "settings": settings,
                    "horizon": horizon, 
                    "include_future_price": True,
                    "Parking_Lot": parking_lot_path,
                    "Gini_starting_fields": gini_starting_fields,
                    "max_charging_power": max_charging_power,
                    "max_grid_power":max_grid_power,
                    "max_building_power": max_building_power,
                    "yearly_building_consumption_in_kWh":yearly_building_consumption_in_kWh,
                    "pred_building_power": pred_building_power,
                    "max_pv_power": max_pv_power,
                    "pv_area_in_m2": pv_area_in_m2,
                    "pred_pv_power": pred_pv_power,
                    "max_parking_time": max_parking_time,
                    "max_energy_request": max_energy_request,
                    "max_ev_energy": max_ev_energy,
                    "max_gini_energy": max_gini_energy,
                    "customers_per_hour":config["customers_per_hour"],
                    "assigner_mode":assigner_mode,
                    "stationary_batteries": stationary_batteries,
                    "control_agent": config["control_agent"],
                    "weights_for_reward": {
                        "weight_not_satisfied":config["weights_for reward"]["weight_not_satisfied"],
                        "weight_rejection":config["weights_for reward"]["weight_rejection"],
                        "weight_energy_consumption":config["weights_for reward"]["weight_energy_consumption"]
                        }
                    }
                    # ...

        #print_config(gym_config)

        return gym_config



