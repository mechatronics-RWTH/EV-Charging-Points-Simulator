from datetime import timedelta
import pandas as pd
import numpy as np
from typing import Tuple

def read_standard_load_data(FILEPATH: str) -> Tuple[np.ndarray, np.ndarray]:
    data = None
    usecols=[0,1,2]
    if str(FILEPATH).endswith('.csv'):
        data = pd.read_csv(FILEPATH, header=0, sep=";", usecols=usecols)
    elif str(FILEPATH).endswith('.xlsx'):
        data = pd.read_excel(FILEPATH, header=0, usecols=usecols)
    else:
        raise ValueError("Dateityp nicht unterstützt. Bitte eine .csv oder .xlsx Datei verwenden.")
    data = data.dropna()
    data = data.to_numpy()
    #we model the start probability as the mean of columns EFG
    prob=data[:, -1]

    #now we build the time axis according to the length of the list:
    seconds_in_a_week = 7 * 24 * 60 * 60
    step_times=len(prob)
    week_time_axis = np.array([timedelta(seconds=seconds) for seconds in range(0, seconds_in_a_week, int(seconds_in_a_week/step_times))])

    return week_time_axis, prob