from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData  
from typing import List
from abc import ABC, abstractmethod
from config.logger_config import get_module_logger
import copy
from SimulationModules.datatypes.EnergyType import EnergyType   

logger = get_module_logger(__name__)


class EmptyPredictictionError(Exception):
    pass

class InterfacePredictedEvCollection:
    evs_left_already: List[EvPredictionData]
    present_ev_prediction_list: List[EvPredictionData]
    purely_predicted_arrivals: List[EvPredictionData]
    new_arrivals: List[EvPredictionData]

    @abstractmethod
    def set_prediction_data(self, input_prediction_data: List[EvPredictionData]) -> None:
        pass

    @abstractmethod
    def append_new_arrivals(self):
        pass

    @abstractmethod
    def find_closest_prediction(self, new_ev: EvPredictionData) -> EvPredictionData:
        pass

    @abstractmethod
    def get_combined_prediction_data_relative(self, current_time: float) -> List[EvPredictionData]:
        pass

    @abstractmethod
    def remove_ev(self, 
                  parking_spot_index: int,
                  current_time: float) -> None:
        pass

    @abstractmethod
    def update_requested_energy(self, parking_spot_index: int, requested_energy: float) -> None:
        pass

    @abstractmethod
    def add_new_arrival(self, new_ev: EvPredictionData):
        pass

    @abstractmethod
    def check_if_ev_with_spot_id_present(self, parking_spot_id: int) -> bool:
        pass

    @abstractmethod
    def shift_arrival_time(self,
                            current_time: float,
                            time_shift: float) -> None:
          pass



class PredictedEvCollection(InterfacePredictedEvCollection):
        
    def __init__(self):
        self.assigned_id = 0
        self.evs_left_already: List[EvPredictionData] = []
        self.present_ev_prediction_list: List[EvPredictionData] = []
        self.new_arrivals: List[EvPredictionData] = []
        self.purely_predicted_arrivals: List[EvPredictionData] = []

    def set_prediction_data(self, input_prediction_data: List[EvPredictionData]) -> None:
        self.purely_predicted_arrivals: List[EvPredictionData] = input_prediction_data
        for ev in self.purely_predicted_arrivals:
            if ev.id is None:
                ev.set_id(self.assigned_id)
                self.assigned_id += 1

    def append_new_arrivals(self):
        for arrived_ev in self.new_arrivals:
            if self.check_if_ev_with_spot_id_present(arrived_ev.parking_spot_id):
                raise ValueError(f"EV with parking spot id {arrived_ev.parking_spot_id} is already present in the prediction list: \n {self.present_ev_prediction_list}")
            self.present_ev_prediction_list.append(arrived_ev)
        self.new_arrivals.clear()

    def find_closest_prediction(self, new_ev: EvPredictionData) -> EvPredictionData:
        if len(self.purely_predicted_arrivals) == 0:
            logger.debug("No predictions available")
            return None
        try:
            closest_prediction = min(self.purely_predicted_arrivals, key=lambda ev: abs(ev.arrival_time - new_ev.arrival_time))
        except ValueError as e:
            raise ValueError(f"Following error occured: {e} \n new_ev: {new_ev} and purely_predicted_arrivals: {self.purely_predicted_arrivals}")
        return closest_prediction
    
    def shift_arrival_time(self, 
                           current_time: float,
                           time_shift: float) -> None:
        for ev in self.purely_predicted_arrivals:
            if ev.arrival_time <= current_time:
                ev.arrival_time = current_time + time_shift


    def get_combined_prediction_data_relative(self, current_time) -> List[EvPredictionData]:
        return self.get_relative_arrival_prediction_data(current_time) + self.get_relative_purely_prediction_data(current_time=current_time)
    
    def get_relative_purely_prediction_data(self, current_time) -> List[EvPredictionData]:
        relative_purely_prediction_data = copy.deepcopy(self.purely_predicted_arrivals) # important to use deepcopy here
        for ev in relative_purely_prediction_data:
            ev.arrival_time -= current_time
        return relative_purely_prediction_data

    def get_relative_arrival_prediction_data(self, current_time) -> List[EvPredictionData]:
        relative_arrival_prediction_data = copy.deepcopy(self.present_ev_prediction_list) # important to use deepcopy here
        for ev in relative_arrival_prediction_data:
            ev.arrival_time -= current_time
        return relative_arrival_prediction_data
    
    def add_new_arrival(self, new_ev: EvPredictionData):
        if self.check_if_ev_with_spot_id_present(new_ev.parking_spot_id):
            raise ValueError(f"EV with parking spot id {new_ev.parking_spot_id} is already present in the prediction list: \n {self.present_ev_prediction_list}")
        new_ev.has_arrived = True
        self.new_arrivals.append(new_ev)

    def remove_ev(self, 
                  parking_spot_index: int,
                  current_time: float) -> None:
        for ev in self.present_ev_prediction_list:
            if ev.parking_spot_id == parking_spot_index:
                ev.stay_duration = current_time- ev.arrival_time
                self.present_ev_prediction_list.remove(ev)
                self.evs_left_already.append(ev)
                return
        raise ValueError("There is no EV with the given parking spot index")
    
    def update_requested_energy(self, parking_spot_index: int, requested_energy: float) -> None:
        for ev in self.present_ev_prediction_list:
            if ev.parking_spot_id == parking_spot_index:
                ev.requested_energy = EnergyType(requested_energy)
                return

        for ev in self.new_arrivals:
            if ev.parking_spot_id == parking_spot_index:
                ev.requested_energy = EnergyType(requested_energy)
                return
        
        if requested_energy != 0:
             raise ValueError("There is no EV with the given parking spot index")
        

       
    
    def check_if_ev_with_spot_id_present(self, parking_spot_id: int) -> bool:
        if parking_spot_id is None:
            raise ValueError("Parking spot id is None")
        for ev in self.present_ev_prediction_list:
            if ev.parking_spot_id == parking_spot_id:
                return True
        return False

