from Controller_Agent.Model_Predictive_Controller.Model_Predictive_Controller import Model_Predictive_Controller, Solver
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import ParkingSpotWithFuture, AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor, SimplePredictor
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import SimplePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceModelEnvTranslator import InterfaceModelEnvTranslator
import numpy as np
from test.conftest_observation import raw_obs, action_raw_base
from SimulationEnvironment.RawEnvSpaces import RawEnvSpaceManager
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

NUM_PARING_FIELDS = 20
NUM_GINIS = 1


class MockRawEnvSpaceManager(RawEnvSpaceManager):
    def __init__(self):
        self.area_size = NUM_PARING_FIELDS
        self.max_grid_power = 100
        self.amount_ginis = NUM_GINIS
        self.max_building_power = 100
        self.max_price = 0.5
        self.max_pv_power = 100
        self.max_parking_time = timedelta(seconds=900)
        self.max_energy_request = 100
        self.max_charging_power = 100
        self.max_gini_energy = 100
        self.max_ev_energy = 100
        self.sim_duration = timedelta(days=1)

    
    def create_observation_space(self):
        return super().create_observation_space()
    
    def create_action_space(self):
        return super().create_action_space()
    
    def create_action_base(self):
        return super().create_action_base()




@pytest.fixture
def mock_availability_horizon_matrix():
    return AvailabilityHorizonMatrix(num_parking_spots=NUM_PARING_FIELDS)

@pytest.fixture
def mock_predicted_ev_collection():
    return PredictedEvCollection()

@pytest.fixture
def mock_prediction_state_updater(mock_predicted_ev_collection):
    return PredictionStateUpdater(predicted_ev_collection=mock_predicted_ev_collection)

@pytest.fixture
def mock_prediction_algorithm(mock_predicted_ev_collection):
    return SimplePredictionAlgorithm(predicted_ev_collection=mock_predicted_ev_collection)

@pytest.fixture
def predictor(mock_availability_horizon_matrix, 
              mock_predicted_ev_collection,
              mock_prediction_state_updater,
              mock_prediction_algorithm):
    return SimplePredictor(availability_horizon_matrix=mock_availability_horizon_matrix,
                           predicted_ev_collection=mock_predicted_ev_collection,
                           prediction_state_updater=mock_prediction_state_updater,
                           prediction_algorithm=mock_prediction_algorithm
                           )




@pytest.fixture
def mock_raw_obs():
    my_raw_obs = raw_obs(area_size=NUM_PARING_FIELDS, amount_ginis=NUM_GINIS)
    user_requests = my_raw_obs["user_requests"]
    user_requests = np.array(user_requests)  # Convert to NumPy array
    user_requests[user_requests > 1] = 1
    my_raw_obs["user_requests"] = user_requests.tolist()
    return my_raw_obs

@pytest.fixture
def mpc_config(predictor,mock_availability_horizon_matrix):
    return {
        "N_pred": 3,
        "number_parking_fields": NUM_PARING_FIELDS,
        "availability_horizon_matrix": mock_availability_horizon_matrix,
        "model": None,
        "solver": "glpk",
        "predictor": predictor
    }

@pytest.fixture
def action():
    action = action_raw_base(area_size=NUM_PARING_FIELDS, amount_ginis=NUM_GINIS)
    return action



@pytest.fixture
def mpc():
    return Model_Predictive_Controller(solver=Mock(Solver),
                                       predictor=Mock(InterfacePredictor),
                                       model=Mock(InterfaceOptimizationModel),
                                       env_translator=Mock(InterfaceModelEnvTranslator)
                                       )


def test_mpc_one_step(mock_raw_obs, mpc, action):
    mpc = mpc
    print(mock_raw_obs["user_requests"])
    mpc.calculate_action(raw_obs=mock_raw_obs, action=action)
    assert "requested_gini_field" in mpc.action
    assert "requested_gini_power" in mpc.action
    assert "target_charging_power" in mpc.action
    assert "request_answer" in mpc.action
    assert "target_stat_battery_charging_power" in mpc.action
    assert mpc.action["requested_gini_field"] is not None
    assert mpc.action["requested_gini_power"] is not None
    assert mpc.action["target_charging_power"][0] is None
    assert mpc.action["request_answer"] is not None
    assert mpc.action["target_stat_battery_charging_power"][0] == 0



