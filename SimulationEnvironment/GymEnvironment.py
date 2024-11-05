from datetime import timedelta
import numpy as np
from SimulationModules.ElectricVehicle.id_register import ID_register
import gymnasium as gym
from SimulationEnvironment.RawEnvSpaces import RawEnvSpaceManager
from SimulationModules.Enums import Request_state
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.ChargingSession import StationaryStorageChargingSession

from SimulationModules.ParkingArea.Parking_Area import ParkingArea
from SimulationModules.TrafficSimulator.TrafficSimulator import TrafficSimulator
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.ParkingArea.ParkingAreaElements import Field
from helpers.Diagnosis import timeit
from typing import List


from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 config: dict,
                 ):
        
        super(CustomEnv, self).__init__()
        
        self.config=config
        self.renderer = None
        self.renderer_initialized=False
        self.current_time=self.config["settings"].start_datetime
        
        self.parking_area=ParkingArea(config=self.config)
        self.area_size=self.parking_area.area_size
        
        self.charging_session_manager=ChargingSessionManager(parking_area=self.parking_area,
                                                             time=self.current_time)     
        self.local_grid: LocalGrid=LocalGrid(price_table=self.config["price_table"],
                                charging_station_list=self.parking_area.get_charging_station_list(),
                                config = self.config)
        self.traffic_simulator= TrafficSimulator(customers_per_hour=self.config["customers_per_hour"],
                                                  parking_area=self.parking_area,
                                                  assigner_mode=config["assigner_mode"],)

        self.raw_env_space_manager=RawEnvSpaceManager(config, 
                                                      self.parking_area,
                                                      self.charging_session_manager,
                                                      self.local_grid
                                                      )    
        self.observation_space_raw=self.raw_env_space_manager.create_observation_space()
        self.action_space_raw=self.raw_env_space_manager.create_action_space()
        self.action_raw_base=self.raw_env_space_manager.create_action_base()
        self.info={}

        self.reset_raw()

    def step(self, action:dict):
        """
        Execute one time step within the environment
        The action is usually provided by the agent
        The structure is based on the 3 part IPO (EVA) 
        principle
        """
        
        self.read_actions(action)
        self.parking_area.step(self.config["settings"].step_time)

        # apply action by updating the charging sessions
        self.charging_session_manager.step(self.config["settings"].step_time)  
        # calculating the grid load based on the uncontrolled and the controlled components
        self.local_grid.step(self.current_time, self.config["settings"].step_time)        
        self.simulate_traffic() 
        self.current_time = self.current_time + self.config["settings"].step_time
    
        self.observation_raw=self.raw_env_space_manager.write_observations(self.current_time)
        

 
        reward= self.calculate_reward_raw()
        terminated=False
        truncated=False
        self.info=self.update_info()


        return self.observation_raw, reward,terminated, truncated, self.info

    def reset(self, seed: int = None, options: dict = None):

        return self.reset_raw(seed= seed, options= options)
    
    def reset_raw(self, seed: int = None, options: dict= None):
        """
        Reset the state of the environment to an initial state
        """
        ID_register.reset()

        soc_stat_battery = [self.local_grid.stationary_battery.get_soc()] if self.local_grid.stationary_battery is not None else None
        stat_battery_chrg_pwr_max = [self.local_grid.stationary_battery.maximum_grid_power.get_in_w().value ] if self.local_grid.stationary_battery is not None else None
        stat_battery_dischrg_pwr_max = [self.local_grid.stationary_battery.minimum_grid_power.get_in_w().value] if self.local_grid.stationary_battery is not None else None

        #at first, we reset the observation space
        price_prediction= self.config["price_table"].get_price_future(date_time=0, horizon = 96, step_time = timedelta(seconds=900))[0]
        
        

        #The Parkinglot gets resetted, so all cars are removed

        #self.parking_area.reset()
        #self.parking_area.update_parking_area()

        self.parking_area=ParkingArea(config=self.config)

        #self.parking_area.park_new_ev()
        #Then the chargingsessionmanager is reinitiated
        self.current_time=self.config["settings"].start_datetime
        self.charging_session_manager: ChargingSessionManager =ChargingSessionManager(self.parking_area, time=self.current_time)
        self.local_grid=LocalGrid(price_table=self.config["price_table"],
                                charging_station_list=self.parking_area.get_charging_station_list(),
                                config = self.config)
        self.traffic_simulator= TrafficSimulator(customers_per_hour=self.config["customers_per_hour"],
                                                  parking_area=self.parking_area,
                                                  assigner_mode=self.config["assigner_mode"],)
        
        if self.local_grid.stationary_battery is not None:

            self.charging_session_manager.start_session(StationaryStorageChargingSession(battery_storage=self.local_grid.stationary_battery,
                                                                                         global_time=self.current_time))
            
        self.raw_env_space_manager=RawEnvSpaceManager(self.config,
                                                      self.parking_area,
                                                      self.charging_session_manager,
                                                      self.local_grid
                                                      )  
        self.observation_raw=self.raw_env_space_manager.reset_obs(price_prediction)
        self.simulate_traffic()
        self.parking_area.step(self.config["settings"].step_time)
        self.observation_raw=self.raw_env_space_manager.write_observations(self.current_time)        
        self.info={}

        return self.observation_raw,{}

    def get_original_obs(self):
        
        return self.observation_raw

    def _get_info(self, observation: dict):
        """
        still in max' old version. has to be adapted to new simulation env
        """
        if isinstance(observation, dict):
            req_energy = observation['requested_energy_kWh']
            time_to_dep = round(observation['time_to_departure_in_s'] / (60 * 60), 3)
            cur_price = round(observation['current_price_in_cent_kWh'], 2)
            chrgn_pow = observation['charging_power']
        else:
            req_energy = observation[2]
            time_to_dep = round(observation[3] / (60 * 60), 3)
            cur_price = round(observation[1], 2)
            chrgn_pow = observation[0]

        info = f"\nActive Session ID {self.charging_session.SessionID}\n" \
               f"Session duration: {self.charging_session.time}\n" \
               f"Requested Energy to target {req_energy} kWh\n" \
               f"Time to departure {time_to_dep} h\n" \
               f"Current price {cur_price} Ct/kWh\n" \
               f"Power {chrgn_pow}kW\n"
        return info

    def render(self, close: bool = False):
        """
        # Render the environment to the screen
        """

        if not self.renderer_initialized:
            from SimulationEnvironment.Renderer.Renderer import InterfaceRenderer, PygameRenderer
            self.renderer = PygameRenderer(self,video_path="OutputData\\videos\\Final_presentation_Gini_Sim.mp4")
            self.renderer_initialized = True
        #self.local_grid.plot_consumption(self.current_time)
        self.renderer.render(close=close)

    def read_actions(self, action: dict):
        self.raw_env_space_manager.validate_to_fit_space(self.action_space_raw, action)
        self.charging_session_manager.set_request_commands(action["request_answer"]) 
        self.parking_area.set_gini_targets(action["requested_gini_field"])
        self.parking_area.set_new_gini_max_limits(action["requested_gini_power"])
        self.parking_area.set_new_cs_max_limits(action["target_charging_power"])
        self.read_new_stat_storage_target(action["target_stat_battery_charging_power"])    


    #region methods for reading the agents input
    def read_new_request_answers(self, request_commands: np.array):
        """
        this method is used to take the requests sent by the agent and
        integrate them into the Simulation environment. If a non existing 
        request is confirmed/denied, the system will ignore it. 
        """
        if request_commands is not None:
            self.charging_session_manager.set_request_commands(request_commands)
   
    def read_new_gini_targets(self, gini_targets: np.array):

        self.parking_area.set_gini_targets(gini_targets)

    def read_new_gini_max_limits(self, gini_power_limits: np.array):
        if gini_power_limits is not None:
            for i, gini in enumerate(self.parking_area.ginis):
                if gini_power_limits[i] is not None:
                    gini.set_agent_power_limit_max(gini_power_limits[i])

    def read_new_cs_max_limits(self, target_charging_powers: np.array):
        fields: List[Field]=self.parking_area.parking_area_fields
        for field in fields:
            if field.has_charging_station():
                if target_charging_powers[field.index] is not None:
                    
                    field.charger.set_target_grid_charging_power(PowerType(
                        target_charging_powers[field.index], 
                        PowerTypeUnit.W)                 
                    )
                else:
                    field.charger.set_target_grid_charging_power()

    def read_new_stat_storage_target(self, target_charging_powers: np.array):
        target_power: PowerType = PowerType(target_charging_powers[0], PowerTypeUnit.W) if target_charging_powers is not None else None
        if self.local_grid.stationary_battery is not None:
            if target_charging_powers is not None:
                self.local_grid.stationary_battery.set_target_grid_charging_power(target_power)
    #endregion

    #region methods for calculating the reward
    def calculate_reward_raw(self):
        """
        the reward function depends on the structure of the agents. Thats why,
        its recalculated in the child class of this environment, where
        feature engineering and Agent design takes place. However, in this place,
        a reward is calculated to compare different Agent designs.
        """
        weight_not_satisfied=self.raw_env_space_manager.weights_for_reward["weight_not_satisfied"]
        weight_rejection=self.raw_env_space_manager.weights_for_reward["weight_rejection"]
        weight_energy_consumption=self.raw_env_space_manager.weights_for_reward["weight_energy_consumption"]

        reward_not_satisfied=       weight_not_satisfied * self.calculate_cost_departing_ev_request_not_satisfied()
        reward_rejection=           weight_rejection * self.calculate_amount_evs_rejected()
        reward_energy_consumption=  weight_energy_consumption * self.calculate_cost_energy_consumption()

        #print(f"reward_not_satisfied: {reward_not_satisfied}, reward_rejection: {reward_rejection}, reward_energy_consumption: {reward_energy_consumption}")

        reward=0
        reward-=reward_not_satisfied
        reward-=reward_rejection
        reward-=reward_energy_consumption

        return reward

    def calculate_cost_departing_ev_request_not_satisfied(self):
        
        user_dissatisfaction_cost=0
        for ev in self.parking_area.departed_ev_list:
            user_dissatisfaction_cost += ev.current_energy_demand.get_in_kwh().value

        return user_dissatisfaction_cost

    def calculate_amount_evs_rejected(self):

        return self.charging_session_manager.denied_requests_amount_step
      
    def calculate_cost_energy_consumption(self):
        
        cost=self.local_grid.get_energy_costs_step()
        if cost is None:
            cost=0
       
        return cost

    def calculate_amount_satisfied_evs_step(self):

        amount_dissatisfied_evs=0
        amount_satisfied_evs=0
        for ev in self.parking_area.departed_ev_list:
            if ev.get_initial_request_state() == Request_state.CONFIRMED:
                if ev.current_energy_demand.get_in_kwh().value > 0:
                    amount_dissatisfied_evs+=1
                else:
                    amount_satisfied_evs+=1

        return amount_satisfied_evs, amount_dissatisfied_evs  

    def calculate_amount_evs_confirmed(self):

        return self.charging_session_manager.confirmed_requests_amount_step
    
    #endregion

    def simulate_traffic(self):
        """
        the prupose of this method is to let new evs come to the parking
        lot and let those leave who want
        """
      
        self.traffic_simulator.simulate_traffic(step_time=self.config["settings"].step_time, 
                                                               time=self.current_time, 
                                                               max_parking_time=self.config["max_parking_time"])


        self.parking_area.ev_departures(self.current_time)

        self.charging_session_manager.handle_requests()
        
        for gini in self.parking_area.ginis:
            gini.update_position(distances_for_indices=self.parking_area.distances_for_indices,
                                 step_time=self.config["settings"].step_time)
        
    def update_info(self):

        info=self.info
        
        for key, value in [("Confirmed EVs", self.calculate_amount_evs_confirmed()),
                           ("Denied EVs", self.calculate_amount_evs_rejected()),
                           ("Satisfied EVs", self.calculate_amount_satisfied_evs_step()[0]),
                           ("Dissatisfied EVs", self.calculate_amount_satisfied_evs_step()[1]),
                           ("KWH not charged", self.calculate_cost_departing_ev_request_not_satisfied()),
                           ("Energy Cost",  self.calculate_cost_energy_consumption())]:
            if key not in info:
                info[key]=value
            else:
                info[key]+=value

        return info
