from gymnasium.spaces import Dict, Box, MultiBinary, Discrete

from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from Controller_Agent.InterfaceAgent import ensure_positive
from abc import ABC, abstractmethod
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class InterfaceChargingPowerLimiter(ABC):
      
    @abstractmethod
    def limit_charging_power_if_required(self, raw_obs):
        pass



class ChargingPowerLimiter():
    
    def __init__(self,
                 P_grid_max: PowerType):
        self.P_grid_max = P_grid_max
        self.charging_spot_list = []
        self.occupied_charging_spot_index = []
        self.action = {}

    def limit_charging_power_if_required(self, 
                                         raw_obs: dict, 
                                         occupied_charging_spot_index: list = []
                                         ):
        P_res = self.determine_residual_power(raw_obs)
        self.set_cs_target_power(P_res)

            
            
    def determine_residual_power(self, raw_obs:Dict) -> PowerType:
        P_prod = ensure_positive(PowerType(raw_obs["pv_power"][0]))
        building_pwr = ensure_positive(raw_obs["building_power"][0])
     
        
        p_load_in_W = building_pwr
        P_load = ensure_positive(PowerType(p_load_in_W))

        if self.action["target_stat_battery_charging_power"]:
            if self.action["target_stat_battery_charging_power"][0] >0:
                P_load = P_load + PowerType(self.action["target_stat_battery_charging_power"][0])

            elif self.action["target_stat_battery_charging_power"][0] <0:
                P_prod = P_prod + PowerType(self.action["target_stat_battery_charging_power"][0]*(-1))
                
            
        P_res = self.P_grid_max +(P_prod - P_load)
        logger.debug(f"Residual Power: {P_res}")
        if P_res < 0:
                P_res = PowerType(0)
        return P_res
    
    def set_cs_target_power(self, 
                            P_res: PowerType
                            ):
        num_cs_with_ev = len(self.occupied_charging_spot_index)
        logger.debug(f"Num CS with EV: {num_cs_with_ev}")

        if num_cs_with_ev > 0:
            P_grid_max_per_cs: PowerType = P_res / num_cs_with_ev
            logger.debug(f"P max per cs: {P_grid_max_per_cs}")
            for charging_spot_index in self.occupied_charging_spot_index:
                self.action["target_charging_power"][charging_spot_index] = P_grid_max_per_cs.get_in_w().value
