from abc import ABC, abstractmethod
from typing import List
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData

class InterfaceParkingSpotWithFuture(ABC):
    assigned_EV: List[EvPredictionData]

    @abstractmethod
    def is_occupied_in_future(self, seconds_in_future: float) -> bool:
        pass

    @abstractmethod
    def is_available_for_Ev(self, ev: EvPredictionData) -> bool:
        pass

    @abstractmethod
    def assign_ev(self, ev: EvPredictionData) -> None:
        pass

    