from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import InterfacePredictionAlgorithm, SimplePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
import pytest   
from test.ControllerAgent.MPC.conftest_mpc import MockPredictedEvCollection
from SimulationModules.datatypes.EnergyType import EnergyType

@pytest.fixture
def input_data():
    input_data = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),]
    return input_data

@pytest.fixture
def prediction_algorithm(input_data):
    object = SimplePredictionAlgorithm(predicted_ev_collection= MockPredictedEvCollection(),
                                       input_prediction_data=input_data)
    return object



class TestPredictionAlgorithm:

    def test_import_prediction_data(self,
                                    prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.import_prediction_data(input_prediction_data=[])
        assert True       
        

    def test_predict_stay_duration_for_new_arrival(self,
                                                   prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.predicted_ev_collection.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=None),
                                                                     EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=None),
                                                                     EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=None)]
        prediction_algorithm.predict_stay_duration_for_new_arrival()
        for ev in prediction_algorithm.predicted_ev_collection.new_arrivals:
            assert ev.stay_duration is not None

    def test_update_prediction_present_ev_increased(self,
                               prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.predicted_ev_collection.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=3, parking_spot_id=4),]

        
        prediction_algorithm.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=9, stay_duration=2)]
        
        prediction_algorithm.update_prediction()
        assert len(prediction_algorithm.predicted_ev_collection.present_ev_prediction_list) == 1
        
        
    
    def test_update_prediction_predicted_ev_decreased(self,
                               prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.predicted_ev_collection.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=3, parking_spot_id=4),]

        
        prediction_algorithm.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=9, stay_duration=2)]
        
        prediction_algorithm.update_prediction()
        assert len(prediction_algorithm.predicted_ev_collection.purely_predicted_arrivals) == 2
        
    
    def test_update_prediction_present_ev_spot_id(self,
                               prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.predicted_ev_collection.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=3, parking_spot_id=4),]

        
        prediction_algorithm.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=9, stay_duration=2)]
        
        prediction_algorithm.update_prediction()
        assert prediction_algorithm.predicted_ev_collection.present_ev_prediction_list[-1].parking_spot_id == 4

    def test_update_prediction_no_stay_duration_set(self,
                               prediction_algorithm: InterfacePredictionAlgorithm):
        prediction_algorithm.predicted_ev_collection.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=None, parking_spot_id=4),]

        
        prediction_algorithm.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                                  EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=9, stay_duration=2)]
        with pytest.raises(ValueError):
            prediction_algorithm.update_prediction()
        