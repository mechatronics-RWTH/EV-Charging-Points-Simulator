from datetime import timedelta, datetime
from SimulationModules.TimeDependent.TimeManager import TimeManager


time_manager = TimeManager(start_time =datetime.now(),
                step_time = timedelta(minutes=5),
                sim_duration = timedelta(days=1))