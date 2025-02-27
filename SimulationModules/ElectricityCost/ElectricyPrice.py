from datetime import datetime, timedelta
from typing import Union
import os
from bisect import bisect_right

import numpy as np
from abc import ABC, abstractmethod

from config.definitions import ROOT_DIR
from helpers. Diagnosis import timeit
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class InterfacePriceTable(ABC):

    def __init__(self, start_time: datetime):
        self.start_time=start_time

    @abstractmethod
    def get_price(self, date_time: Union[datetime, timedelta, float]):
        raise NotImplementedError
    
    """
    @abstractmethod
    def get_price_table_24h(self, current_time: Union[datetime, timedelta, float, int], step_time: timedelta = timedelta(seconds=900)):
        
        this method gives the energy prices for the current day splitted in the given
        step_times. These are not the prices for the next 24h, but for the 24h of the
        current day starting at 0 o'clock.
        
        raise NotImplementedError
    """
    
    def convert_to_datetime(self, date_time: Union[datetime, timedelta, float, int]):
        """
        this method converts the three types into a datetime
        """
        if isinstance(date_time, datetime):
            return date_time
        elif isinstance(date_time, timedelta):
            return self.start_time+date_time
        elif isinstance(date_time, (float,int)):
            #if a float is given, this float is interpreted as the amount of seconds since
            #the start of the sim
            return self.convert_to_datetime(timedelta(seconds=int(date_time)))
            
    def get_price_future(self,date_time: Union[datetime, timedelta, float], horizon: int = 1, step_times = timedelta(seconds=900) ):

        date_time=self.convert_to_datetime(date_time)
        prices=[self.get_price(date_time+i*step_times) for i in range(horizon)]

        time_delta=date_time-self.start_time
        dt_array=np.array([time_delta.total_seconds() + (step_times.total_seconds() * i) for i in range(horizon)])

        return prices, dt_array

class PriceTable(InterfacePriceTable):

    def __init__(self, start_time: datetime = datetime.now()):

        super().__init__(start_time)

        self.stepsize_hours = 0.25
        self.duration_hours = 24
        self.time = np.arange(0, self.duration_hours, self.stepsize_hours) * 60 * 60
        #self.price = np.array([50, 60, 65, 58, 55, 53, 46, 40, 35, 25, 19, 16, 19, 21, 15, 10,
                               #5, 3, -5, -7, 10, 15, 20, 35])
        #self.price = np.random.randint(0, 200, size=int(duration_hours/stepsize_hours))
        self.price =np.array([17, 68, 196, 46, 187, 193, 144, 145, 120, 89, 128, 198, 195,
               166, 180, 115, 136, 25, 49, 107, 138, 79, 174, 113, 56, 62,
               32, 175, 163, 89, 0, 134, 188, 113, 69, 171, 153, 135, 175,
               83, 96, 81, 23, 29, 64, 73, 181, 162, 0, 35, 106, 88,
               13, 170, 77, 94, 92, 158, 141, 181, 75, 183, 156, 109, 170,
               63, 77, 191, 77, 163, 22, 85, 5, 174, 156, 95, 62, 71,
               97, 169, 50, 195, 41, 183, 61, 44, 38, 67, 154, 99, 35,
               115, 85, 47, 51, 156])
        if len(self.time) != len(self.price):
            msg = f"Length of time vector is {len(self.time)}, while length of price vector is {len(self.price)}\n " \
                  f"Vectors must be same length"
            raise ValueError(msg)

    def get_price(self, date_time: Union[datetime, timedelta, float]):
        xp = self.time
        fp = self.price
        if isinstance(date_time, datetime):
            clocktime = date_time.time()
            time_delta = timedelta(hours=clocktime.hour,
                                   minutes=clocktime.minute,
                                   seconds=clocktime.second)
            total_secs = time_delta.total_seconds()%(self.duration_hours*3600)
        elif isinstance(date_time, timedelta):
            total_secs = date_time.total_seconds()%(self.duration_hours*3600)
        elif isinstance(date_time, float):
            total_secs = date_time%(self.duration_hours*3600)

        return np.interp(total_secs, xp, fp)

    """
    def get_price_table_24h(self,current_time: Union[datetime, timedelta, float, int], step_time: timedelta = timedelta(seconds=900)):
        secs_per_step=step_time.total_seconds()
        steps=timedelta(hours=24).total_seconds()/secs_per_step
        return np.array([np.interp(i*secs_per_step, self.time, self.price) for i in range(int(steps))])
    """

class StockPriceTable(InterfacePriceTable):
    """
    this class uses stock market energy prices from
    https://www.energy-charts.info/charts/price_spot_market/chart.htm?l=de&c=DE
    which are downloaded and used in this simulation
    """
    def __init__(self, start_time: datetime = datetime(year=2022,
                                                          month=8,
                                                          day=8,
                                                          hour=6),
                end_time: datetime = None,
                step_time: timedelta = timedelta(minutes=15),
                horizon=96):
        super().__init__(start_time)
        #Loading path
        file_path = os.path.join(ROOT_DIR, "SimulationModules", "energy-charts_Stromproduktion_und_Boersenstrompreise_in_Deutschland_2022-2024_CSV.txt")
        #Load prices from txt:
        self.prices= np.genfromtxt(file_path,delimiter=';', dtype=None, names=True, converters={0: self.date_converter})

        if end_time is None:
            end_time=max(self.prices, key=lambda x: x[0])[0]
        #we cut all timestamps from the list which are set earlier than starttime
        self.prices=np.array([(time, price) for (time, price) in self.prices if start_time <= time <= end_time+horizon*step_time])
        self.datetime_list = [item[0] for item in self.prices]
        self.prices_list = [item[1] for item in self.prices]

        self.time_steps_list = self.generate_time_steps_list(start_time= min(self.datetime_list), 
                                                            end_time= max(self.datetime_list), 
                                                            delta_t=step_time)
        self.prices_for_time_steps_list = [self.get_price(date_time) for date_time in self.time_steps_list]
        
    def generate_time_steps_list(self, start_time, end_time, delta_t):
        times = []
        current_time = start_time
        while current_time <= end_time:
            times.append(current_time)
            current_time += delta_t
        return times


    def get_price(self, date_time: Union[datetime, timedelta, float, int]):
        price=0

        if isinstance(date_time, datetime):
            #the stock market gets updated hourly, so we set the min & sec to zero
            date_time_hour=date_time.replace(minute=0, second=0, microsecond=0)
            #if necessary, we change the year to 2022, so that it fits our table
            if not (np.min(self.prices[:,0]) <= date_time_hour <= np.max(self.prices[:,0])):
                date_time_hour=date_time_hour.replace(year=2022)
            
            pos = bisect_right(self.datetime_list, date_time_hour) - 1
            price=self.prices_list[pos]

        elif isinstance(date_time, timedelta):
            #if a timedelta is given, we add this timedelta on the starttime and then calculate
            #its referring energy price
            date_time_hour=(self.start_time+date_time).replace(minute=0, second=0, microsecond=0)
            price=self.get_price(date_time_hour)
        elif isinstance(date_time, (float,int)):
            #if a float is given, this float is interpreted as the amount of seconds since
            #the start of the sim
            time_delta=timedelta(seconds=int(date_time))
            price=self.get_price(time_delta)

        return price

    """
    def get_price_table_24h(self, current_time: Union[datetime, timedelta, float, int], step_time: timedelta = timedelta(seconds=900)):
        current_time=self.convert_to_datetime(current_time)
        midnight=current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        steps=timedelta(hours=24).total_seconds()/step_time.total_seconds()
        return np.array([self.get_price(midnight+i*step_time) for i in range(int(steps))])
    """

    def get_price_future(self,date_time: Union[datetime, timedelta, float], horizon: int = 1, step_time = timedelta(seconds=900) ):


        date_time=self.convert_to_datetime(date_time)
        try:
            start_pos = self.time_steps_list.index(date_time)
        except ValueError as e:
            logger.error(f"Date {date_time} not in list")
            raise ValueError(f"Date {date_time} not in list: {e}")
        prices = self.prices_for_time_steps_list[start_pos:start_pos+horizon]

        time_delta=date_time-self.start_time
        dt_array=np.array([time_delta.total_seconds() + (step_time.total_seconds() * i) for i in range(horizon)])

        return prices, dt_array

    #function for conversion of the date column in the read csv
    # into a numpy-conform format
    def date_converter(self, date_string):
        #2022-01-01T02:00+01:00;43.22
        year=int(date_string[:4])
        month=int(date_string[5:7])
        day=int(date_string[8:10])
        hour=int(date_string[11:13])
        min=int(date_string[14:16])

        return datetime(year, month, day, hour, min, 0)
    
