import pathlib
from config.definitions import ROOT_DIR
from helpers.DataAnalyzer.DataAnalyzer import DataAnalyzer, EvSessionPeriod
import pytest
import numpy as np
from random import random
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from typing import List

def almost_equal(a, b, tol=1e-5):
    return abs(a-b) < tol

def test_init():
    DataAnalyzer(filename=pathlib.Path(ROOT_DIR)/"test"/"mock_json_trace.json")

@pytest.fixture
def mock_data_analyser():
    
    return DataAnalyzer(filename=pathlib.Path(ROOT_DIR)/"test"/"mock_json_trace.json")

@pytest.fixture
def mock_data():
    data =[]
    obs_length =20
    for i in range(obs_length):
        observation = {"current_time": i, "grid_power": random()*30, "price_table": [random()*100,random()*100, random()*100 ]} 
        data.append({"observations": observation})
    return data
    


@pytest.fixture
def mock_data_with_energy_request():
    data =[]
    #obs_length =20
    
    energy_request = [[[50 ,100*3600*1000]], [[50 ,100*3600*1000]], [[50 ,100*3600*1000]], [[50 ,100*3600*1000]], [[]]]
    for index, request in enumerate(energy_request):
        observation = {"current_time": index, "energy_requests": request} 
        data.append({"observations": observation})
    return data

@pytest.fixture
def mock_data_with_energy_request2():
    data =[]
    #obs_length =20
    
    energy_request = [[[50 ,100*3600*1000], [60 ,100*3600*1000]], [[50 ,100*3600*1000], [60 ,100*3600*1000]], [[50 ,100*3600*1000]], [[50 ,100*3600*1000]], [[70 ,100*3600*1000]]]
    for index, request in enumerate(energy_request):
        observation = {"current_time": index, "energy_requests": request} 
        data.append({"observations": observation})
    return data

@pytest.fixture
def mock_data_analyzer(mock_data, mock_data_analyser):
    data_analyser = mock_data_analyser
    data_analyser.data = mock_data
    data_analyser.calculate_time_data()
    return data_analyser

@pytest.fixture
def mock_ev_session_list():
    mock_ev_session_list = [EvSessionPeriod(id=1, start_index=0, end_index=1),
                            EvSessionPeriod(id=2, start_index=0, end_index=1),
                            EvSessionPeriod(id=3, start_index=1, end_index=2),
                            EvSessionPeriod(id=4, start_index=2, end_index=4),
                            EvSessionPeriod(id=5, start_index=4, end_index=8),
                            EvSessionPeriod(id=6, start_index=8, end_index=10),]

    mock_ev_session_list[0].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH)]
    mock_ev_session_list[1].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH)]
    mock_ev_session_list[2].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH)]
    mock_ev_session_list[3].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=80, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=70, unit=EnergyTypeUnit.KWH)]
    mock_ev_session_list[4].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=80, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=70, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=60, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=50, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=40, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=30, unit=EnergyTypeUnit.KWH)]
    mock_ev_session_list[5].energy_request = [EnergyType(energy_amount_in_j=100, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=90, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=80, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=70, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=60, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=50, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=40, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=30, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=20, unit=EnergyTypeUnit.KWH), EnergyType(energy_amount_in_j=10, unit=EnergyTypeUnit.KWH)]
    for session in mock_ev_session_list:
        #session.energy_request = [EnergyType(energy_amount_in_j=5-i, unit=EnergyTypeUnit.KWH) for i in range(session.end_index-session.start_index)]
        session.calculate_charged_energy()
    return mock_ev_session_list


def get_total_energy_charged(list_of_energy_request_lists):
    energy_requests = EnergyType(0, EnergyTypeUnit.KWH)
    for energy_request_list in list_of_energy_request_lists:
        energy_requests += (energy_request_list[0] - energy_request_list[-1])
    return energy_requests

def get_departure_energy_request(list_of_energy_request_lists):
    departure_energies = EnergyType(0, EnergyTypeUnit.KWH)
    for energy_request_list in list_of_energy_request_lists:
        departure_energies += energy_request_list[-1]
    return departure_energies

def test_correct_time_by_offset(mock_data_analyzer: DataAnalyzer):
    mock_data_analyzer.time_data = [0, 1, 2, 3, 4, 5, 1, 2 ,3 ,1,2,3,4]
    mock_data_analyzer.correct_time_by_offset()
    assert np.array_equal(mock_data_analyzer.time_data, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
    mock_data_analyzer.time_data= np.array([0, 1, 2, 3, 4, 5, 1, 2 ,3 ,1,2,3,4])
    mock_data_analyzer.correct_time_by_offset()
    assert np.array_equal(mock_data_analyzer.time_data, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))

def test_get_observation_by_name(mock_data_analyzer: DataAnalyzer):
    observation = mock_data_analyzer.get_observation_by_name("current_time")
    assert np.array_equal(observation, np.array([i for i in range(20)]))

def test_get_electricity_price(mock_data_analyzer: DataAnalyzer):
    assert np.array_equal(mock_data_analyzer.get_electricity_price(),
                          np.array([mock_data_analyzer.data[i]["observations"]["price_table"][0] for i in range(len(mock_data_analyzer.data))]))

def test_get_energy_cost(mock_data_analyzer: DataAnalyzer):

    energy_cost = mock_data_analyzer.get_energy_cost()
    delta_time = 1
    energy_cost_expected  = np.cumsum([mock_data_analyzer.data[i]["observations"]["grid_power"] * 
                                       mock_data_analyzer.data[i]["observations"]["price_table"][0]*
                                       delta_time* (1/1000)*(1/1000)*(1/3600)
                                       for i in range(len(mock_data_analyzer.data))])
    for i in range(len(energy_cost)):
        assert almost_equal(a=energy_cost[i], b=energy_cost_expected[i])



def test_get_ev_depatrue_energy(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    departure_energies = mock_data_analyzer.get_ev_depatrue_energy()
    for departure_energy in departure_energies:
        departure_energy_in_kWh: EnergyType = departure_energy/1000/3600
        assert departure_energy_in_kWh > 0
        assert departure_energy_in_kWh.get_in_kwh().value < 100

def test_get_cs_power(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    cs_power = mock_data_analyzer.get_cs_power()
    assert cs_power[0] == 0


def test_get_departure_energy_over_time(mock_ev_session_list, mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    mock_data_analyzer.ev_session_periods = mock_ev_session_list
    departure_energies = mock_data_analyzer.get_ev_depature_energy_over_time_in_kWh()
    
    assert len(departure_energies) == len(mock_data_analyzer.data)




def test_get_departure_energy_over_time_value_right(mock_ev_session_list, mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    mock_data_analyzer.ev_session_periods = mock_ev_session_list
    departure_energies = mock_data_analyzer.get_ev_depature_energy_over_time_in_kWh()
    assert len(departure_energies) == len(mock_data_analyzer.data)
    assert departure_energies[-1] == get_departure_energy_request([session.energy_request for session in mock_ev_session_list])


def test_get_gini_energy(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    gini_energies = mock_data_analyzer.get_gini_energy()
    for gini_data in gini_energies:
        for gini_energy in gini_data:
            assert gini_energy > 0
            assert gini_energy < 100
    assert len(gini_energies) > 0

def test_get_ev_count(mock_ev_session_list, mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    mock_data_analyzer.ev_session_periods = mock_ev_session_list
    ev_count = mock_data_analyzer.get_total_amount_of_ev()

    assert ev_count > 0


def test_get_ev_session(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    
    mock_data_analyzer.get_ev_session()
    assert len(mock_data_analyzer.ev_session_periods) > 10
    assert len(mock_data_analyzer.ev_session_periods) < 50
    for session in mock_data_analyzer.ev_session_periods:
        assert session.charged_energy is not None 

def test_get_total_charged_energy(mock_ev_session_list, mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    mock_data_analyzer.ev_session_periods = mock_ev_session_list
    total_charged_energy: List[EnergyType] = mock_data_analyzer.get_charged_energy_over_time()
    expectec_total_charged_energy = get_total_energy_charged([session.energy_request for session in mock_ev_session_list])
    assert total_charged_energy[-1].get_in_kwh() > expectec_total_charged_energy + EnergyType(energy_amount_in_j=-1, unit=EnergyTypeUnit.KWH)
    assert total_charged_energy[-1].get_in_kwh() < expectec_total_charged_energy + EnergyType(energy_amount_in_j=1, unit=EnergyTypeUnit.KWH)

def test_continous_charged_energy_is_equal_stepwise(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    stepwise_charged_energy: List[EnergyType]  = mock_data_analyzer.get_charged_energy_over_time()
    continuous_charged_energy: List[EnergyType] = mock_data_analyzer.get_charged_energy_over_time_continuous()
    assert len(stepwise_charged_energy) == len(continuous_charged_energy)
    assert stepwise_charged_energy[-1] == continuous_charged_energy[-1]
   

def test_get_total_charged_energy_continous(mock_data_analyser):
    mock_data_analyzer: DataAnalyzer = mock_data_analyser
    total_charged_energy: List[EnergyType] = mock_data_analyzer.get_charged_energy_over_time_continuous()
    total_charged_energy_stepwise: List[EnergyType] = mock_data_analyzer.get_charged_energy_over_time()
    assert almost_equal(total_charged_energy[-1].get_in_kwh().value, total_charged_energy_stepwise[-1].get_in_kwh().value, tol=1e-5)
    #assert total_charged_energy[-1].get_in_kwh() < EnergyType(energy_amount_in_j=136, unit=EnergyTypeUnit.KWH)














