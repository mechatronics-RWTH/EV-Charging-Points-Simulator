from abc import ABC, abstractmethod
from typing import Union
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingStation.EfficiencyMap import InterfaceEfficiencyMap, EfficiencyMap, ConstantEfficiencyMap
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class ElectricalGridConsumer(ABC):
    """
    This base class, ElectricalGridConsumer, has attributes for the consumer's name
    and maximum power consumption. It also tracks the power consumed and provides methods
    for consuming power, getting the remaining power capacity, and displaying information about the consumer.
    """
    def __init__(self, name: str):
        self.name = name
        self.power_consumed = 0

    @abstractmethod
    def get_power_contribution(self, time=None) -> PowerType:
        #this method gives back the participants power
        #contribution to the local grid. Thats why consumers give a negative value
        #and energy producers (pv, later maybe cs) give a posiive value
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__} "
    
class UncontrolledElectricalGridConsumer(ElectricalGridConsumer):
    def __init__(self, name: str):
        super().__init__(name)

    def get_power_contribution(self, time=None) -> PowerType:
        raise NotImplementedError

class ControlledEletricalGridConsumer(ElectricalGridConsumer):
    def __init__(self, name: str,
                        maximum_charging_power: PowerType,
                         minimum_charging_power: PowerType,
                         efficiency_map: InterfaceEfficiencyMap = ConstantEfficiencyMap(efficiency=0.9)):
        super().__init__(name)
        
        self.actual_grid_power = PowerType(0, PowerTypeUnit.KW)
        self.actual_consumer_power: PowerType = PowerType(0, PowerTypeUnit.KW)
        self.efficiency_map: InterfaceEfficiencyMap = efficiency_map
        self.maximum_grid_power: PowerType = maximum_charging_power
        self.minimum_grid_power: PowerType = minimum_charging_power
        self.target_grid_power:PowerType = None #PowerType(0, PowerTypeUnit.KW)


    def set_target_grid_charging_power(self, target_grid_side_power: Union[PowerType, None] = None):
        if target_grid_side_power is None:
            self.target_grid_power = self.maximum_grid_power
        else:
            self.target_grid_power= self.limit_grid_power(target_grid_side_power)


    def get_target_grid_charging_power(self):
        return self.target_grid_power
    
    def get_target_consumer_charging_power(self):
        if self.target_grid_power is None: 
            return None 
        return self.efficiency_map.get_output_power(self.target_grid_power)

    def set_actual_consumer_charging_power(self, actual_consumer_power: PowerType):
        actual_grid_side_power = self.efficiency_map.get_input_power(actual_consumer_power)
        self.actual_grid_power= self.limit_grid_power(actual_grid_side_power)
        self.actual_consumer_power = self.efficiency_map.get_output_power(self.actual_grid_power)
        logger.info(f"CS charging power on grid side: {self.actual_grid_power.get_in_kw().value} kW, on consumer side: {self.actual_consumer_power.get_in_kw().value} kW")

    def get_actual_consumer_charging_power(self):
        return self.actual_consumer_power   

    
    def get_maximum_grid_power(self):
        return self.maximum_grid_power
    
    def get_maximum_consumer_power(self):
        return self.efficiency_map.get_output_power(self.maximum_grid_power)
    
    def get_minimum_grid_power(self):
        return self.minimum_grid_power
    
    def get_minimum_consumer_power(self):
        if self.minimum_grid_power < PowerType(0, PowerTypeUnit.KW):
            return self.efficiency_map.get_input_power(self.minimum_grid_power)
        return self.efficiency_map.get_output_power(self.minimum_grid_power)
    
    def limit_grid_power(self, power: PowerType):
        if power > self.maximum_grid_power:
            return self.maximum_grid_power
        elif power < self.minimum_grid_power:
            return self.minimum_grid_power
        else:
            return power
            

    #the following method is implemented from Electricalgridconsumer,
    #the time is at first not considered, it will be depending on the
    #requirments we will have later
    def get_power_contribution(self, time = None) -> PowerType:
        grid_power = self.efficiency_map.get_input_power(self.actual_consumer_power)
        return grid_power*(-1)
