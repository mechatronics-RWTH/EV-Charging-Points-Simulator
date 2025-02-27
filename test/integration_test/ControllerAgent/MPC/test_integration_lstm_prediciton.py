from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import InterfacePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.Prediction.LstmPredictionAlgorithm import LstmPredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData

#test
def test_lstm_prediction():
    ev1 = EvPredictionData(arrival_time=-4500, stay_duration=3600, requested_energy=20)
    ev2 = EvPredictionData(arrival_time=-3300, stay_duration=7200, requested_energy=10)
    ev3 = EvPredictionData(arrival_time=-2700, stay_duration=3000, requested_energy=10)
    ev4 = EvPredictionData(arrival_time=2700, stay_duration=5400, requested_energy=30)

    predicted_ev_collection = PredictedEvCollection()
    predicted_ev_collection.evs_left_already = [ev1]
    predicted_ev_collection.present_ev_prediction_list = [ev2, ev3]
    predicted_ev_collection.purely_predicted_arrivals = [ev4]
    prediction_state_updater = PredictionStateUpdater(predicted_ev_collection=predicted_ev_collection)
    from SimulationEnvironment.EnvConfig import EnvConfig
    sim_start_dt = EnvConfig.load_env_config()["settings"].start_datetime
    pred_alg = LstmPredictionAlgorithm(predicted_ev_collection=predicted_ev_collection, prediction_state_updater=prediction_state_updater, sim_start_datetime=sim_start_dt)

    pred_alg.update_prediction()
    assert True