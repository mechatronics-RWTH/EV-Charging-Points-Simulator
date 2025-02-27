from abc import ABC, abstractmethod

class InterfaceRewardMetrik(ABC):
    metrik_name: str
    total_cost: float
    step_cost: float

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def calculate_total_cost(self):
        pass

    @abstractmethod
    def get_step_cost(self):
        pass

    @abstractmethod
    def get_total_cost(self):
        pass

    @abstractmethod
    def calculate_step_cost(self):
        pass



