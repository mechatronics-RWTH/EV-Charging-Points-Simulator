from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import TimeManager, InterfaceTimeManager
import pytest
from datetime import datetime, timedelta

time_manager_singleton_test = TimeManager(start_time=datetime.now(),
                            step_time=timedelta(minutes=5),
                            sim_duration=timedelta(days=1))

class TimeDependentClassWrong(InterfaceTimeManager):
    pass 

class TimeDependentClass(InterfaceTimeDependent):
    def __init__(self):
        self._time_manager = TimeManager(start_time=datetime.now(),
                                        step_time=timedelta(minutes=5),
                                        sim_duration=timedelta(days=1))

    @property
    def time_manager(self) -> TimeManager:
        return self._time_manager


@pytest.fixture
def time_manager():
    time_manager = TimeManager(start_time=datetime.now(),
                                step_time=timedelta(minutes=5),
                                sim_duration=timedelta(days=1))
    return time_manager

class TestTimeDependent:

    def test_init_time_dependent_without_time_manager(self):
        with pytest.raises(TypeError):
            time_dependent_object = TimeDependentClassWrong()

    def test_init_time_dependent_correctly(self):
        time_dependent_object = TimeDependentClass()
        assert time_dependent_object.time_manager is not None


    def test_time_manager_init(self):
        time_manager = TimeManager(start_time=datetime.now(),
                                step_time=timedelta(minutes=5),
                                sim_duration=timedelta(days=1))
        assert isinstance(time_manager, InterfaceTimeManager)

    def test_time_manager_set_time_wrong_type(self,
                                              time_manager: InterfaceTimeManager):

        with pytest.raises(TypeError):
            time_manager.set_current_time(1)

    def test_time_manager_set_current_time_correctly(self,
                                                     time_manager: InterfaceTimeManager):

        current_time = datetime(2021, 1, 1, 0, 0)
        time_manager.set_current_time(current_time)
        assert time_manager.current_time == current_time
    
    def test_time_manager_set_step_time_wrong_type(self,
                                                   time_manager: InterfaceTimeManager):

        with pytest.raises(TypeError):
            time_manager.set_step_time(1)
    
    def test_time_manager_set_step_time_correctly(self,
                                                  time_manager: InterfaceTimeManager):

        time_manager.set_step_time(timedelta(minutes=1))
        assert time_manager.step_time == timedelta(minutes=1)

    def test_get_current_time(self,
                              time_manager: InterfaceTimeManager):

        current_time = datetime(2021, 1, 1, 0, 0)
        time_manager.set_current_time(current_time)
        assert time_manager.get_current_time() == current_time

    def test_get_step_time(self,
                           time_manager: InterfaceTimeManager):

        time_manager.set_step_time(timedelta(minutes=1))
        assert time_manager.get_step_time() == timedelta(minutes=1)

    def test_get_start_of_the_day_datetime(self,
                                           time_manager: InterfaceTimeManager):

        current_time = datetime(2021, 1, 1, 0, 0)
        time_manager.set_current_time(current_time)
        assert time_manager.get_start_of_the_day_datetime() == datetime(2021, 1, 1, 0, 0)
    
    def test_get_end_of_the_day_datetime(self,
                                         time_manager: InterfaceTimeManager):

        current_time = datetime(2021, 1, 1, 0, 0)
        time_manager.set_current_time(current_time)
        assert time_manager.get_end_of_the_day_datetime() == datetime(2021, 1, 2, 0, 0)
    
    def test_get_start_of_the_week_datetime(self,
                                            time_manager: InterfaceTimeManager):

        current_time = datetime(2021, 1, 1, 0, 0)
        time_manager.set_current_time(current_time)
        assert time_manager.get_start_of_the_week_datetime() == datetime(2020, 12, 28, 0, 0)

    def test_is_singleton(self):
        time_manager_1 = TimeManager(start_time=datetime.now(),
                                    step_time=timedelta(minutes=5),
                                    sim_duration=timedelta(days=1))
        time_manager_2 = TimeManager(start_time=datetime.now(),
                                    step_time=timedelta(minutes=5),
                                    sim_duration=timedelta(days=1))
        assert time_manager_1 is time_manager_2

    def test_time_manager_instance_1(self):
        instance1 = TimeManager(start_time=datetime.now(),
                                step_time=timedelta(minutes=5),
                                sim_duration=timedelta(days=1))
        assert instance1 is not None

    def test_time_manager_instance_2(self):
        instance2 = TimeManager(start_time=datetime.now(),
                                step_time=timedelta(minutes=5),
                                sim_duration=timedelta(days=1))
        assert instance2 is not None
        assert instance2 is not time_manager_singleton_test


