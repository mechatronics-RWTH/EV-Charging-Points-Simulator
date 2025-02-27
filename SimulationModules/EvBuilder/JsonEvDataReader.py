from datetime import datetime, timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit#
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import json
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.PowerMap import EmpiricPowerMapFactory, InterfaceChargingPowerMap, TypeOfChargingCurve
from typing import List
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

empiric_power_map_factory = EmpiricPowerMapFactory()

class JsonEvDataReader:
    def __init__(self,
                 path_to_ev_record: str = None,
                 ):
        self.Evs_from_json: List[EV] = []
        self.file_path: str = "test\\arriving_evs_record_test.json" if path_to_ev_record is None else path_to_ev_record
        self.ev_data = []


    def getArrivingEVsFromJSON(self, path_to_ev_record: str = None):
        if path_to_ev_record is not None:
            self.file_path = path_to_ev_record

        if(self.file_path == "" or self.file_path == None):
            raise ValueError("No path to EV record specified. Specify path in the selected config file")
        with open(self.file_path, 'r') as file: 
            file_data = json.load(file) 
            self.get_ev_data_from_file(file_data)
        for json_ev in self.ev_data:
            arrival_time = datetime.strptime(json_ev['arrival_time'], '%Y-%m-%d %H:%M:%S')
            stay_duration = datetime.strptime(json_ev['departure_time'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(json_ev['arrival_time'], '%Y-%m-%d %H:%M:%S')
            energy_demand = EnergyType(float(json_ev['energy_demand_at_arrival']), EnergyTypeUnit.KWH)
            parking_spot_index = int(json_ev['parking_spot_id'])

            ev = EV(arrival_time=arrival_time,
                    stay_duration=stay_duration,
                    energy_demand=energy_demand,
                    battery = self.get_battery_data_from_file(json_ev)
                    )
            ev.parking_spot_index = parking_spot_index
            self.Evs_from_json.append(ev)

    def get_battery_data_from_file(self,json_ev):

        if 'power_map_type' not in json_ev['battery'] or json_ev['battery']['power_map_type'] == "None":
            power_map = empiric_power_map_factory.get_power_map_by_type(type=TypeOfChargingCurve.LIMOUSINE)
        else:
            
            power_map = empiric_power_map_factory.get_power_map_by_type(type=json_ev['battery']['power_map_type'],
                                                                    maximum_power=PowerType(float(json_ev['battery']['maximum_charging_power']), PowerTypeUnit.KW),
                                                                    minimum_power=PowerType(float(json_ev['battery']['maximum_discharging_power']), PowerTypeUnit.KW))
        battery = Battery(battery_energy=EnergyType(float(json_ev['battery']['battery_energy']), EnergyTypeUnit.KWH),
                            present_energy=EnergyType(float(json_ev['battery']['present_energy']), EnergyTypeUnit.KWH),
                            power_map=power_map
                            )
        
        return battery

    def get_ev_data_from_file(self,file_data):
        if isinstance(file_data, dict):
            self.ev_data = file_data["ev_data"]
        else:
            self.ev_data = file_data

        
