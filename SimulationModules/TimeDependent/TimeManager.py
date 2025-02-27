from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class InterfaceTimeManager(ABC):
    @abstractmethod
    def perform_time_step(self) -> None:
        pass

    @abstractmethod
    def get_start_time(self) -> datetime:
        pass

    @abstractmethod
    def get_current_time(self) -> datetime:
        pass
    
    @abstractmethod
    def get_step_time(self) -> timedelta:
        pass

    @abstractmethod
    def set_current_time(self, current_time: datetime, step_time: timedelta) -> None:
        pass

    @abstractmethod
    def set_step_time(self, step_time: timedelta) -> None:
        pass

    @abstractmethod    
    def get_start_of_the_day_datetime(self) -> datetime:
        pass
    
    @abstractmethod
    def get_end_of_the_day_datetime(self) -> datetime:
        pass
    
    @abstractmethod
    def get_start_of_the_week_datetime(self) -> datetime:
        pass
    
    @abstractmethod
    def get_stop_time(self) -> datetime:
        pass

    @abstractmethod
    def reset_time(self):
        pass
    
    @abstractmethod
    def get_day_of_the_week(self) -> int:
        pass
    
    @abstractmethod
    def get_week_in_year(self) -> int:
        pass
    
    @abstractmethod
    def get_second_in_day(self) -> int:
        pass

    @abstractmethod
    def reset_start_time(self, start_time: datetime) -> None:
        pass

class TimeManager(InterfaceTimeManager):
    #TODO: Implement Singleton pattern, for now deactivated due to issues during testing
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, 
                 start_time: datetime, 
                 step_time: timedelta,
                 sim_duration: timedelta) -> None:
        if hasattr(self, 'initialized'):
            return
        self.start_time = start_time
        self.current_time = start_time
        self.step_time = step_time
        self.sim_duration = sim_duration
        self.stop_time = start_time + self.sim_duration
        self.initialized = True

    def perform_time_step(self) -> None:
        self.current_time += self.step_time

    def get_start_time(self) -> datetime:
        return self.start_time
    
    def reset_start_time(self, start_time: datetime) -> None:
        if not isinstance(start_time, datetime):
            raise TypeError(f"start_time must be a datetime object, but is {type(start_time)}")
        self.start_time = start_time
        self.current_time = start_time
        self.stop_time = start_time + self.sim_duration

    def set_current_time(self, current_time: datetime) -> None:
        if not isinstance(current_time, datetime):
            raise TypeError(f"current_time must be a datetime object, but is {type(current_time)}")
        self.current_time = current_time
        
    def set_step_time(self, step_time: timedelta) -> None: 
        if not isinstance(step_time, timedelta):
            raise TypeError(f"step_time must be a timedelta object, but is {type(step_time)}")   
        self.step_time = step_time

    def get_current_time(self) -> datetime:
        return self.current_time

    def get_step_time(self) -> timedelta:
        return self.step_time
    
    def get_stop_time(self) -> datetime:
        return self.stop_time
    
    def get_start_of_the_day_datetime(self) -> datetime:
        return self.current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_end_of_the_day_datetime(self) -> datetime:
        return self.get_start_of_the_day_datetime() + timedelta(days=1) 
    
    def get_start_of_the_week_datetime(self) -> datetime:
        return self.current_time - timedelta(days=self.current_time.weekday())

    def reset_time(self):
        self.current_time = self.start_time

    def get_day_of_the_week(self) -> int:
        return self.current_time.weekday()
    
    def get_week_in_year(self) -> int:
        return self.current_time.isocalendar()[1]
    
    def get_second_in_day(self) -> int:
        return self.current_time.hour * 3600 + self.current_time.minute * 60 + self.current_time.second
