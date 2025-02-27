from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Prediction.InterfaceParkingSpotWithFuture import InterfaceParkingSpotWithFuture
from typing import List
import numpy as np
from config.logger_config import get_module_logger
from datetime import datetime, timedelta

logger = get_module_logger(__name__)

class DepartureInPastError(Exception):
    pass

class ArrivalInPastError(Exception):
    pass

class TimeNotInFutureError(Exception):
    pass

class TimeOutOfHorizonError(Exception):
    pass

class ParkingSpotWithFuture(InterfaceParkingSpotWithFuture):

    def __init__(self, 
                 parking_spot_id: int, 
                 horizon: int,
                 timestep_size: timedelta = timedelta(minutes=5),
                 ):
        self.timestep_size = timestep_size
        self.parking_spot_id = parking_spot_id
        self.horizon = horizon
        self.assigned_EV: List[EvPredictionData] = []
        self.future_time = np.arange(0, horizon*self.timestep_size.total_seconds(), self.timestep_size.total_seconds())
        self.occupacy_with_id = np.zeros(horizon)

    def is_occupied_in_future(self, seconds_in_future: int):
        try:
            index = self.get_index_by_time(seconds_in_future)
        except TimeNotInFutureError as e:
            return False
        except TimeOutOfHorizonError as e:
            return False
        return self.occupacy_with_id[index] != 0

    def is_available_for_Ev(self, ev: EvPredictionData):
        arrival_index = self.get_arrival_index_from_time(ev.arrival_time)
        departure_index = self.get_departure_index_from_time(ev.arrival_time + ev.stay_duration)
        if (self.occupacy_with_id[arrival_index: departure_index]== ev.id).all():
            logger.warning(f"spot with {self.parking_spot_id} is already assigned to EV with id {ev.id}")
            return True
        if self.occupacy_with_id[arrival_index: departure_index].any():
            logger.debug(f"spot with {self.parking_spot_id} is not available for EV with id {ev.id}")
            return False
        return True
    
    def assign_ev(self, ev: EvPredictionData):
        self.assigned_EV.append(ev)
        self.assign_occupancy(ev)

    def assign_occupancy(self, ev: EvPredictionData):
        arrival_index = self.get_arrival_index_from_time(ev.arrival_time)
        departure_index = self.get_departure_index_from_time(ev.arrival_time + ev.stay_duration)
        # Fill the slice with ev.id
        for i in range(arrival_index, departure_index):
            self.occupacy_with_id[i] = ev.id

    def get_arrival_index_from_time(self, time: int):
        try:
            arrival_index= self.get_index_by_time(time)
        except TimeNotInFutureError as e:
            arrival_index = 0
        except TimeOutOfHorizonError as e:
            logger.warning(f"Arrival time {time} of EV is out of horizon {self.future_time}")
        return arrival_index
    
    def get_departure_index_from_time(self, time: int):
        try:
            departure_index = self.get_index_by_time(time)
        except TimeNotInFutureError as e:
            raise DepartureInPastError(f"Departure time {time} is in the past")
        except TimeOutOfHorizonError as e:
            departure_index = len(self.future_time)
        return departure_index



    def unassign_ev(self, ev: EvPredictionData):
        self.occupacy_with_id[self.occupacy_with_id == ev.id] = 0
        self.assigned_EV.remove(ev)


    def get_start_energy_by_ev_id(self, ev_id: int):
        try:
            return [ev.requested_energy for ev in self.assigned_EV if ev.id == ev_id][0]
        except IndexError as e:
            logger.debug(f"EV with id {ev_id} is not assigned to parking spot with id {self.parking_spot_id}")
            raise IndexError(f"EV with id {ev_id} is not assigned to parking spot with id {self.parking_spot_id}")
        
    def get_index_by_time(self, time: int):
        logger.debug(f"Time: {time} and future time: {self.future_time}")
        if time < self.future_time[0]:
            logger.debug(f"Time {time} is not in the future")
            raise TimeNotInFutureError(f"Time {time} is not in the future")
        try:
            index = next(i for i, t in enumerate(self.future_time) if time <= t)
        except StopIteration:
            logger.debug(f"No valid index found for time {time}")
            raise TimeOutOfHorizonError(f"Horizon is {self.future_time} and time is {time}")
        
        return index
    
    def __str__(self) -> str:
        return f"Parking spot {self.parking_spot_id} with horizon {self.horizon} and occupancy {self.occupacy_with_id}"
        
