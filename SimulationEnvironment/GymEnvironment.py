from datetime import timedelta
import numpy as np
from SimulationModules.ElectricVehicle.id_register import ID_register
import gymnasium as gym
from SimulationEnvironment.RawEnvSpaces import RawEnvSpaceManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.Reward.InterfaceReward import InterfaceReward
from datetime import datetime
from config.definitions import VIDEO_DIR
from SimulationEnvironment.EnvBuilder import EnvBuilder
from SimulationEnvironment.EnvConfig import EnvConfig


from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 config: EnvConfig,
                 ):
        
        super(CustomEnv, self).__init__()
        
        self.config=config
        self.renderer = None
        self.renderer_initialized=False
        #self.current_time=
        self.env_builder=EnvBuilder(env_config=config)
        self.time_manager: InterfaceTimeManager=self.env_builder.build_time_manager()
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
        self.parking_area.update_parking_area()
        self.gini_mover.move_ginis()
        # apply action by updating the charging sessions
        self.charging_session_manager.step()  
        # calculating the grid load based on the uncontrolled and the controlled components
        self.local_grid.calculate_connection_point_load()
        self.energy_cost.calculate_energy_costs_step()     
        self.traffic_simulator.simulate_traffic()
        
        self.time_manager.perform_time_step()
        self.reward_manager.update_all_metrics()
        #self.current_time = self.current_time + self.config["settings"].step_time
    
        self.observation_raw=self.raw_env_space_manager.write_observations()
        self.reward_manager.calculate_combined_step_reward()
        reward= self.reward_manager.get_combined_step_reward()
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
        self.time_manager.reset_start_time(self.config.start_datetime)
        ID_register.reset()

        #TODO: A dedicated reset without recreating all the objects would be more efficient
        self.time_manager.reset_time()
        self.parking_area= self.env_builder.build_parking_area()
        self.parking_area.request_collector.clear_requests()
        self.traffic_simulator= self.env_builder.build_traffic_simulator()
        self.local_grid=self.env_builder.build_local_grid()
        self.charging_session_manager= self.env_builder.build_charging_session_manager()
        self.energy_cost: ElectricityCost = self.env_builder.build_electricity_cost()        
        self.gini_mover = self.env_builder.build_gini_mover()
        self.reward_manager: InterfaceReward = self.env_builder.build_reward_system()
        #TODO: This does not seem very elegant
        price_prediction=self.energy_cost.price_table.get_price_future(self.time_manager.get_current_time(), horizon=24)[0]
        
        self.local_grid.calculate_connection_point_load()  
        self.traffic_simulator.simulate_traffic()
        self.parking_area.update_field_states()
        self.raw_env_space_manager=RawEnvSpaceManager(config=self.config, 
                                                      parking_area=self.parking_area,
                                                      charging_session_manager=self.charging_session_manager,
                                                      local_grid=self.local_grid,
                                                      gini_mover=self.gini_mover,
                                                        time_manager=self.time_manager,
                                                      ) 
        
        self.observation_space_raw=self.raw_env_space_manager.create_observation_space()
        self.action_space_raw=self.raw_env_space_manager.create_action_space()
        self.action_raw_base=self.raw_env_space_manager.create_action_base()
        self.observation_raw=self.raw_env_space_manager.reset_obs(price_prediction)
        self.observation_raw=self.raw_env_space_manager.write_observations()        
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
            video_path = VIDEO_DIR / f"Gini_Sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            self.renderer = PygameRenderer(self,video_path=video_path)
            self.renderer_initialized = True
        #self.local_grid.plot_consumption(self.current_time)
        self.renderer.render(close=close)

    def read_actions(self, action: dict):
        self.raw_env_space_manager.validate_to_fit_space(self.action_space_raw, action)
        self.charging_session_manager.set_request_commands(action["request_answer"]) 
        self.gini_mover.set_gini_targets(action["requested_gini_field"])
        self.gini_mover.set_new_gini_max_limits(action["requested_gini_power"])
        self.parking_area.set_new_cs_max_limits(action["target_charging_power"])
        self.read_new_stat_storage_target(action["target_stat_battery_charging_power"])    


    def read_new_stat_storage_target(self, target_charging_powers: np.array):
        target_power: PowerType = PowerType(target_charging_powers[0], PowerTypeUnit.W) if target_charging_powers is not None else None
        if self.local_grid.stationary_battery is not None:
            if target_charging_powers is not None:
                self.local_grid.stationary_battery.set_target_grid_charging_power(target_power)
    #endregion

    def update_info(self):
        user_satisfaction_metric = self.reward_manager.get_metrik_by_name(name="user_satisfaction")
        info=self.info


        info["Confirmed EVs"]=user_satisfaction_metric.calculate_amount_evs_confirmed()
        info["Denied EVs"]=user_satisfaction_metric.calculate_amount_evs_rejected()
        info["Satisfied EVs"]= user_satisfaction_metric.calculate_amount_evs_satisfied()
        info["Dissatisfied EVs"]=user_satisfaction_metric.calculate_amount_evs_unsatisfied()
        info["kWh not charged"]=user_satisfaction_metric.calculate_not_satisfied_kwH()
        info["kWh charged"]=user_satisfaction_metric.calculate_kWh_charged()
        self.reward_manager.update_total_reward_dictionary()
        reward_dict  = self.reward_manager.get_total_reward_dictionary()
        info={**info, **reward_dict}
        logger.info(info)

        return info
