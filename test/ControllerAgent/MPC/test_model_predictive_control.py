from typing import List
from Controller_Agent.Model_Predictive_Controller.Model_Predictive_Controller import Model_Predictive_Controller, calculate_energy_request
from test.conftest_observation import raw_obs
from test.ControllerAgent.MPC.conftest_mpc import FakeOptimizationModel
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor, SimplePredictor
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import InterfacePredictionAlgorithm, SimplePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Model_Predictive_Controller import Solver
from unittest.mock import MagicMock
from datetime import timedelta

fake_predictor = MagicMock(spec=InterfacePredictor)


import pytest
import numpy as np

NUM_PARING_FIELDS = 5

class MockSolver(Solver):
    def __init__(self):
        self.status = None
        self.termination_condition = None

    def solve(self, model, tee = False):
        self.status = 'ok'
        self.termination_condition = 'optimal'
        return MagicMock()

@pytest.fixture
def mock_availability_horizon_matrix():
    return AvailabilityHorizonMatrix(num_parking_spots=NUM_PARING_FIELDS, time_step_size=timedelta(seconds=1))

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
    raw_obs = {"current_time": 0,
               "price_table": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],
               "user_requests": [0,1,1,1,1],
               "energy_requests": [0,30,40,50,60],
               "field_indices_ginis" : [1],
               "soc_ginis": [0.5],
               "charging_states": [0.1,0.2,0.3,0.4,0.5],
               "ev_energy": [50,70,80,90,10],
               "gini_states": [1],
               "field_kinds": [0,1,2,3,4]}
    return raw_obs

@pytest.fixture
def mpc_config(predictor,mock_availability_horizon_matrix):
    return {
        "N_pred": 23,
        "number_parking_fields": NUM_PARING_FIELDS,
        "solver": MockSolver(),
        "predictor": predictor,
        "availability_horizon_matrix": mock_availability_horizon_matrix,
        "model": None
    }

@pytest.fixture
def action_raw_base(area_size=5, amount_ginis=2):
    action_raw_base={
        "requested_gini_field": np.full(amount_ginis,None),
        "requested_gini_power": np.full(amount_ginis,None),
        "target_charging_power" : np.full(area_size,None),
        "request_answer": np.full(area_size,None),
        "target_stat_battery_charging_power": [0]
    }
    return action_raw_base

@pytest.fixture
def mpc():
    mockmpc = Model_Predictive_Controller(
                                          solver=MagicMock(),
                                            predictor=MagicMock(),
                                            model=MagicMock(),
                                            env_translator=MagicMock())
    #mockmpc.initialize_mpc()
    return mockmpc


@pytest.fixture
def initialized_mpc(mpc_config):
    mpc = Model_Predictive_Controller(mpc_config=mpc_config)
    mpc.setup_variables()
    mpc.setup_parameters()
    mpc.setup_objective()
    return mpc

@pytest.fixture
def fake_optimization_model():
    # return FakeOptimizationModel(number_parking_fields=NUM_PARING_FIELDS, 
    #                              length_prediction_horizon=23,
    #                              amount_ginis=1)
    return MagicMock()

class TestModelPredictiveControler:

    #@pytest.mark.usefixtures("mpc_config")
    def test_init(self, mpc_config):
        mpc = Model_Predictive_Controller(
                                          solver=MagicMock(),
                                            predictor=MagicMock(),
                                            model=MagicMock(),
                                            env_translator=MagicMock())
        
        assert mpc.current_time_step == 0


    def test_update_time_step(self, mpc: Model_Predictive_Controller):
        mpc.predictor = fake_predictor
        mpc.update_time_step(1)
        assert mpc.current_time_step == 1

    def test_update_model_price(self, 
                                mpc: Model_Predictive_Controller,
                                fake_optimization_model,
                                mock_raw_obs,
                                action_raw_base):
        mpc.model = fake_optimization_model
        mpc.env_translator.initialize_model(mpc.model)
        mpc.initialize_action(action_raw_base=action_raw_base)
        mpc.update_model(mock_raw_obs)
        assert True

    def test_update_prediction(self, mpc:Model_Predictive_Controller, mock_raw_obs,predictor):
        mpc.predictor = predictor
        mpc.predictor.prediction_state_updater.env_mpc_mapper.field_to_parking_spot_mapping = {0:0,1:1,2:2,3:3,4:4}
        mpc.update_prediction(raw_obs=mock_raw_obs)
        assert True

    def test_solve(self, mpc: Model_Predictive_Controller):
        mpc.solver = MockSolver()
        mpc._solve()
        assert mpc.solver.status == 'ok'
        assert mpc.solver.termination_condition == 'optimal'

    def test_initialize_action(self,mpc: Model_Predictive_Controller, action_raw_base):

        mpc.initialize_action(action_raw_base=action_raw_base)
        assert "requested_gini_field" in mpc.action
        assert "requested_gini_power" in mpc.action
        assert "target_charging_power" in mpc.action
        assert "request_answer" in mpc.action
        assert "target_stat_battery_charging_power" in mpc.action
        assert mpc.action["requested_gini_field"] is not None
        assert mpc.action["requested_gini_power"] is not None
        assert mpc.action["target_charging_power"] is not None
        assert mpc.action["request_answer"] is not None
        assert mpc.action["target_stat_battery_charging_power"][0]  == 0



    def test_construct_one_step_action(self, mpc: Model_Predictive_Controller, 
                                       action_raw_base):
        mpc.initialize_action(action_raw_base)     
        mpc.env_translator.initialize_model(mpc.model) 
        
        
        mpc.model.setup_variables()
        mpc.model.P_robot_charge[0].value = 100
        mpc.model.P_robot_discharge[0].value = 0
        mpc._construct_one_step_action()
        mpc.env_translator.translate_request_gini_field_from_model_to_action.assert_called
        mpc.env_translator.translate_request_gini_power_from_model_to_action.assert_called
        mpc.env_translator.translate_target_charging_power_from_model_to_action.assert_called
        mpc.env_translator.translate_target_stat_battery_charging_power_from_model_to_action.assert_called

    # def test_calculate_energy_request(self):
    #     raise NotImplementedError("This should only be here temporary, calculate_energy_request is not well placed in this module")


        
    def test_calculate_energy_request(self):
        energy_actual = [0,20,30,40,100]
        soc_obs = [0,0.2,0.3,0.4,1]
        e_total = [100, 100, 100, 100, 100]

        energy_request = calculate_energy_request(Ev_actual_energy=energy_actual, 
                                                  Ev_soc_obs=soc_obs)
        assert energy_request == [100*3600*1000,80,70,60,0]
    
    def test_calculate_energy_request_double_check(self):
        energy_actual = [0,20,30,40,100]
        soc_obs = [0,0.2,0.3,0.4,1]
        e_total = [100, 100, 100, 100, 100]

        energy_request = calculate_energy_request(Ev_actual_energy=energy_actual, 
                                                  Ev_soc_obs=soc_obs)
        for i,e_req in enumerate(energy_request):
            if soc_obs[i] == 0:
                assert e_req == 100*3600*1000
            else:
                assert e_req + energy_actual[i] == e_total[i]



