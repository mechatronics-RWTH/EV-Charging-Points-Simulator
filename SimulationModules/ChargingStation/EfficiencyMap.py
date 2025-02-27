from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.Interpolator import EfficiencyInterpolator, Interpolator

import numpy as np
from typing import List
from abc import ABC, abstractmethod



class InterfaceEfficiencyMap(ABC):

    @abstractmethod
    def get_efficiency(self, input_power: PowerType) -> float:
        pass

    @abstractmethod
    def get_output_power(self, input_power: PowerType) -> PowerType:
        pass

    @abstractmethod
    def get_input_power(self, output_power: PowerType) -> PowerType:
        pass

class EfficiencyMap(InterfaceEfficiencyMap):
    def __init__(self, 
                 min_input_power: PowerType, 
                 max_input_power: PowerType,
                 relative_power_steps: np.ndarray = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])/100,
                 efficiency_values: np.ndarray= np.array([85, 88, 94, 95, 96, 97, 97.5, 97.7, 98, 98, 98])/100):
        

        self.check_input(relative_power_steps)
        self.check_input(efficiency_values)
        delta_power = max_input_power - min_input_power
        absolute_power_steps = relative_power_steps * delta_power
        input_power_ax = min_input_power + absolute_power_steps
        output_power_ax = input_power_ax * efficiency_values
        self.efficiency_interpolator= EfficiencyInterpolator(x_values=input_power_ax, y_values=efficiency_values)
        self.output_power_interpolator = EfficiencyInterpolator(x_values=input_power_ax, y_values=output_power_ax)
        self.input_power_interpolator = EfficiencyInterpolator(x_values=output_power_ax, y_values=input_power_ax)


    def check_input(self, axes: np.ndarray):
        if not isinstance(axes, np.ndarray):
            raise ValueError("Input axes must be a numpy array")

        if not np.all((0 <= axes) & (axes <= 1)):
            raise ValueError("Input axes must be between 0 and 1")
        return 

    def get_efficiency(self, input_power: PowerType):
        """
        Get the efficiency of the charging station for a given input power
        """
        try:
            value = self.efficiency_interpolator.interpolate(input_power)
        except ValueError:
            negative_value = input_power*(-1)
            value = self.efficiency_interpolator.interpolate(negative_value)
        return value
    
    def get_output_power(self, input_power: PowerType):
        """
        Get the output power of the charging station for a given input power
        """
        try:
            value = self.output_power_interpolator.interpolate(input_power)
        except ValueError:
            negative_value = input_power*(-1)
            value = self.output_power_interpolator.interpolate(negative_value)*(-1)
        return value
    
    def get_input_power(self, output_power: PowerType):
        """
        Get the output power of the charging station for a given input power
        """
        try:
            value = self.input_power_interpolator.interpolate(output_power)
        except ValueError:
            negative_value = output_power*(-1)
            value = self.input_power_interpolator.interpolate(negative_value)*(-1)
        return value
    

class ConstantEfficiencyMap(InterfaceEfficiencyMap):
    def __init__(self,
                 efficiency: float = 0.94,):
        self.efficiency = efficiency

    def get_efficiency(self, input_power: PowerType) -> float:
        return self.efficiency

    def get_output_power(self, input_power: PowerType) -> PowerType:
        return input_power * self.efficiency

    def get_input_power(self, output_power: PowerType) -> PowerType:
        return output_power / self.efficiency