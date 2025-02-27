from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
from test.performance_test.conf_performance_power_trajectory import PowerTypeBasedPowerTrajectory, NpBasedPowerTrajectory
import pytest

STARTTIME = datetime(2022, 1, 1, 0, 0, 0)

@pytest.fixture
def power_trajectory():
    return PowerTrajectory()

def add_powertrajectory(power_trajectory: PowerTrajectory ):
    start_time = STARTTIME
    power_values = [100, 200, 150]  # Add your desired power values here
    for i, power in enumerate(power_values):
        time = start_time + timedelta(hours=i)
        power_trajectory.add_power_value(PowerType(power, PowerTypeUnit.KW), time)

@pytest.fixture
def power_type_based_trajectory():
    power_trajectory = PowerTypeBasedPowerTrajectory()
    add_powertrajectory(power_trajectory)
    return power_trajectory

@pytest.fixture
def np_based_trajectory():
    power_trajectory = NpBasedPowerTrajectory()
    # Add a trajectory of datetimes and power values
    add_powertrajectory(power_trajectory)
    return power_trajectory

class TestPerformancePowerTrajectory:

    @pytest.mark.performance
    def test_np_based_trajectory(self, benchmark, np_based_trajectory: NpBasedPowerTrajectory):
        def target():
            np_based_trajectory.get_power_at_time(STARTTIME + timedelta(hours=1))
        benchmark.group = "get_power_at_time"
        benchmark(target)
        stats = benchmark.stats
        assert stats["mean"] < 1e6  # Target execution time in nanoseconds

    @pytest.mark.performance
    def test_power_type_based_trajectory(self, benchmark, power_type_based_trajectory: PowerTypeBasedPowerTrajectory):
        def target():
            power_type_based_trajectory.get_power_at_time(STARTTIME + timedelta(hours=1))
        benchmark.group = "get_power_at_time"
        benchmark(target)
        stats = benchmark.stats
        assert stats["mean"] < 1e6  # Target execution time in nanoseconds


    

    @pytest.mark.performance
    def test_np_based_add_power_value(self, benchmark, np_based_trajectory: NpBasedPowerTrajectory):
        benchmark.group = "add_power_value"
        benchmark(np_based_trajectory.add_power_value, PowerType(10), STARTTIME + timedelta(hours=1))
        stats = benchmark.stats
        assert stats["mean"] < 1e6  # Target execution time in nanoseconds

    @pytest.mark.performance
    def test_power_type_add_power_value(self, benchmark, power_type_based_trajectory: PowerTypeBasedPowerTrajectory):
        benchmark.extra_info['min_rounds'] = 10  # Set minimum rounds
        benchmark.group = "add_power_value"
        execution_time = benchmark(power_type_based_trajectory.add_power_value, PowerType(10), STARTTIME + timedelta(hours=1))
        stats = benchmark.stats
        assert stats["mean"] < 1e6  # Target execution time in nanoseconds