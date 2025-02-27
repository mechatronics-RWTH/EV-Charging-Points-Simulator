from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pathlib
import numpy as np
from config.definitions import ROOT_DIR
from SimulationModules.TrafficSimulator.DataImport import read_standard_load_data

class InterfaceParkingAreaPenetrationData(ABC):
    time_axis_start: np.ndarray
    probability_arrival_per_time_unit_data: np.ndarray
    probability_arrival_per_time_unit_data_scaled: np.ndarray
    amount_of_new_evs: int
    customers_per_hour: float
    time: datetime
    week_start: datetime
    week_time: timedelta
    step_time: timedelta
    amount_of_new_evs: int 

    @abstractmethod
    def update_time(time: datetime):
        raise NotImplementedError

    @abstractmethod
    def calculate_amount_new_evs():
        raise NotImplementedError
    
    @abstractmethod
    def get_amount_new_evs():
        raise NotImplementedError
    
    @abstractmethod
    def scale_distribution():
        raise NotImplementedError
    
    @abstractmethod
    def load_data():
        raise NotImplementedError
    
    



