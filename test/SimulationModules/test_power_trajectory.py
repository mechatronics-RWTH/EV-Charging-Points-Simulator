from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory, TimeOutOfRangeErrorHigh
from SimulationModules.datatypes.PowerType import PowerType
from datetime import datetime, timedelta
import pytest

class TestPowerTrajectory:

    def setup_method(self):
        self.power_trajectory = PowerTrajectory()

    def test_init_power_trajectory(self):
        pwr_traj = PowerTrajectory()
        print(pwr_traj.power)
        assert len(pwr_traj) ==0

    def test_get_power_at_time(self):
        power_trajectory = PowerTrajectory()
        power_trajectory.power = [PowerType(i) for i in range(10)]
        start_time = datetime(year=2024, month=3, day=11, hour=0, minute=0, second=0)
        power_trajectory.time = [start_time + timedelta(minutes=1*i) for i in range(10)]
        power_trajectory._determine_np_values()
        assert power_trajectory.get_power_at_time(start_time+timedelta(minutes=5)) == PowerType(5)


    def test_get_power_at_time_not_at_timestamp(self):
        power_trajectory = PowerTrajectory()
        power_trajectory.power = [PowerType(i) for i in range(10)]
        start_time = datetime(year=2024, month=3, day=11, hour=0, minute=0, second=0)
        power_trajectory.time = [start_time + timedelta(minutes=1*i) for i in range(10)]
        power_trajectory._determine_np_values()
        assert power_trajectory.get_power_at_time(start_time+timedelta(minutes=4, seconds=30)) == PowerType(4.5)

    def test_get_power_at_time_beyond_timestamps(self):
        power_trajectory = PowerTrajectory()
        power_trajectory.power = [PowerType(i) for i in range(10)]
        start_time = datetime(year=2024, month=3, day=11, hour=0, minute=0, second=0)
        power_trajectory.time = [start_time + timedelta(minutes=1*i) for i in range(10)]
        with pytest.raises(TimeOutOfRangeErrorHigh):
            power_trajectory.get_power_at_time(start_time+timedelta(minutes=90))

    def test_get_power_at_time_before_timestamps(self):
        power_trajectory = PowerTrajectory()
        power_trajectory.power = [PowerType(i) for i in range(10)]
        start_time = datetime(year=2024, month=3, day=11, hour=0, minute=0, second=0)
        power_trajectory.time = [start_time + timedelta(minutes=1*i) for i in range(10)]
        with pytest.raises(ValueError):
            power_trajectory.get_power_at_time(start_time-timedelta(minutes=20))