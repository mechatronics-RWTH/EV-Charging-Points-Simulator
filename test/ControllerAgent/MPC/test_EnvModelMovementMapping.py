import pytest
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvModelMovementMapping import  (EnvModelMovementMapping, 
                                                                                                 RobotForMapping, 
                                                                                                 ParkingSpotForMapping, 
                                                                                                 ChargingStationForMapping)
from pyomo.environ import Var, Binary
from unittest.mock import MagicMock
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper

horizon = 5
num_robots = 2
num_parking_spots = 4
num_chargers = 3


@pytest.fixture
def env_model_movement_mapping():
    env_mpc_mapper: InterfaceEnvMpcMapper =MagicMock(wraps=InterfaceEnvMpcMapper)
    env_mpc_mapper.get_num_parking_spots = MagicMock(return_value=num_parking_spots)
    env_mpc_mapper.get_num_chargers = MagicMock(return_value=num_chargers)
    env_mpc_mapper.get_num_robots = MagicMock(return_value=num_robots)
    env_model_movement_mapping = EnvModelMovementMapping(env_mpc_mapper=env_mpc_mapper)
    return env_model_movement_mapping

@pytest.fixture
def z_charger_occupied():
    z_charger_occupied = Var(range(horizon), range(num_robots), range(num_parking_spots), within=Binary, initialize=0)
    z_charger_occupied.construct()
    return z_charger_occupied

@pytest.fixture
def z_parking_spot():
    z_parking_spot = Var(range(horizon), range(num_robots), range(num_parking_spots), within=Binary, initialize=0)
    z_parking_spot.construct()
    return z_parking_spot

class TestEnvModelMovementMapping:

    def test_EnvModelMovementMapping(self):
        env_mpc_mapper=MagicMock()

        num_robots = 2
        num_parking_spots = 4
        num_chargers = 3
        env_mpc_mapper.get_num_parking_spots = MagicMock(return_value=num_parking_spots)
        env_mpc_mapper.get_num_chargers = MagicMock(return_value=num_chargers)
        env_mpc_mapper.get_num_robots = MagicMock(return_value=num_robots)
        env_model_movement_mapping = EnvModelMovementMapping(env_mpc_mapper=env_mpc_mapper)

        assert len(env_model_movement_mapping.parking_spots) == num_parking_spots
        assert len(env_model_movement_mapping.charging_station) == num_chargers
        assert len(env_model_movement_mapping.robots) == num_robots

    def test_assign_current_occupations(self, 
                                        env_model_movement_mapping: EnvModelMovementMapping,
                                    z_charger_occupied,
                                    z_parking_spot):
        env_model_movement_mapping.assign_current_occupations(z_charger_occupied, z_parking_spot)
        assert len(env_model_movement_mapping.robots[0].at_charger_boolean_list) == num_chargers
        assert len(env_model_movement_mapping.robots[0].at_parking_spot_boolean_list) == num_parking_spots


    
    def test_update_robot_positions_error(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.robots = [RobotForMapping(num=0, at_charger_boolean_list=[1, 0, 0], at_parking_spot_boolean_list=[0, 1, 0]),
                                             ]
        with pytest.raises(ValueError):
            env_model_movement_mapping.update_robot_positions()

    def test_update_robot_positions_at_parking_spot(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.robots = [RobotForMapping(num=0, at_charger_boolean_list=[0, 0, 0], at_parking_spot_boolean_list=[0, 1, 0]),
                                             ]
        
        env_model_movement_mapping.update_robot_positions()
        assert env_model_movement_mapping.robots[0].get_field().num == 1
        assert isinstance(env_model_movement_mapping.robots[0].get_field(), ParkingSpotForMapping)

    def test_update_robot_positions_at_charger(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.robots = [RobotForMapping(num=0, at_charger_boolean_list=[0, 0, 1], at_parking_spot_boolean_list=[0, 0, 0]),
                                             ]
        
        env_model_movement_mapping.update_robot_positions()
        assert env_model_movement_mapping.robots[0].get_field().num == 2
        assert isinstance(env_model_movement_mapping.robots[0].get_field(), ChargingStationForMapping)


    def test_get_env_based_field_index_for_robot_parking_spot(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.env_mpc_mapper = MagicMock()
        env_model_movement_mapping.env_mpc_mapper.get_field_index_from_parking_spot_id = MagicMock(return_value=2)
        env_model_movement_mapping.robots = [RobotForMapping(num=0, field=ParkingSpotForMapping(num=1)),
                                             ]
        assert env_model_movement_mapping.get_env_based_field_index_for_robot() == [2]

    def test_get_env_based_field_index_for_robot_charging_spot(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.env_mpc_mapper = MagicMock()
        env_model_movement_mapping.env_mpc_mapper.get_charging_spot_by_index = MagicMock(return_value=5)
        env_model_movement_mapping.robots = [RobotForMapping(num=0, field=ChargingStationForMapping(num=1)),
                                             ]
        assert env_model_movement_mapping.get_env_based_field_index_for_robot() == [5]

    def test_get_env_based_field_index_for_robot_None_error(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.env_mpc_mapper = MagicMock()
        env_model_movement_mapping.env_mpc_mapper.get_charging_spot_by_index = MagicMock(return_value=5)
        env_model_movement_mapping.robots = [RobotForMapping(num=0, field=None),
                                             ]
        with pytest.raises(ValueError):
            env_model_movement_mapping.get_env_based_field_index_for_robot()

    def test_get_env_based_field_index_for_robot_multi(self,
                                    env_model_movement_mapping: EnvModelMovementMapping,):
        env_model_movement_mapping.env_mpc_mapper = MagicMock()
        env_model_movement_mapping.env_mpc_mapper.get_charging_spot_by_index = MagicMock(return_value=5)
        env_model_movement_mapping.env_mpc_mapper.get_field_index_from_parking_spot_id = MagicMock(return_value=2)
        env_model_movement_mapping.robots = [RobotForMapping(num=0, field=ChargingStationForMapping(num=1)),
                                                RobotForMapping(num=1, field=ParkingSpotForMapping(num=1)),
                                             ]
        assert env_model_movement_mapping.get_env_based_field_index_for_robot() == [5, 2]