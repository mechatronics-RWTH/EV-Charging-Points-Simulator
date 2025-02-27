from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper, EnvMpcMapper
import pytest
from SimulationModules.Enums import TypeOfField


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

class TestEnvMpcMapper:

    def test_create_parking_spot_id_mapping(self,                                            
                                            field_kinds):
        
        env_mpc_mapper = EnvMpcMapper()
        env_mpc_mapper.create_parking_spot_id_mapping(field_kinds)

        assert len(env_mpc_mapper.field_to_parking_spot_mapping) == 5
        assert env_mpc_mapper.field_to_parking_spot_mapping[1] == 0
        assert env_mpc_mapper.field_to_parking_spot_mapping[2] == 1
        assert env_mpc_mapper.field_to_parking_spot_mapping[3] == 2
        assert env_mpc_mapper.field_to_parking_spot_mapping[5] == 3
        assert env_mpc_mapper.field_to_parking_spot_mapping[7] == 4

    def test_get_parking_spot_id_for_field_index(self,
                                                   field_kinds):
        env_mpc_mapper = EnvMpcMapper()
        env_mpc_mapper.create_parking_spot_id_mapping(field_kinds)
        assert env_mpc_mapper.get_parking_spot_id_for_field_index(1) == 0
        assert env_mpc_mapper.get_parking_spot_id_for_field_index(2) == 1
        assert env_mpc_mapper.get_parking_spot_id_for_field_index(3) == 2
        assert env_mpc_mapper.get_parking_spot_id_for_field_index(5) == 3
        assert env_mpc_mapper.get_parking_spot_id_for_field_index(7) == 4
