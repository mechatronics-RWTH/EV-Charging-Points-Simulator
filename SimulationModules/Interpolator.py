
import numbers
import numpy as np
from typing import Iterable, List, Union
from numbers import Number

from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit


class EfficiencyInterpolator:
    #this class calculates an efficiency (number 0 to 1)
    #from a Powertype. That for, a list of Powers for x has 
    #to be given to init an a list of floats for y
    def __init__(self, x_values: Iterable[Union[PowerType, numbers.Number]], y_values: Iterable[Union[PowerType, numbers.Number]]):
        
        self.x_type=type(x_values[0])
        self.y_type=type(y_values[0])

        self.x_values = self.get_scalar_axis(x_values)
        self.y_values = self.get_scalar_axis(y_values)


    def interpolate(self, x):
        
        x_value=x.get_in_w().value        
        if x_value > self.x_values[-1] or x_value < self.x_values[0]:
            raise ValueError("x is out of bounds.")
        
        y_value=np.interp(x_value, self.x_values, self.y_values)

        return self.get_full_quantity(y_value)


    def get_scalar_axis(self, values):
        #the class takes different types for the interpolation axes
        #and turns them into np arrays of scalars, so that we can use 
        #the numpy interpolaion later

        return np.array([self.get_scalar_x_value(element) for element in values])
      

    def get_scalar_x_value(self, x):

        scalar=0

        if issubclass(type(x), PowerType):
            scalar=x.get_in_w().value
        elif issubclass(type(x), Number):
            scalar=x
        else: 
            raise ValueError("x-Type: "+str(self.x_type)+" is not compatible with EfficiencyInterpolator")
        return scalar


    def get_full_quantity(self, value):
        """
        this method takes a scalar from the interpolation
        and completes it with a unit to the full quantity
        """
        quantity=None
        if issubclass(self.y_type, PowerType):
            quantity=PowerType(power_in_w=value, unit=PowerTypeUnit.W)
        elif issubclass(self.y_type, Number):
            quantity=value
        else:
            raise ValueError("yType: "+str(self.y_type)+" is not compatible with EfficiencyInterpolator")

        return quantity

    
class Interpolator:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values

    def find_indices(self, x):
        for i in range(len(self.x_values) - 1):
            if self.x_values[i] <= x <= self.x_values[i + 1]:
                return i, i + 1
        raise ValueError("x is out of bounds.")

    def interpolate(self, x):
        idx1, idx2 = self.find_indices(x)
        x1, x2 = self.x_values[idx1], self.x_values[idx2]
        y1, y2 = self.y_values[idx1], self.y_values[idx2]
        if x1 != x2:
            y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
            return y
        else:
            return y1

