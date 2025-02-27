from typing import List 
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from config.logger_config import get_module_logger

from abc import ABC, abstractmethod

logger = get_module_logger(__name__)




class InterfacePredictionAlgorithm:
    predicted_ev_collection: InterfacePredictedEvCollection

    @abstractmethod
    def import_prediction_data(self, input_prediction_data: List[EvPredictionData]) -> None:
        pass

    @abstractmethod
    def predict_stay_duration_for_new_arrival(self):
        pass

    @abstractmethod
    def update_prediction(self):
        pass
    
  


class SimplePredictionAlgorithm(InterfacePredictionAlgorithm):

    def __init__(self,
                 predicted_ev_collection: InterfacePredictedEvCollection,
                 input_prediction_data: List[EvPredictionData] = []) -> None:
        self.predicted_ev_collection: InterfacePredictedEvCollection = predicted_ev_collection
        self.input_data: List[EvPredictionData] = input_prediction_data


    def import_prediction_data(self, input_prediction_data: List[EvPredictionData]) -> None:
        if input_prediction_data is not None:
            self.input_data = input_prediction_data
        self.predicted_ev_collection.set_prediction_data(self.input_data) # Set the prediction data to the predicted_ev_collection

    def predict_stay_duration_for_new_arrival(self):
        if self.predicted_ev_collection.new_arrivals is not None:
            for ev in self.predicted_ev_collection.new_arrivals:
                if ev.stay_duration is None:
                    logger.warning(f"Stay duration not assigned to new arrival {ev}")
                    ev.set_stay_duration(2000)#150000)

    def update_prediction(self):
        for ev in self.predicted_ev_collection.new_arrivals:
            #self.check_stay_duration_assigned(ev)
            replacement_ev = self.predicted_ev_collection.find_closest_prediction(ev)            
            if replacement_ev is not None:
                ev.stay_duration = replacement_ev.stay_duration
                self.predicted_ev_collection.purely_predicted_arrivals.remove(replacement_ev)
        self.predict_stay_duration_for_new_arrival()
        self.predicted_ev_collection.append_new_arrivals()
        logger.debug(f"predicted evs: {self.predicted_ev_collection.purely_predicted_arrivals}") 
        logger.debug(f"new arrivals: {self.predicted_ev_collection.new_arrivals}")

    def check_stay_duration_assigned(self,ev: EvPredictionData):
        if ev.stay_duration is None:
            raise ValueError(f"Stay duration not assigned to new arrival {ev}")

