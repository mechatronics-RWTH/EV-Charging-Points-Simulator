from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.ModelEnvTranslator import  ModelEnvTranslator
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceModelEnvTranslator import InterfaceModelEnvTranslator
from test.conftest_observation import raw_obs, action_raw_base#
import pytest
import numpy as np
from SimulationModules.Enums import TypeOfField
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import  EnvMpcMapper
from unittest.mock import MagicMock
from pyomo.environ import Var

@pytest.fixture
def field_kinds():
    return [TypeOfField.GiniChargingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,]

@pytest.fixture
def simple_field_kinds():
    return [TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,]

NUM_PARING_FIELDS = 10
NUM_GINIS=1
PREDICTION_HORIZON = 10

@pytest.fixture
def mock_raw_obs():
    my_raw_obs = raw_obs(area_size=NUM_PARING_FIELDS, amount_ginis=NUM_GINIS)
    user_requests = my_raw_obs["user_requests"]
    user_requests = np.array(user_requests)  # Convert to NumPy array
    user_requests[user_requests > 1] = 1
    my_raw_obs["user_requests"] = user_requests.tolist()
    return my_raw_obs

@pytest.fixture
def action():
    action = action_raw_base(area_size=NUM_PARING_FIELDS, amount_ginis=NUM_GINIS)
    return action

@pytest.fixture
def fake_optimization_model():
    return MagicMock()
    # return FakeOptimizationModel(number_parking_fields=NUM_PARING_FIELDS, 
    #                              length_prediction_horizon=PREDICTION_HORIZON, 
    #                              amount_ginis=NUM_GINIS)

@pytest.fixture
def model_env_translator(action, fake_optimization_model):
    return ModelEnvTranslator(action=action, model=fake_optimization_model,
                              env_mpc_mapper=MagicMock(),
                              env_model_movement_mapping=MagicMock())

class TestModelEnvTranslator:

    
    def test_initialize_observation(self, action, mock_raw_obs):
        model_env_translator = ModelEnvTranslator(action=action, model=None,
                                                  env_mpc_mapper=MagicMock())
        model_env_translator.initialize_observation(mock_raw_obs)
        assert model_env_translator.user_request is not None
        assert model_env_translator.gini_field_indices is not None
        assert model_env_translator.gini_soc is not None
        assert model_env_translator.charging_soc_state is not None
        assert model_env_translator.gini_states is not None

    def test_initialize_action(self, action):
        model_env_translator = ModelEnvTranslator(action=action, model=None)
        assert model_env_translator.action["target_charging_power"] is not None

        action["requested_gini_power"][0] = 10
        action["requested_gini_field"][0] = 20
        action["target_stat_battery_charging_power"][0] = 30
        action["target_charging_power"][0] = 40
        model_env_translator.initialize_action(action)

        assert model_env_translator.action["requested_gini_power"][0] == 10
        assert model_env_translator.action["requested_gini_field"][0] == 20
        assert model_env_translator.action["target_stat_battery_charging_power"][0] == 30
        assert model_env_translator.action["target_charging_power"][0] == 40

    def test_derive_imporant_fields(self, model_env_translator: InterfaceModelEnvTranslator):
        model_env_translator.type_of_field = [TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.GiniChargingSpot.value , 
                                        TypeOfField.ParkingPath.value,
                                        TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.GiniChargingSpot.value , 
                                        TypeOfField.ParkingPath.value]
        model_env_translator.gini_states = [1, 2]
        model_env_translator.initialize_mapper()
        model_env_translator.env_mpc_mapper.create_charging_spot_list.assert_called()
        model_env_translator.env_mpc_mapper.create_parking_spot_id_mapping.assert_called()
        model_env_translator.env_mpc_mapper.count_parking_spots.assert_called()
        model_env_translator.env_mpc_mapper.determine_num_chargers.assert_called()
        model_env_translator.env_mpc_mapper.determine_num_robots.assert_called()

                                                     

    def test_translate_request_gini_field_from_model_to_action(self, 
                                                               model_env_translator: InterfaceModelEnvTranslator,
                                                               mock_raw_obs):
        
        mock_raw_obs["field_kinds"] = [TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.GiniChargingSpot.value , 
                                        TypeOfField.ParkingPath.value,
                                        TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.ParkingPath.value , 
                                        TypeOfField.ParkingPath.value]
        
        model_env_translator.initialize_observation(mock_raw_obs)
        model_env_translator.env_model_movement_mapping = MagicMock()
        model_env_translator.model.z_robot[0].value = 1
        model_env_translator.translate_request_gini_field_from_model_to_action()
        model_env_translator.env_model_movement_mapping.assign_current_occupations.assert_called()
        model_env_translator.env_model_movement_mapping.update_robot_positions.assert_called()
        model_env_translator.env_model_movement_mapping.get_env_based_field_index_for_robot.assert_called()



    def test_translate_request_gini_power_from_model_to_action(self,
                                                               model_env_translator: InterfaceModelEnvTranslator,
                                                               mock_raw_obs):
        model_env_translator.initialize_observation(mock_raw_obs)
        model_env_translator.model.P_robot_charge = Var(range(1),range(1))
        model_env_translator.model.P_robot_charge.construct()
        model_env_translator.model.P_robot_charge[0,0].value = 10
        model_env_translator.model.P_robot_discharge = Var(range(1),range(1))
        model_env_translator.model.P_robot_discharge.construct()
        model_env_translator.model.P_robot_discharge[0,0].value = 0
        model_env_translator.translate_request_gini_power_from_model_to_action()
        assert model_env_translator.action["requested_gini_power"][0] == 10000

    def test_translate_target_charging_power_from_model_to_action(self,
                                                                  model_env_translator: InterfaceModelEnvTranslator,
                                                                  action):
        model_env_translator.initialize_action(action)
        model_env_translator.translate_target_charging_power_from_model_to_action()
        assert model_env_translator.action["target_charging_power"][0] == None
        assert len( model_env_translator.action["target_charging_power"]) == NUM_PARING_FIELDS


    def test_translate_target_stat_battery_charging_power_from_model_to_action(self,
                                                                               model_env_translator: InterfaceModelEnvTranslator,
                                                                  action):
        model_env_translator.initialize_action(action)
        model_env_translator.translate_target_stat_battery_charging_power_from_model_to_action()
        assert model_env_translator.action["target_stat_battery_charging_power"][0] == 0
        assert len( model_env_translator.action["target_stat_battery_charging_power"]) == 1

    def test_get_number_parking_fields(self,
                                       model_env_translator: InterfaceModelEnvTranslator,
                                       mock_raw_obs):
        mock_raw_obs["field_kinds"] = [TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.GiniChargingSpot.value , 
                                        TypeOfField.ParkingPath.value,
                                        TypeOfField.Obstacle.value, 
                                       TypeOfField.ParkingSpot.value, 
                                       TypeOfField.ParkingPath.value,
                                        TypeOfField.ParkingPath.value , 
                                        TypeOfField.ParkingPath.value]
        model_env_translator.initialize_observation(mock_raw_obs)
        assert model_env_translator.get_number_parking_fields() == 2

    def test_update_translation(self, 
                                model_env_translator: InterfaceModelEnvTranslator, 
                                action, 
                                mock_raw_obs):
        
        model_env_translator.initialize_observation(mock_raw_obs)
        model_env_translator.env_model_movement_mapping = MagicMock()
        # Mock P_robot_charge and P_robot_discharge as 2D arrays
        model_env_translator.model.P_robot_charge = Var(range(1),range(1))
        model_env_translator.model.P_robot_charge.construct()
        model_env_translator.model.P_robot_charge[0,0].value = 10
        model_env_translator.model.P_robot_discharge = Var(range(1),range(1))
        model_env_translator.model.P_robot_discharge.construct()
        model_env_translator.model.P_robot_discharge[0,0].value = 5
        model_env_translator.update_translation()
        
        assert model_env_translator.action["requested_gini_power"][0] == 10000


            

    
   