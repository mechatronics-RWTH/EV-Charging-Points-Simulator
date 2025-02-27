from abc import ABC, abstractmethod
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from dataclasses import dataclass

from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

@dataclass
class Context:
    P_prod: PowerType
    P_load: PowerType
    P_grid_max: PowerType

    P_batt_chrg_max: PowerType
    P_batt_dischrg_max: PowerType
    battery_soc: float
    soc_x_limit: float
    soc_y_limit: float
    soc_a_limit: float
    hysteresis_val: float = 0.01
    P_batt_max: PowerType = None 

class OperatingStrategy(ABC):
    def __init__(self, context):
        self.context: Context = context





    def calculate_charge(self):
        assert self.context.P_batt_chrg_max >= 0
        assert self.context.P_batt_dischrg_max >= 0
        assert self.context.P_prod >= 0
        assert self.context.P_load >= 0
        assert self.context.P_grid_max > 0

        logger.debug(f"Battery max {self.context.P_batt_chrg_max}, Battery discharge max {self.context.P_batt_dischrg_max}, P_prod {self.context.P_prod}, P_load {self.context.P_load}, P_grid_max {self.context.P_grid_max}")
        logger.debug(self.__class__.__name__)
        

    def process(self):
        pass

class ChargingStrategy(OperatingStrategy):
    def calculate_charge(self):
        super().calculate_charge()
        self.context.P_batt_max = self.context.P_batt_chrg_max
    

class DischargingStrategy(OperatingStrategy):
    def calculate_charge(self):
        super().calculate_charge()
        self.context.P_batt_max = self.context.P_batt_dischrg_max

class SurplusCharging(ChargingStrategy):
    def calculate_charge(self):
        super().calculate_charge()

        if self.context.P_prod > self.context.P_load:
            charge_power = min(self.context.P_prod - self.context.P_load, self.context.P_batt_max)
        else:
            charge_power = PowerType(0) 
        return charge_power
    
    def process(self):
        if self.context.battery_soc < self.context.soc_x_limit - self.context.hysteresis_val:
            return LocalCharging(self.context)
        else:
            return self

class LocalCharging(ChargingStrategy):
    def calculate_charge(self):
        super().calculate_charge()

        self.P_res = max(self.context.P_load - self.context.P_grid_max, PowerType(0))
        if self.context.P_prod > self.P_res:
            charge_power = min(self.context.P_prod - self.P_res, self.context.P_batt_max)
        else:
            charge_power = 0
        return charge_power
    
    def process(self):
        if self.context.battery_soc < self.context.soc_y_limit - self.context.hysteresis_val:
            return GridCharging(self.context)
        elif self.context.battery_soc > self.context.soc_x_limit + self.context.hysteresis_val:
            return SurplusCharging(self.context)
        else:
            return self

class GridCharging(ChargingStrategy):
    def calculate_charge(self):
        super().calculate_charge()

        if self.context.P_load < self.context.P_grid_max:
            charge_power = min(self.context.P_grid_max - self.context.P_load, self.context.P_batt_max)
        else:
            charge_power = PowerType(0)
        return charge_power
    
    def process(self):
        if self.context.battery_soc > self.context.soc_y_limit + self.context.hysteresis_val:
            return LocalCharging(self.context)
        else:
            return self

class OptimizingSelfConsumption(DischargingStrategy):
    def calculate_charge(self):
        super().calculate_charge()
        print(f"Load: {self.context.P_load}, Prod: {self.context.P_prod}, Batt_max {self.context.P_batt_max}")
        if self.context.P_load > self.context.P_prod:
            charge_power = min(self.context.P_load - self.context.P_prod, self.context.P_batt_max)
        else:
            charge_power = PowerType(0)
        return charge_power
    
    def process(self) -> DischargingStrategy:
        if self.context.battery_soc < self.context.soc_a_limit - self.context.hysteresis_val:
            return LimitingPeakLoad(self.context)
        else:
            return self

class LimitingPeakLoad(DischargingStrategy):
    def calculate_charge(self):
        super().calculate_charge()

        if (self.context.P_load - self.context.P_prod) > self.context.P_grid_max:
            charge_power = min(self.context.P_load - self.context.P_prod - self.context.P_grid_max, self.context.P_batt_max)
        else:
            charge_power = PowerType(0)
        return charge_power
    
    def process(self) -> DischargingStrategy:
        if self.context.battery_soc > self.context.soc_a_limit + self.context.hysteresis_val:
            return OptimizingSelfConsumption(self.context)
        else:
            return self
