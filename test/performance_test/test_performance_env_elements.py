import pytest
from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationEnvironment.GymEnvironment import CustomEnv
import time
from datetime import timedelta
import numpy as np
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

@pytest.fixture(scope="function")
def custom_env():

    gym_config = EnvConfig.load_env_config(config_file="test/env_config_test.json")
    custom_env= CustomEnv(config=gym_config)
    custom_env.time_manager.reset_time()
    yield custom_env
    #return custom_env

def infer_unit(mean_time):
    if mean_time < 1e3:        # Nanoseconds
        return 'ns'
    elif mean_time < 1e6:      # Microseconds
        return 'us'
    else:                      # Milliseconds or higher
        return 'ms'

def get_time_from_stats(stats):
    mean_time = stats["mean"]
    # unit = infer_unit(mean_time)
    # if unit == 'ns':
    #     factor = 1e-3
    # elif unit == 'us':
    #     factor = 1
    # elif unit == 'ms':
    #     factor = 1e3
    factor = 1e3
    print(f"time in s {mean_time}, time in ms {mean_time*factor}")
    return timedelta(seconds=mean_time)

def create_simple_action(custom_env: CustomEnv):
    #custom_env.time_manager.reset_time()
    num_ginis = len(custom_env.gini_mover.ginis)
    num_parking_fields = len(custom_env.parking_area.parking_area_fields)
    action={
            "requested_gini_field": np.full(num_ginis,None),
            "requested_gini_power": np.full(num_ginis,None),
            "target_charging_power" : np.full(num_parking_fields,None),
            "request_answer": np.full(num_parking_fields,None),
            "target_stat_battery_charging_power" : [None]
        } 

    for i in range(num_ginis):
        custom_env.gini_mover.ginis[i]._current_field = custom_env.parking_area._get_field_by_index(i)
        action["requested_gini_field"][i] = custom_env.parking_area.parking_spot_list[i].index

    return action

class TestRawEnvPerformance:
    max_time_reset = timedelta(seconds=5)
    max_time_read_actions = timedelta(milliseconds=2.5)
    max_time_env_step = timedelta(milliseconds=10)
    max_time_update_parking_area = timedelta(milliseconds=0.5)
    max_time_csm_step = timedelta(milliseconds=0.5)
    max_time_step_elements = timedelta(milliseconds=0.5)
    max_time_write_obs = timedelta(milliseconds=20)
    max_time_calculate_connection_points = timedelta(milliseconds=0.8)
    max_time_move_ginis = timedelta(milliseconds=1.5)

    @pytest.mark.benchmark
    def test_performance_env_reset(self, custom_env: CustomEnv, benchmark):
        def reset_env():
            custom_env.reset()

        result = benchmark(reset_env)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_reset

    @pytest.mark.benchmark
    def test_env_step(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)
        
        custom_env.raw_env_space_manager.validate_to_fit_space(custom_env.action_space_raw, actions)
        def step_env():
            try:
                custom_env.step(actions)
            except Exception as e:
                logger.error(f"Error in env step: {e}")

        result = benchmark(step_env)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_env_step
        print(f" calculate from stats: {get_time_from_stats(stats=stats)} and max time: {self.max_time_env_step}")

    @pytest.mark.benchmark
    def test_read_actions_performance(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def read_actions():
            custom_env.read_actions(actions)

        result = benchmark(read_actions)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_read_actions

    @pytest.mark.benchmark
    def test_performance_validate_actions(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def validate_actions():
            custom_env.raw_env_space_manager.validate_to_fit_space(custom_env.action_space_raw, actions)

        result = benchmark(validate_actions)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements

    @pytest.mark.benchmark
    def test_performance_set_request_commands(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def set_request_commands():
            custom_env.charging_session_manager.set_request_commands(actions["request_answer"])

        result = benchmark(set_request_commands)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements

    @pytest.mark.benchmark
    def test_performance_set_gini_targets(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def set_gini_targets():
            custom_env.gini_mover.set_gini_targets(actions["requested_gini_field"])

        result = benchmark(set_gini_targets)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats)< self.max_time_step_elements

    @pytest.mark.benchmark
    def test_performance_set_new_gini_max_limits(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def set_new_gini_max_limits():
            custom_env.gini_mover.set_new_gini_max_limits(actions["requested_gini_power"])

        benchmark(set_new_gini_max_limits)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements

    @pytest.mark.benchmark
    def test_performance_set_new_cs_max_limits(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def set_new_cs_max_limits():
            custom_env.parking_area.set_new_cs_max_limits(actions["target_charging_power"])

        benchmark(set_new_cs_max_limits)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements

    @pytest.mark.benchmark
    def test_performance_new_stat_storage_target(self, custom_env: CustomEnv, benchmark):
        actions = create_simple_action(custom_env)

        def new_stat_storage_target():
            custom_env.read_new_stat_storage_target(actions["target_stat_battery_charging_power"])

        benchmark(new_stat_storage_target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements,(
        f"Performance test failed: Execution time {get_time_from_stats(stats=stats)} "
        f"exceeds the maximum allowed time {self.max_time_step_elements}"
    )

    @pytest.mark.benchmark
    def test_performance_update_parking_area(self, custom_env: CustomEnv, benchmark):
        def update_parking_area():
            custom_env.parking_area.update_parking_area()

        benchmark(update_parking_area)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats)< self.max_time_update_parking_area

    @pytest.mark.benchmark
    def test_performance_csm_step(self, custom_env: CustomEnv, benchmark):
        custom_env.charging_session_manager.set_request_commands(np.full(len(custom_env.parking_area.parking_area_fields),0))
        def csm_step():
            custom_env.charging_session_manager.step()

        benchmark(csm_step)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_csm_step



    @pytest.mark.performance
    def test_performance_calculate_connection_point_load(self,benchmark, custom_env: CustomEnv):
        def target():
            custom_env.local_grid.calculate_connection_point_load()
        benchmark.group = "calculate_connection_point_load"
        benchmark(target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_calculate_connection_points

    @pytest.mark.performance
    def test_performance_simulate_traffic(self,benchmark, custom_env: CustomEnv):
        custom_env.parking_area.update_parking_area()
        def target():
            try:
                custom_env.traffic_simulator.simulate_traffic()
            except Exception as e:
                logger.error(f"Error in simulate_traffic: {e}")
        benchmark.group = "simulate_traffic"
        benchmark(target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_step_elements

    @pytest.mark.performance
    def test_performance_move_ginis(self,benchmark, custom_env: CustomEnv):
        def target():
            for i, gini in enumerate(custom_env.gini_mover.ginis):
                field = custom_env.parking_area.parking_spot_list[i]    
                gini.set_target_field(custom_env.parking_area.parking_spot_list[i+len(custom_env.gini_mover.ginis)])

            custom_env.gini_mover.move_ginis()
        benchmark.group = "move_ginis"
        benchmark(target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats)  < self.max_time_move_ginis

    @pytest.mark.performance
    def test_performance_perform_time_step(self,benchmark, custom_env: CustomEnv):
        def target():
            custom_env.time_manager.perform_time_step()
        benchmark.group = "perform_time_step"
        benchmark(target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats)  < self.max_time_step_elements

    @pytest.mark.performance
    def test_performance_write_obs(self,benchmark, custom_env: CustomEnv):
        def target():
            custom_env.local_grid.calculate_connection_point_load()
            assert len(custom_env.local_grid.power_trajectory) > 0
            custom_env.raw_env_space_manager.write_observations()
        benchmark.group = "write_obs"
        benchmark(target)
        stats = benchmark.stats
        assert get_time_from_stats(stats=stats) < self.max_time_write_obs


