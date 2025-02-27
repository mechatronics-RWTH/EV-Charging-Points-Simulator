import numbers
from gymnasium.spaces import Dict, Box, MultiBinary, Discrete

from Controller_Agent.InterfaceAgent import InterfaceAgent, ensure_positive, TemplateAgent
from Controller_Agent.Rule_based.Stationary_Battery_Controller.AdaptiveStationaryBatteryController import AdaptiveStationaryBatteryController
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from Controller_Agent.Rule_based.ChargingPowerLimiter import ChargingPowerLimiter
import numpy as np
from config.logger_config import get_module_logger

logger =get_module_logger(__name__)


class RuleBasedAgentStatStorage(TemplateAgent,
                                ChargingPowerLimiter):

        def __init__(self,
                     soc_a_limit: numbers.Number=0.95,
                     soc_x_limit: numbers.Number=0.95,
                soc_y_limit: numbers.Number=0.5,
                P_grid_max: PowerType =PowerType(power_in_w=20, unit=PowerTypeUnit.KW)):
                super().__init__()
                ChargingPowerLimiter.__init__(self,P_grid_max)
                self.soc_a_limit = soc_a_limit
                self.soc_x_limit = soc_x_limit
                self.soc_y_limit = soc_y_limit
                self.P_grid_max = P_grid_max


        def _initialize_stationary_battery_controller(self):
                self.stationary_battery_controller = AdaptiveStationaryBatteryController(soc_a_limit=self.soc_a_limit,
                                                                                     soc_x_limit=self.soc_x_limit,
                                                                                     soc_y_limit=self.soc_y_limit,
                                                                                     P_grid_max=self.P_grid_max)
            
        def calculate_action_stationary_battery_controller(self, raw_obs: Dict):
                P_prod = ensure_positive(PowerType(raw_obs["pv_power"][0]))
                building_pwr = ensure_positive(raw_obs["building_power"][0])
                cs_pwr_sum = self.determine_charging_station_power(raw_obs)
                P_load = ensure_positive(PowerType(building_pwr)) + cs_pwr_sum #ensure_positive(PowerType(cs_pwr_sum))
                try:
                        P_batt_chrg_max = ensure_positive(PowerType(raw_obs["stat_battery_chrg_pwr_max"][0]))
                        P_batt_dischrg_max = ensure_positive(PowerType(raw_obs["stat_battery_dischrg_pwr_max"][0]))
                except TypeError as e:
                        raise TypeError(f"Error in RuleBasedAgentStatStorage for {raw_obs}: {e}")
                #P_grid_max = ensure_positive(PowerType(power_in_w=20, unit=PowerTypeUnit.KW))
                self.stationary_battery_controller.step(current_soc=raw_obs["soc_stat_battery"][0],
                                                        P_prod=P_prod,
                                                        P_load=P_load,
                                                        P_batt_chrg_max=P_batt_chrg_max,
                                                        P_batt_dischrg_max=P_batt_dischrg_max
                                                        )
                
                self.action["target_stat_battery_charging_power"] = np.array([self.stationary_battery_controller.charge_power.get_in_w().value], dtype=np.float32)
                                                                                

        def determine_charging_station_power(self, raw_obs: Dict) -> PowerType:
                NOT_FULLY_CHARGED_ENERGY_THRESHOLD = 1000 # Sometimes there is a case where the EV fully charged but the energy request remains at a tiny number
                sum_cs_charging_power: PowerType = PowerType(0, PowerTypeUnit.KW)
                index_field_charged_before = [index for index, value in enumerate(raw_obs["cs_charging_power"]) if value is not None and value > 0]
                index_field_EV_present = [index for index, value in enumerate(raw_obs["energy_requests"]) if value is not None and value > NOT_FULLY_CHARGED_ENERGY_THRESHOLD]
                index_user_request_active = [index for index, value in enumerate(raw_obs["user_requests"]) if value in [1,2,4]]

                # on which chargers is still a vehicle?
                for index in index_field_charged_before:
                        sum_cs_charging_power += PowerType(raw_obs["cs_charging_power"][index])

                # where are new EVs
                for index in index_field_EV_present:
                        if index not in index_field_charged_before and raw_obs["cs_charging_limits"][index] is not None:
                                #logger.error(f" time {raw_obs['current_time']}: {raw_obs['cs_charging_limits'][index]} with index {index} and index_field_EV_present {index_field_EV_present}")
                                sum_cs_charging_power += PowerType(raw_obs["cs_charging_limits"][index])


                # which EVs left?
                for index in index_field_charged_before:
                        if index not in index_user_request_active:
                                sum_cs_charging_power -= PowerType(raw_obs["cs_charging_power"][index])

                return sum_cs_charging_power
                
        def handle_unanswered_requests(self):
                pass

        def request_moving_ginis(self):
                pass

        def limit_charging_power_if_required(self, raw_obs: Dict):
                #pass
                ChargingPowerLimiter.limit_charging_power_if_required(self,raw_obs)