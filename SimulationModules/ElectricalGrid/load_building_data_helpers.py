import os
from enum import IntEnum
from config.definitions import ROOT_DIR
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType
from helpers.interpolation import get_data_from_lookup_table
from helpers.data_handling import convert_to_datetime, read_data_excel
import numpy as np
import pickle
from datetime import datetime, timedelta

SOURCE_FILEPATH = os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "Repräsentative Profile VDEW.xls")
DATA_FILEPATH=os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "building_power_year.pkl")

class Season(IntEnum):
    WINTER = 1
    TRANSIT = 2
    SUMMER = 3

class DayCategory(IntEnum):
    WORKDAY = 1
    SATURDAY = 2
    SUNDAY = 3

DayStringMapping = {DayCategory.WORKDAY: 'workday',
                DayCategory.SATURDAY: 'saturday',
                DayCategory.SUNDAY: 'sunday'}

SeasonStringMapping = {Season.WINTER: 'winter',
                Season.TRANSIT: 'transit',
                Season.SUMMER: 'summer'}

usedcols_map = {
        (Season.SUMMER, DayCategory.WORKDAY): 'A, G',
        (Season.SUMMER, DayCategory.SATURDAY): 'A, E',
        (Season.SUMMER, DayCategory.SUNDAY): 'A, F',
        (Season.WINTER, DayCategory.WORKDAY): 'A, D',
        (Season.WINTER, DayCategory.SATURDAY): 'A, B',
        (Season.WINTER, DayCategory.SUNDAY): 'A, C',
        (Season.TRANSIT, DayCategory.WORKDAY): 'A, J',
        (Season.TRANSIT, DayCategory.SATURDAY): 'A, H',
        (Season.TRANSIT, DayCategory.SUNDAY): 'A, I'
    }

START_TIME = convert_to_datetime('20200101:0010')
END_TIME = convert_to_datetime('20201231:2330')


def read_standard_load_data(season: str = Season.SUMMER,
                            day: str = DayCategory.WORKDAY,
                            yearly_consumption: EnergyType = EnergyType(100000, unit=EnergyTypeUnit.KWH)):

    try:
        usedcols = usedcols_map[(season, day)]
    except KeyError:
        raise ValueError(f"{season} and {day} are invalid")

    data = read_data_excel(SOURCE_FILEPATH, usedcols=usedcols)
    data= data.dropna()
    data = data.to_numpy()
    time_axis =  np.array([d[0] for d in data])
    factor= yearly_consumption/EnergyType(1000, unit=EnergyTypeUnit.KWH)

    power_data = np.array(PowerType([factor*d[1] for d in data]))
    return time_axis, power_data

# TODO: this can rather be functions, not methods, they only artificially belong to the class
def transform_raw_source_file():

    raw_data={}
    energy = EnergyType(1000, unit=EnergyTypeUnit.KWH)

    for season in SeasonStringMapping.keys():
        for day_category, suffix in DayStringMapping.items():
            key = f"power_data_{season.name.lower()[0]}_{suffix}"
            raw_data["timeAxis"], raw_data[key] = read_standard_load_data(season, day_category, energy)
    start_time = datetime(year=2020, month=1, day=1, hour=0, minute=0)
    delta_t=timedelta(minutes=15)
    time_steps = timedelta(hours=24)/delta_t
    date_times= [start_time + i*delta_t for i in range(time_steps)]

    building_power_year={
                        season:{ weekday:{
                                            date_time.time(): -get_power_from_raw_source(date_time, weekday, season, raw_data).get_in_w().value for date_time in date_times
                                        }for weekday in DayStringMapping.values()
                                }for season in SeasonStringMapping.values()
                        }

    with open(DATA_FILEPATH, 'wb') as f:
        pickle.dump(building_power_year, f)

def get_power_from_raw_source(date_time: datetime, weekday: str, season: str, raw_data: dict)-> PowerType:

    if isinstance(date_time, np.float64) or isinstance(date_time, int):
        date_time=START_TIME+timedelta(seconds=int(date_time))


    time=date_time-datetime(date_time.year, date_time.month, date_time.day)


    power=0
    data_name_string = "power_data_" + SeasonStringMapping[season] + "_" + DayStringMapping[weekday]
    power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data[data_name_string], time)*(-1)

    return power

def get_season(date_time: datetime) -> Season:

    spring_start = datetime(date_time.year, 3, 21)
    summer_start = datetime(date_time.year, 5, 15)
    fall_start = datetime(date_time.year, 9, 15)
    winter_start = datetime(date_time.year, 11, 1)
    season= Season.WINTER
    if date_time >= spring_start and date_time < summer_start:
        season= Season.TRANSIT
    elif date_time >= summer_start and date_time < fall_start:
        season= Season.SUMMER
    elif date_time >= fall_start and date_time < winter_start:
        season= Season.WINTER
    return SeasonStringMapping[season]

def get_weekday( date_time: datetime) -> DayCategory:
    weekday=DayCategory.WORKDAY
    day=date_time.weekday()
    if day==5:
        weekday=DayCategory.SATURDAY
    if day==6:
        weekday=DayCategory.SUNDAY
    return DayStringMapping[weekday]


