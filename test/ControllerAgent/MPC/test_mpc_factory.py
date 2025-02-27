from Controller_Agent.Model_Predictive_Controller.MpcFactory import MPCFactory
import pytest
from unittest.mock import MagicMock, patch 

@pytest.fixture
def mpc_config():
    mpc_config = MagicMock()
    return mpc_config

@pytest.fixture
def mpc_factory(mpc_config):
    mpc_factory = MPCFactory(mpc_config=mpc_config,
                             env_config=MagicMock())
    return mpc_factory



class TestMpcFactory:

    def test_init(self, mpc_config):
        mpc_factory =MPCFactory(mpc_config=mpc_config,
                                env_config=MagicMock())
        assert mpc_factory.availability_horizon_matrix == None
        assert mpc_factory.predicted_ev_collection == None
        assert mpc_factory.env_mpc_mapper == None
        assert mpc_factory.prediction_algorithm == None
        assert mpc_factory.prediction_state_updater == None

    def test_create_availability_horizon_matrix(self,mpc_factory:MPCFactory):
        mpc_factory.env_mpc_mapper = MagicMock()
        mpc_factory._create_availability_horizon_matrix()
        assert mpc_factory.availability_horizon_matrix != None


    def test_create_solver(self, mpc_factory: MPCFactory):

        mpc_factory._create_solver()
        assert mpc_factory.solver != None

    def test_create_ev_collection(self, mpc_factory: MPCFactory):

        mpc_factory._create_ev_collection()
        assert mpc_factory.predicted_ev_collection != None

    def test_create_env_mpc_mapper(self,mpc_factory: MPCFactory):

        mpc_factory._create_env_mpc_mapper()
        assert mpc_factory.env_mpc_mapper != None

    def test_create_prediction_algorithm(self, mpc_factory: MPCFactory):

        mpc_factory._create_prediction_algorithm()
        assert mpc_factory.prediction_algorithm != None

    def test_create_prediction_state_updater(self, mpc_factory:MPCFactory):

        mpc_factory._create_prediction_state_updater()
        assert mpc_factory.prediction_state_updater != None

    def test_create(self,mpc_factory: MPCFactory):

        # with patch.object(mpc_factory.env_mpc_mapper, 'get_num_chargers', return_value=5), \
        #     patch.object(mpc_factory.env_mpc_mapper, 'count_parking_spots', return_value=3), \
        #         patch.object(mpc_factory.env_mpc_mapper, 'get_num_robots', return_value=2):
        observation = MagicMock()
        observation.__getitem__.side_effect = lambda key: {
            'field_kinds': [0,1,2,3,4],
            'user_requests': [0,1,2,3,4],
            'field_indices_ginis': [0,1,2,3,4],
            'soc_ginis': [0,0.5], 
            'gini_states': [0,1],
            'gini_energy': [10,10],
            'ev_energy': [10,10],
            'charging_states': [0,1,2,3,4],
            'price_table': [0,1,2,3,4],
            'pred_building_power': [0,1,2,3,4],
            'pred_pv_power': [0,1,2,3,4]
            }[key]
        mpc_factory.config.horizon_steps = 24
        mpc = mpc_factory.create(observation=observation, action=MagicMock())
        assert mpc != None
        assert mpc.solver != None
        assert mpc.predictor != None
        assert mpc.model != None
        assert mpc.env_translator != None
        assert mpc.current_time_step == 0
        assert mpc.initialized_mpc == False
        assert mpc_factory.availability_horizon_matrix != None
        assert mpc_factory.predicted_ev_collection != None
        assert mpc_factory.env_mpc_mapper != None
        assert mpc_factory.prediction_algorithm != None
        assert mpc_factory.prediction_state_updater != None
        assert mpc_factory.predictor != None
        assert mpc_factory.optimization_model != None
        assert mpc_factory.solver != None