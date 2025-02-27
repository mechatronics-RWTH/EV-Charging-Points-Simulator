from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import random
from SimulationModules.Enums import Request_state
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import InterfacePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import InterfacePredictionStateUpdater, PredictionStateUpdater
from config.logger_config import get_module_logger
from SimulationModules.datatypes.EnergyType import EnergyType

logger = get_module_logger(__name__)


t_arrival = {0: 3, 1: 5, 2: 7, 3: 10, 4: 12}  # EV arrival times
t_departure = {0: 9, 1: 15, 2: 20, 3: 14, 4: 23}  # EV departure times




class InterfacePredictor(ABC):
    current_time: float
    predicted_ev_collection: InterfacePredictedEvCollection
    prediction_algorithm: InterfacePredictionAlgorithm
    prediction_state_updater: InterfacePredictionStateUpdater
    availability_horizon_matrix: AvailabilityHorizonMatrix


    @abstractmethod
    def predict_ev_behavior(self, current_time) -> List[EvPredictionData]:
        pass

    @abstractmethod
    def update_prediction_state(self, energy_requests: List[float], user_requests: List[int]):
        pass

    @abstractmethod
    def update_availability_horizon_matrix(self):
        pass

    @abstractmethod
    def initialize_prediction(self, prediction_data: List[EvPredictionData]):
        pass
    


class SimplePredictor(InterfacePredictor):

    def __init__(self,
                 availability_horizon_matrix: AvailabilityHorizonMatrix,
                 predicted_ev_collection: InterfacePredictedEvCollection,
                 prediction_algorithm: InterfacePredictionAlgorithm,
                 prediction_state_updater: InterfacePredictionStateUpdater) -> None:
        
        self.predicted_ev_collection: InterfacePredictedEvCollection = predicted_ev_collection
        self.prediction_algorithm: InterfacePredictionAlgorithm = prediction_algorithm
        self.prediction_state_updater: InterfacePredictionStateUpdater = prediction_state_updater
        self.current_time = 0
        self.availability_horizon_matrix: AvailabilityHorizonMatrix = availability_horizon_matrix
        self.initialized = False

    def initialize_prediction(self, prediction_data: List[EvPredictionData]):
        self.prediction_algorithm.import_prediction_data(prediction_data)
        self.initialized = True

    def predict_ev_behavior(self, current_time:float) -> None:
        self.current_time = current_time
        self.prediction_algorithm.update_prediction()
        #self.prediction_algorithm.predict_stay_duration_for_new_arrival()
       


    def update_prediction_state(self,energy_requests: List[float], user_requests: List[int]):
        # if not isinstance(energy_requests,EnergyType):
        #     energy_requests = [EnergyType(energy_request) for energy_request in energy_requests]
        self.prediction_state_updater.update_prediction_based_on_observation(current_time=self.current_time,
                                                                             energy_requests=energy_requests,
                                                                             user_requests=user_requests)
        #self.prediction_algorithm.update_prediction()
    
    def update_availability_horizon_matrix(self):
        predicted_ev_collection = self.predicted_ev_collection.get_combined_prediction_data_relative(self.current_time)
        logger.debug(f"Predicted EV collection: {predicted_ev_collection} at time {self.current_time}")
        self.availability_horizon_matrix.assign_evs_to_availability_matrix(predicted_ev_collection)







    




