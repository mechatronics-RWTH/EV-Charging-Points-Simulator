from helpers.JSONSaver import JsonReader
import numpy as np
from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationEnvironment.EnvConfig import EnvConfig
from typing import List
from config.logger_config import get_module_logger
from SimulationModules.Enums import Request_state
from helpers.DataAnalyzer.EvSessionPeriods import EvSessionPeriod
from helpers.DataAnalyzer.ObservationSessionReader import ObservationSessionReader
import math 

logger = get_module_logger(__name__)

def make_np_array_if_needed(data):
    if isinstance(data, list):
        return np.array(data).flatten()
    return data


class DataAnalyzer: 

    def __init__(self, 
                 filename: str) -> None:
        self.file_to_analyze = filename
        self.config_filename = str(filename).replace("_trace", "_config")
        self.json_reader = JsonReader(filename=self.file_to_analyze)
        self.data = self.json_reader.read_data()
        self.calculate_time_data()
        self.ev_session_periods: List[EvSessionPeriod] = []
        self.session_from_observation = ObservationSessionReader()
        #self.get_ev_session()

    def get_start_date(self):
        self.env_config = EnvConfig.load_env_config(config_file=self.config_filename)
        return self.env_config.start_datetime


    def get_observation_by_name(self, 
                                name: str):

        observation = [data["observations"][name] for data in self.data]
        return observation
    
    def get_action_by_name(self,name:str):
        action = [data["actions"][name] for data in self.data]
        return action
    

    
    def correct_time_by_offset(self):
        self.time_data = make_np_array_if_needed(self.time_data)
        time_offset = 0
        for index,time in enumerate(self.time_data):
            if index == 0:
                continue
             
            if time + time_offset < self.time_data[index-1]:
                time_offset = self.time_data[index-1]
            self.time_data[index] = time + time_offset

    def calculate_time_data(self):
        self.time_data = self.get_observation_by_name("current_time")
        self.correct_time_by_offset()
    
    def get_energy_cost(self):
        grid_power = self.get_grid_power()
        grid_power[grid_power>0] =0

        electricity_price = self.get_electricity_price()

        delta_time = self.time_data[1] - self.time_data[0]
        energy_cost_list = grid_power/1000 * electricity_price/1000*delta_time/3600
        energy_cost = np.cumsum(energy_cost_list)
        return energy_cost
    
    def get_electricity_price(self):
        electricity_table = self.get_observation_by_name("price_table")
        first_entries = np.array([row[0] for row in electricity_table])
        return first_entries
    
    def get_ev_depature_energy_over_time_in_kWh(self):       
        
        #departure_energies_over_time = self._get_depature_energy_with_list_entries()
        total_depature_energy_over_time = []
        energy_offset = EnergyType(energy_amount_in_j=0)
        for index,time_step in enumerate(self.time_data):
            energy_for_sessions_ending_in_time_step = sum([session.get_departure_energy_request() for session in self.ev_session_periods if session.end_index == index])
            energy_offset += energy_for_sessions_ending_in_time_step
            total_depature_energy_over_time.append(energy_offset)
        return total_depature_energy_over_time
    
   
    def get_ev_depatrue_energy(self):
        departure_energies = []
        if len(self.ev_session_periods)==0:
            self.get_ev_session()
        for ev_session in self.ev_session_periods:
            departure_energies.append(EnergyType(energy_amount_in_j=np.sum(ev_session.energy_request)).get_in_j().value)
        return departure_energies
    
  
    def get_ev_session(self):
        self.session_from_observation.set_user_requests(self.get_observation_by_name('user_requests'))
        self.session_from_observation.set_energy_requests(self.get_observation_by_name('energy_requests'))
        self.session_from_observation.read_sessions_from_requests()
        self.ev_session_periods = self.session_from_observation.ev_session_periods
       

    def get_cs_power(self):
        cumulated_power = []
        cs_power_over_time = self.get_observation_by_name('cs_charging_power')
        for cs_pwr in cs_power_over_time:
            if not cs_pwr:
                cumulated_power.append(0)
                continue
            cumulated_power.append(np.sum(cs_pwr))
        return make_np_array_if_needed(cumulated_power)
    
    def get_grid_power(self):
        grid_power = self.get_observation_by_name('grid_power')
        return make_np_array_if_needed(grid_power)
    
    def get_building_power(self):
        building_power = self.get_observation_by_name('building_power')
        return make_np_array_if_needed(building_power)
    
    def get_gini_energy(self):
        gini_energy=[]
        gini_energy_data= self.get_observation_by_name("gini_energy")
        if not gini_energy_data or all(not sublist for sublist in gini_energy_data):
            raise ValueError("No Gini Energy available")
        for _ in gini_energy_data[0]:
            gini_energy.append([])
        for step_time_data in gini_energy_data:
            for (index, data) in step_time_data:
                gini_energy_val= EnergyType(energy_amount_in_j=data).get_in_kwh().value
                gini_energy[int(index)].append(gini_energy_val)
        return gini_energy
    
    def get_gini_soc(self):
        gini_soc=[]
        gini_soc_data= self.get_observation_by_name("soc_ginis")
        if not gini_soc_data or all(not sublist for sublist in gini_soc_data):
            raise ValueError("No Gini SOC available")
        for _ in gini_soc_data[0]:
            gini_soc.append([])
        for step_time_data in gini_soc_data:
            for (index, data) in step_time_data:
                gini_soc_val= data
                gini_soc[int(index)].append(gini_soc_val)
        return gini_soc
    
    def get_gini_power(self):
        gini_power=[]
        gini_power_data= self.get_observation_by_name("gini_charging_power")
        if not gini_power_data or all(not sublist for sublist in gini_power_data):
            raise ValueError("No Gini Power available")
        for _ in gini_power_data[0]:
            gini_power.append([])
        for step_time_data in gini_power_data:
            for (index, data) in step_time_data:
                gini_power_val= data
                gini_power[int(index)].append(gini_power_val)
        return gini_power

    
    def get_pv_power(self):
        pv_power = self.get_observation_by_name('pv_power')
        return make_np_array_if_needed(pv_power)
    
    
    
    def get_ev_energy_requests(self):
        total_ev_energy_req=[]
        
        for energy_requests_at_step_time in self.get_observation_by_name('energy_requests'):
            total_ev_energy_req_at_step_time = EnergyType(energy_amount_in_j=0).get_in_kwh()
            for energy_request in energy_requests_at_step_time:
                ev_energy = EnergyType(energy_amount_in_j=energy_request[1]).get_in_kwh()
                total_ev_energy_req_at_step_time += ev_energy
            total_ev_energy_req.append(total_ev_energy_req_at_step_time.get_in_kwh().value)
        return make_np_array_if_needed(total_ev_energy_req)
    
    def get_amount_of_evs(self):
        
        amount_evs= [len(obs) for obs in self.get_observation_by_name('charging_states')]
        return make_np_array_if_needed(amount_evs)
    
    def get_config_data_as_string(self):
        config_data = EnvConfig.load_env_config(config_file=self.config_filename)
        output = ""
        for key, value in config_data.items():
            if isinstance(value, list) and len(value) > 10:
                continue
            output += "%-30s: %s\n" % (key, value)
        return output
    
    def get_maximum_grid_power(self):
        config_data =EnvConfig.load_env_config(config_file=self.config_filename)
        return config_data.max_grid_power.get_in_kw().value
    
    def get_total_amount_of_ev(self):
        return len(self.ev_session_periods)
    
    def get_charged_energy_over_time(self):
        total_charged_energy_over_time = []
        energy_offset = EnergyType(energy_amount_in_j=0)
        for index,time_step in enumerate(self.time_data):
            energy_for_sessions_ending_in_time_step = sum([session.charged_energy for session in self.ev_session_periods if session.end_index == index])
            energy_offset += energy_for_sessions_ending_in_time_step
            total_charged_energy_over_time.append(energy_offset)
        return total_charged_energy_over_time
    

    def get_charged_energy_over_time_continuous(self):
        total_charged_energy_over_time = []
        energy_offset = EnergyType(energy_amount_in_j=0)
        for index,time_step in enumerate(self.time_data):
            active_sessions = [session for session in self.ev_session_periods if index > session.start_index and index <= session.end_index]
            
            #print(f"for index {index} following active session {active_sessions}")

            delta_energy_for_active_sessions = EnergyType(0)
            for session in active_sessions:
                try:
                    delta_energy_for_session=session.energy_request[index-session.start_index-1] - session.energy_request[index-session.start_index]
                    #TODO: Fix this, getting this error too often 
                    if delta_energy_for_session < 0:
                        raise ValueError(f"Negative energy for {session}")
                    delta_energy_for_active_sessions += delta_energy_for_session
                except IndexError as e:
                    logger.debug(e)
                except ValueError as e:
                    logger.error(e)
                
                #sum([session.energy_request[index-session.start_index-1]-session.energy_request[index-session.start_index] for session in active_sessions if len(session.energy_request)>1])
            energy_offset += delta_energy_for_active_sessions
            total_charged_energy_over_time.append(energy_offset)
        return total_charged_energy_over_time

    
    def get_stationary_storage_power(self):
        return make_np_array_if_needed(self.get_observation_by_name('stat_batt_power'))
    
    def get_stationary_storage_soc(self):
        if self.get_observation_by_name('soc_stat_battery')[0] == 'Type not convertable':
            raise ValueError("Stationary Storage not available")
        return make_np_array_if_needed(self.get_observation_by_name('soc_stat_battery'))
    
    def has_stationary_storage(self) -> bool:
        try:
            self.get_stationary_storage_soc()
        except ValueError as e:
            return False
        return True
    
    def has_ginis(self) -> bool:
        try:
            self.get_gini_energy()
        except ValueError as e:
            return False
        return True
    
    def get_num_ev_sessions(self):
        return len(self.ev_session_periods)
    

    def get_num_ev_sessions_charged(self):
        return len([session for session in self.ev_session_periods if session.charged_energy != 0])
    
    def get_average_amount_charged(self) -> EnergyType:
        return np.mean([session.charged_energy for session in self.ev_session_periods if session.charged_energy != 0])
    
    def print_charged_energy_and_status(self):
        for session in self.ev_session_periods:
            print(f" status: {session.status} and charged energy {session.charged_energy.get_in_kwh().value} kWh")


    def compare_battery_target_and_observation(self):
        target_battery_charging_power = [target[0][1] for target in self.get_action_by_name('target_stat_battery_charging_power')]     
        #print(target_battery_charging_power)
        stat_battery_charging_power = [power[0] for power in self.get_observation_by_name('stat_batt_power')]
        battery_soc = self.get_stationary_storage_soc()
        pwr_max = self.get_observation_by_name('stat_battery_chrg_pwr_max')
        pwr_min = self.get_observation_by_name('stat_battery_dischrg_pwr_max')
        for index, (target_power, stat_power) in enumerate(zip(target_battery_charging_power, stat_battery_charging_power)):
            if not math.isclose(target_power, stat_power):
                print(f"Index {index} Target Power {target_power} and Stat Power {stat_power} with SoC {battery_soc[index]} and limit {pwr_max[index]} and {pwr_min[index]}")

    def get_total_energy_charged(self):
        return sum([session.get_charged_energy() for session in self.ev_session_periods])

if "__main__" == __name__:
    filename = "OutputData\\logs\\save_as_json_logs\\run_2024-11-17_17-29-09\\run_2024-11-17_17-29-09_trace.json"
    #"OutputData\\logs\\save_as_json_logs\\run_2024-07-26_15-12-36\\run_2024-07-26_15-12-36_trace.json"

    data_analyzer = DataAnalyzer(filename=filename)
    #print(data_analyzer.get_num_ev_sessions())
    data_analyzer.get_ev_session()
    for session in data_analyzer.ev_session_periods:
        print(f"{session}")
    print(data_analyzer.get_charged_energy_over_time_continuous()[-1].get_in_kwh())
    print(data_analyzer.get_total_energy_charged())
    print(data_analyzer.get_total_amount_of_ev())

    #print(len(data_analyzer.session_from_observation.user_requests))
    #for session in data_analyzer.ev_session_periods:
    #    print(f"{session.id}: {[energy_request.get_in_kwh() for energy_request in session.energy_request ]}")
    #print(f"Energy charged total {data_analyzer.get_charged_energy_over_time().get_in_kwh().value} kWh")
    #data_analyzer.compare_battery_target_and_observation()
    #print(f" {data_analyzer.get_num_ev_sessions_charged()} of {data_analyzer.get_num_ev_sessions()} EVs charged")
    #print(f"Average amount charged {data_analyzer.get_average_amount_charged().get_in_kwh().value} kWh")

