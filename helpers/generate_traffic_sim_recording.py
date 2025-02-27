import json
from datetime import datetime
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.TrafficSimulator.TrafficSimulatorBuilder import TrafficSimulatorBuilder
from SimulationModules.TrafficSimulator.TrafficSimulator import TrafficSimulator
from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationModules.ParkingArea.ParkingAreaBuilder import ParkingAreaBuilder
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.TimeDependent.TimeManager import TimeManager
import os 
from config.definitions import TRAFFIC_SIM_CONFIG_DIR
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

CONFIG_PATH = "config/env_config/comparison_data_generator.json"

class EvArrivalRecorder:

    def __init__(self, filename_with_path=None):
        if filename_with_path is not None:
            self.filename_with_path = filename_with_path
        else:
            self.filename_with_path = os.path.join(TRAFFIC_SIM_CONFIG_DIR,
                                                "arriving_evs_record_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".json") 
        self.arrived_evs_counter = 0
        self.ev_data_for_json = []
        self.metadata = {}

    def save_ev_data(self, build_ev: EV):
        ev_data = {
            "arrival_id": self.arrived_evs_counter, 
            "arrival_time": build_ev.arrival_time.strftime("%Y-%m-%d %H:%M:%S"),
            "departure_time": build_ev.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
            "energy_demand_at_arrival": build_ev.energy_demand_at_arrival.value,
            "battery": {
                "battery_energy": build_ev.battery.battery_energy.get_in_kwh().value,
                "present_energy": build_ev.battery.present_energy.get_in_kwh().value,
                # "maximum_charging_c_rate": build_ev.battery.maximum_charging_c_rate,
                "maximum_charging_power": build_ev.battery.charging_power_map.maximum_power.get_in_kw().value,
                "maximum_discharging_power": build_ev.battery.charging_power_map.minimum_power.get_in_kw().value,
                "power_map_type": build_ev.battery.charging_power_map.get_map_type()
            },
            "parking_spot_id": build_ev.parking_spot_index
        }
        self.ev_data_for_json.append(ev_data)
        self.arrived_evs_counter += 1

    def save_metadata(self, config:EnvConfig):
        self.metadata = {}
        self.metadata["start_date"] = config.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["sim_duration"] = config.sim_duration.total_seconds()
        self.metadata["step_time"] = config.step_time.total_seconds()
        self.metadata["customers_per_hour"] = config.customers_per_hour
        self.metadata["assigner_mode"] = config.assigner_mode
        self.metadata["max_parking_time"] = config.max_parking_time.total_seconds()
        self.metadata["parking_lot_path"]=config.parking_lot_path

    def determine_power_map_type(self, power_map):
        if power_map is None:
            return "None"
        return power_map.__class__.__name__



    def write_ev_record_to_json(self):
        data = {
            "metadata": self.metadata,
            "ev_data": self.ev_data_for_json
        }
        try:
            with open(self.filename_with_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            if os.path.exists(self.filename_with_path):
                os.remove(self.filename_with_path)

def ensure_evs_are_in_charging(parking_area: ParkingArea):
    """
    """
    for spot in parking_area.parking_spot_occupied:
        try:
            spot.vehicle_parked.set_to_charging()
        except Exception as e:
            logger.error(f"Error setting vehicle to charging: {e}")


def generate_traffic_sim_recording(config_path = "config\\env_config\\env_config gini_1day.json",
                                   output_file_name=None):

    config = EnvConfig.load_env_config(config_path, check_config=False)
    time_manager = TimeManager(start_time=config.start_datetime, 
                                   step_time=config.step_time,
                                   sim_duration=config.sim_duration)
    config.assigner_mode= "random"
    ev_arrival_recorder = EvArrivalRecorder(filename_with_path=output_file_name)
    builder = ParkingAreaBuilder()
    parking_area = builder.build(parking_lot_file_path=config.parking_lot_path, max_power_of_cs=config.max_charging_power)
    traffic_simulator: TrafficSimulator = TrafficSimulatorBuilder.build(time_manager=time_manager,
                                                                       parking_area=parking_area,
                                                                       customers_per_hour=config.customers_per_hour,
                                                                       assigner_mode=config.assigner_mode,
                                                                       max_parking_time=config.max_parking_time,
                                                                       recording_data_path=None)
    

    while time_manager.get_current_time() < time_manager.get_stop_time():

        traffic_simulator.simulate_traffic()
        parking_area.update_parking_area()
        ensure_evs_are_in_charging(parking_area)
        evs = traffic_simulator.arrived_evs
        for ev in evs:
            ev_arrival_recorder.save_ev_data(ev)
        logger.debug(f"Current time: {time_manager.get_current_time()}, added {len(evs)} EVs to the recording.")
        time_manager.perform_time_step()
        logger.debug(f"Current time: {time_manager.get_current_time()} and end time: {time_manager.get_stop_time()}")
    
    ev_arrival_recorder.save_metadata(config)
    ev_arrival_recorder.write_ev_record_to_json()

    logger.info(f"Ev arrival recording generated successfully in path {ev_arrival_recorder.filename_with_path},totally {len(ev_arrival_recorder.ev_data_for_json)} Evs.")



if __name__ == "__main__":
    generate_traffic_sim_recording(config_path=CONFIG_PATH)
