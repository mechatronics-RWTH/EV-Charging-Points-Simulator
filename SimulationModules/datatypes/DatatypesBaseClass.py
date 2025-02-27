from typing import Union
import numpy as np
import numbers
import copy

class DatatypesBaseClass:
    """
    This class defines the base for all datatypes. It defines how operations regarding logical
    and arithmetical operations are supposed to be performed with the data types. 
    Especially the transformation of the unit (which is implemented in the child classes) is important
    to make sure that no values with different units are mixed. 
    """

    def compare_to_zero_helper(self, other_object: Union['DatatypesBaseClass', numbers.Number]):
        if isinstance(other_object, numbers.Number):
            if other_object == 0:
                class_self = self.__class__
                other_object = class_self(0, self.unit)

        return other_object

    def _same_unit(self, other_object: 'DatatypesBaseClass'):

        if other_object.unit in self.units:
            while other_object.unit is not self.unit:
                    other_object._transform_unit()
        else:
            names = [member.name for member in self.units]
            exep_txt=f"Unit of {other_object} not in " \
                     f"units of {self} which are {names}"
            raise TypeError(exep_txt)

    def __abs__(self):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.value = abs(copy_of_self.value)
        return copy_of_self

    def __neg__(self):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.value = -copy_of_self.value
        return copy_of_self


    def __float__(self):
        return float(self.value)

    def __add__(self, other: Union['DatatypesBaseClass', np.array]):
        if isinstance(other, np.ndarray):
            res = np.empty_like(other)
            for index,element in enumerate(other):
                res[index]=self.__add__(element)
            return res

        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        res=copy.deepcopy(self)
        res.value = self.value + other.value
        return res

    def __sub__(self, other: 'DatatypesBaseClass'):
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        res=copy.deepcopy(self)
        res.value = self.value - other.value
        return res

    def __rsub__(self, other: 'DatatypesBaseClass'):

        return self.__sub__(other)

    def __radd__(self, other:  Union['DatatypesBaseClass', np.array]):

        return self.__add__(other)

    def __gt__(self, other: 'DatatypesBaseClass'):
        """        
        __gt__ is the function overloader for > (greater than)
        """
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        if self.value > other.value:
            return True
        else:
            return False

    
    def __lt__(self, other: 'DatatypesBaseClass'):
        """        
        __lt__ is the function overloader for < (lower than)
        """
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        if self.value < other.value:
            return True
        else:
            return False

    def __eq__(self, other: 'DatatypesBaseClass'):
        """
        __eq__ is the function overloader for == (equal to)

        """
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        if self.value == other.value:
            return True
        else:
            return False

    def __ge__(self, other: 'DatatypesBaseClass'):
        """
        __ge__ is the function overloader for >= (greater equal to)

        """
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        if self.value >= other.value:
            return True
        else:
            return False

    def __le__(self, other: 'DatatypesBaseClass'):
        """
        __le__ is the function overloader for <= (lower equal to)

        """
        other= self.compare_to_zero_helper(other)
        self._same_unit(other)
        comparison = self.value <= other.value
        try:
            iterator = iter(comparison)
        except TypeError:
            return comparison # not iterable
        else:
            return all(comparison)

    def __ne__(self, other: 'DatatypesBaseClass'):
        """
        __ne__ is the function overloader for != (not equal to)

        """
        other = self.compare_to_zero_helper(other)
        self._same_unit(other)
        if self.value != other.value:
            return True
        else:
            return False

    def __mul__(self,other: 'DatatypesBaseClass'):
        """
        __mul__ is the function overloader for * (multiplication)
        """
        res=copy.deepcopy(self)
        res.value = self.value * other
        return res

    def __rmul__(self,other: 'DatatypesBaseClass'):
        """
        __mul__ is the function overloader for * (multiplication)
        """
        return self.__mul__(other)

    def __truediv__(self, other: 'DatatypesBaseClass'):
        if type(self) == type(other):
            a=copy.deepcopy(self)
            b=copy.deepcopy(other)
            a._same_unit(b)
            value = a.value / b.value
            return value
        else:
            res=copy.deepcopy(self)
            res.value = self.value / other
            return res




    #def __cmp__(self, other): #cmp does not exist in python 3
     #   return cmp(self.value, other.value)


    def __repr__(self):
        return f'{self.__class__.__name__}: {self.value} {self.unit}'

    def __iter__(self):
        return DataBaseClassIter(self)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, i: int):
        return type(self)(self.value[i],self.unit)


class DataBaseClassIter:
    def __init__(self, DataBaseClass: type):
        self._databaseclass=DataBaseClass
        self._base_class_size = len(self._databaseclass)
        self._current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < self._base_class_size:
            member = self._databaseclass[self._current_index]
            self._current_index += 1
            return member
        raise StopIteration
