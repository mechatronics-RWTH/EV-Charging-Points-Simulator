from dataclasses import dataclass
import datetime


@dataclass
class SimSettings:
    step_time: datetime.timedelta
    sim_duration: datetime.timedelta
    start_datetime: datetime.datetime = datetime.datetime(year=2022,
                                                          month=8,
                                                          day=8,
                                                          hour=6)
