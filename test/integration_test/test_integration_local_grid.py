import pytest
pytestmark = pytest.mark.skip(reason="Skipping all tests in this file for now, because they need to be fully revised")

import numpy as np
from datetime import datetime, timedelta
from helpers.data_handling import convert_to_datetime, read_data_json
import pathlib
from SimulationModules.ElectricalGrid.PhotovoltaicArray import  PhotovoltaicArray
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingStation.EfficiencyMap import  ConstantEfficiencyMap
from SimulationModules.TimeDependent.TimeManager import TimeManager

from helpers.plot_filled_stack import plot_stacked
import matplotlib.pyplot as plt
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

time_manager = TimeManager(start_time=datetime(year=2024, month=3, day=11),
                            step_time=timedelta(seconds=300),
                            sim_duration=timedelta(days=7))

FILEPATH = pathlib.Path(ROOT_DIR) / "SimulationModules" / "ElectricalGrid" / "data" / "Timeseries_50.763_6.074_SA2_20kWp_crystSi_14_42deg_-3deg_2020_2020.json"

START_TIME= convert_to_datetime('20200601:0010')
END_TIME = convert_to_datetime('20200602:0000')
DATA= read_data_json(FILEPATH)

def test_read_pv_data():
    time, PV_Power= read_PV_data(DATA,START_TIME, END_TIME)


def test_pv_array():
    PV_Array= PhotovoltaicArray("PV1",
                                time_manager=time_manager)
    consumption=PV_Array.get_power_contribution(60*60*7)
    logger.info(f"Consumption {PV_Array.name} after {7} hours is {consumption}")

def test_max_pv_power():

    test_time = datetime(2020, 6, 1, 12, 0)

    pv_1=PhotovoltaicArray(name="PV1",
                           time_manager=time_manager)
    assert MAX_POWER_FROM_TABLE == 20
    assert pv_1.power_factor == 1.0
    cont_without_scale = pv_1.get_power_contribution(time=test_time)


    test_max_pv_power=PowerType(power_in_w=50, unit=PowerTypeUnit.KW)
    pv_2=PhotovoltaicArray(name="PV2",
                            max_pv_power=test_max_pv_power,
                            time_manager=time_manager)
    assert pv_2.power_factor==2.5
    assert pv_2.get_power_contribution(time=test_time)==cont_without_scale*pv_2.power_factor

def test_pv_power_prediction():

    local_grid=LocalGrid()
    time_manager.set_current_time(datetime(year=2020,month=5, day=1, hour=6, minute=0))
    time_manager.sim_duration=timedelta(days=1)
    time_manager.set_step_time(timedelta(hours=1))
    local_grid.connected_consumers.append(PhotovoltaicArray(name="pv_1",
                                                            time_manager=time_manager,  
                                                     max_pv_power=PowerType(power_in_w=20, unit=PowerTypeUnit.KW))
                                                     )
    preds=local_grid.get_pv_power_future(date_time=datetime(year=2020,month=5, day=5, hour=10, minute=0), horizon=5, step_time=timedelta(hours=1))
    assert preds == [15460.6, 17973.6, 17888.8, 16282.4, 13639.4]


def test_read_building_data():

    data = read_standard_load_data()
    #logger.info(data)

def test_building():
    building= Building("Supermarket", yearly_consumption=EnergyType(1000, EnergyTypeUnit.KWH),time_manager=time_manager)
    consumption=building.get_power_contribution(60*60*7)
    logger.info(f"Consumption from {building.name} after {7} hours is {consumption}")

def test_building_power_prediction():

    local_grid=LocalGrid()
    time_manager.set_current_time(datetime(year=2020,month=5, day=5, hour=6, minute=0))
    time_manager.sim_duration=timedelta(days=1)
    time_manager.set_step_time(timedelta(hours=1))

    local_grid.connected_consumers.append(Building(name="Supermarkt",
                                                   time_manager=time_manager,
                                                    yearly_consumption=EnergyType(1000, unit=EnergyTypeUnit.KWH),
)
                                                     )
    preds=local_grid.get_building_power_future(date_time=datetime(year=2020,month=5, day=5, hour=10), horizon=5, step_time=timedelta(hours=1))
    assert preds == [131.2, 136.7, 140.9, 137.9, 134.3]


def test_local_grid_add():
    building = Building("Supermarket",
                        time_manager=time_manager,)
    PV_Array = PhotovoltaicArray("PV1",
                                 time_manager=time_manager)
    cs=ChargingStation()
    local_grid= LocalGrid()

    local_grid.add_consumers(building)
    local_grid.add_consumers(PV_Array)
    local_grid.add_consumers(cs)

def test_local_grid_add():
    building = Building("Supermarket",
                        time_manager=time_manager,)
    pv_array = PhotovoltaicArray("PV1",
                                 time_manager=time_manager)
    local_grid= LocalGrid()

    local_grid.add_consumers(building)
    local_grid.add_consumers(pv_array)
    with pytest.raises(ValueError):
        local_grid.add_consumers(pv_array)

def test_all_power_values():

    building = Building(name="Supermarket",
                        time_manager=time_manager,)
    pv_array = PhotovoltaicArray("PV1",
                                 time_manager=time_manager)
    cs=ChargingStation()
    local_grid1 = LocalGrid()

    local_grid1.add_consumers(building)
    local_grid1.add_consumers(pv_array)
    local_grid1.add_consumers(cs)

    time = np.linspace(0,7*60*60, 10)
    for t in time:
        power_dict= local_grid1.get_all_power_values(t)
        logger.info('\n')
        logger.info(power_dict)


def test_local_grid_load():
    building = Building("Supermarket",
                        time_manager=time_manager,)
    pv_array = PhotovoltaicArray("PV1",
                                 time_manager=time_manager)
    local_grid= LocalGrid()
    local_grid.connected_consumers=[building, pv_array]

    time = np.linspace(0, 7*60*60, 10)
    for t in time:
        power= local_grid.calculate_connection_point_load(t)
        logger.info(f'Power after {t} seconds: {power}')

def test_print_consumption_data(interval = 2):
    building = Building("Supermarket",
                        time_manager=time_manager,)
    pv_array = PhotovoltaicArray("PV1",
                                 time_manager=time_manager)
    local_grid= LocalGrid()
    local_grid.connected_consumers=[building, pv_array]
    time = np.linspace(0, 24 * 60 * 60, 100)
    data_array=[]
    grid_power=[]
    for t in time:
        power_consumers = local_grid.get_all_power_values(t)
        power= local_grid.calculate_connection_point_load(t)
        appendarray = [power_consumers["Supermarket"].value, power_consumers["PV1"].value]
        data_array.append(appendarray)
        grid_power.append(power.value)

    data_array= np.array(data_array)
    data_array= np.transpose(data_array)
    labels = list(power_consumers.keys())
    labels = labels[1:]
    fig, ax = plt.subplots(nrows=1, ncols=1, facecolor="#F0F0F0")
    plot_stacked(time, data_array, labels=labels, ax= ax)
    plt.plot(time, grid_power, label = "Grid Power",linewidth=2, color='k')
    plt.show(block=False)


    if interval is not None:
        logger.info(f"Parking Area rendered for {interval} seconds",interval)
        plt.pause(interval)
        plt.close()

def test_consumption_values():
    #this test is made to check if the calculated values for the buildings power consumption
    #are correct. That for, we calculate some power values 
    #and check if they match what is in our table 
    #"SimulationEnvironment\ElectricalGrid\data\Repräsentative Profile VDEW.xls"

    building=Building("Supermarket", yearly_consumption=EnergyType(1000, EnergyTypeUnit.KWH),
                      time_manager=time_manager)
    #at first, a workday in winter
    date_time=datetime(year=2024, month=3, day=13, hour=10, minute=0)
    assert building.get_power_contribution(date_time).get_in_w().value == -145.8
    #a saturday in summer 
    date_time=datetime(year=2024, month=7, day=6, hour=14, minute=15)
    assert building.get_power_contribution(date_time).get_in_w().value == -123.0
    #a sunday in the transitiontime 
    date_time=datetime(year=2024, month=3, day=24, hour=18, minute=0)
    assert building.get_power_contribution(date_time).get_in_w().value == -99.2




def test_add_stationary_storage_to_local_grid():
    stationary_storages = StationaryBatteryStorage(energy_capacity=EnergyType(100, EnergyTypeUnit.KWH),
                                                   present_energy=EnergyType(50, EnergyTypeUnit.KWH),
                                                   efficiency_map=ConstantEfficiencyMap(efficiency=0.9))
    stationary_storages.set_actual_consumer_charging_power(PowerType(10, PowerTypeUnit.KW))
    
    localgrid = LocalGrid(connected_consumers=[stationary_storages])

    assert localgrid.calculate_connection_point_load(time=None) == stationary_storages.efficiency_map.get_input_power(PowerType(-10, PowerTypeUnit.KW)) 


def test_sign_convention_for_stationary_storage_with_building():
    set_power_value = PowerType(10, PowerTypeUnit.KW)
    stationary_storages = StationaryBatteryStorage(energy_capacity=EnergyType(100, EnergyTypeUnit.KWH),
                                                   present_energy=EnergyType(50, EnergyTypeUnit.KWH))
    stationary_storages.set_actual_consumer_charging_power(set_power_value)
    building=Building("Supermarket", yearly_consumption=EnergyType(1000, EnergyTypeUnit.KWH), time_manager=time_manager)
    date_time=datetime(year=2024, month=3, day=13, hour=10, minute=0)

    
    localgrid = LocalGrid(connected_consumers=[stationary_storages, building])

    assert localgrid.calculate_connection_point_load(time=date_time) <  PowerType(-10, PowerTypeUnit.KW)

 
    
def test_sign_convention_for_stationary_storage_with_PV():
    set_power_value = PowerType(10, PowerTypeUnit.KW)
    stationary_storages = StationaryBatteryStorage(energy_capacity=EnergyType(100, EnergyTypeUnit.KWH),
                                                   present_energy=EnergyType(50, EnergyTypeUnit.KWH))
    stationary_storages.set_actual_consumer_charging_power(set_power_value)
    time_manager.set_current_time(datetime(year=2020, month=6, day=1, hour=0, minute=0))
    time_manager.sim_duration=timedelta(weeks=4)
    PV_Array = PhotovoltaicArray("PV1",
                                    time_manager=time_manager)
    date_time=datetime(year=2020, month=6, day=13, hour=12, minute=10)

    localgrid = LocalGrid(connected_consumers=[stationary_storages, PV_Array])

    assert localgrid.calculate_connection_point_load(time=date_time) >  PowerType(-10, PowerTypeUnit.KW)
