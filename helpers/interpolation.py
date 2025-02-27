from datetime import timedelta, datetime, time, date
from typing import Union
import numpy as np

from SimulationModules.datatypes.PowerType import PowerType
from helpers.Diagnosis import timeit


def get_data_from_lookup_table(timeAxis, dataAxis, date_time: Union[datetime, timedelta, float]):

    if isinstance(timeAxis[0],time):
        timeAxis = np.array([datetime.combine(date.today(), val) for val in list(timeAxis)])
    starttime_in_s = timeAxis[0]

    timeAxis= list(timeAxis-starttime_in_s)
    timeAxis = np.array([t.total_seconds() for t in timeAxis])
    dataAxis = np.array([val.value for val in list(dataAxis)])

    if isinstance(date_time, datetime):

        time_delta=date_time-starttime_in_s
        total_secs = time_delta.total_seconds()
    elif isinstance(date_time, timedelta):
        total_secs = date_time.total_seconds()
    elif isinstance(date_time, float):
        total_secs = date_time
    elif isinstance(date_time, int):
        total_secs = float(date_time)

    return PowerType(np.interp(total_secs, timeAxis, dataAxis))