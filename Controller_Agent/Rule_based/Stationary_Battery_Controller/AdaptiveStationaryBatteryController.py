import numbers
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from Controller_Agent.Rule_based.Stationary_Battery_Controller.OperatingStrategy import (ChargingStrategy, 
                                                                                         DischargingStrategy, 
                                                                                         OperatingStrategy,
                                                                                         OptimizingSelfConsumption,
                                                                                         SurplusCharging, 
                                                                                         Context)
from typing import List


from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class AdaptiveStationaryBatteryController:
    def __init__(self,
                 soc_a_limit: float,
                 soc_x_limit: float,
                 soc_y_limit: float,
                 P_grid_max: PowerType = None,):
        self.battery_soc = None
        self.soc_a_limit = soc_a_limit
        self.soc_x_limit = soc_x_limit
        self.soc_y_limit = soc_y_limit
        self.P_grid_max = PowerType(0, unit=PowerTypeUnit.KW) if P_grid_max is None else P_grid_max
        self.context = Context(P_prod=PowerType(0, unit=PowerTypeUnit.KW),
                               P_load=PowerType(0, unit=PowerTypeUnit.KW),
                                P_batt_chrg_max=PowerType(0, unit=PowerTypeUnit.KW),
                               P_batt_dischrg_max=PowerType(0, unit=PowerTypeUnit.KW),
                               P_grid_max=self.P_grid_max,
                               soc_a_limit=soc_a_limit,
                               soc_x_limit=soc_x_limit,
                               soc_y_limit=soc_y_limit,
                               battery_soc=self.battery_soc)
        self.charging_strategy: ChargingStrategy = SurplusCharging(context=self.context)
        self.discharging_strategy: DischargingStrategy = OptimizingSelfConsumption(context=self.context)
        

    def determine_soc_limit_parameters(self):
        raise NotImplementedError

    def step(self,
             current_soc: float,
             P_prod: PowerType,
             P_load: PowerType,
             P_batt_chrg_max: PowerType,
             P_batt_dischrg_max: PowerType,
             P_grid_max: PowerType = None ,
            ):
        P_grid_max = self.P_grid_max if P_grid_max is None else P_grid_max
        self.update_state(current_soc=current_soc,
                          P_prod=P_prod,
                          P_load=P_load,
                          P_batt_chrg_max=P_batt_chrg_max,
                          P_batt_dischrg_max=P_batt_dischrg_max,
                          P_grid_max=P_grid_max)
        self.determine_charging_strategy()
        self.determine_discharging_strategy()
        self.calculate_charge()        

    def update_state(self, 
                     current_soc: numbers.Number,
                     P_prod: PowerType,
                     P_load: PowerType,
                     P_batt_chrg_max: PowerType,
                     P_batt_dischrg_max: PowerType,
                     P_grid_max: PowerType,):
        strategies: List[OperatingStrategy] = [self.charging_strategy, self.discharging_strategy]
        for strategy in strategies:
            strategy.context.battery_soc = current_soc
            strategy.context.P_prod = P_prod
            strategy.context.P_load = P_load
            strategy.context.P_batt_chrg_max = P_batt_chrg_max
            strategy.context.P_batt_dischrg_max = P_batt_dischrg_max
            strategy.context.P_grid_max = P_grid_max
            strategy.context.soc_a_limit = self.soc_a_limit
            strategy.context.soc_x_limit = self.soc_x_limit
            strategy.context.soc_y_limit = self.soc_y_limit


    def determine_charging_strategy(self):
        self.charging_strategy = self.charging_strategy.process()
    
    def determine_discharging_strategy(self):
        self.discharging_strategy = self.discharging_strategy.process()
    
    def calculate_charge(self) -> PowerType:
        
        charge_power = self.charging_strategy.calculate_charge()
        discharge_power = self.discharging_strategy.calculate_charge()
        self.charge_power: PowerType = charge_power + discharge_power*(-1)
        #self.charge_power: PowerType = charge_power + discharge_power*(-1)
        logger.debug(f"Charge power: {charge_power}, discharge power: {discharge_power}")
        
    
    

    

