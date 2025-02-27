from SimulationEnvironment.EnvBuilder import EnvBuilder
import pytest

@pytest.mark.skip(reason="Not yet implemented")
class TestEnvBuilder:

    def test_env_builder(self):
        env_builder = EnvBuilder({})
        env_builder.build_time_manager()
        env_builder.build_parking_area()
        env_builder.build_traffic_simulator()
        env_builder.build_local_grid()
        env_builder.build_charging_session_manager()
        env_builder.build_electricity_cost()
        env_builder.build_gini_mover()
        env_builder.build_reward_system()
        assert True