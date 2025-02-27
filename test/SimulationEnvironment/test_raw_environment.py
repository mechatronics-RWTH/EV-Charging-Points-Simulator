import copy
import pytest

from SimulationEnvironment.GymEnvironment import CustomEnv
from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationEnvironment.Settings.SimSettings import SimSettings

from SimulationModules.ElectricityCost.ElectricyPrice import PriceTable
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricVehicle.EV import InterfaceEV, EV
from SimulationEnvironment.RawEnvSpaces import RawEnvSpaceManager
from SimulationModules.Enums import  Request_state
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.ParkingArea.ParkingAreaElements import Field
from typing import List

from unittest.mock import Mock
import random

from datetime import timedelta, datetime
import numpy as np
import platform
from gymnasium.spaces import Dict, Box, MultiBinary
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

def create_mock_ev():
    mock_ev = Mock(spec=InterfaceEV)
    mock_ev.park_vehicle_at_spot = Mock(return_value=None)
    mock_ev.charging_request = Request()
    mock_ev.charging_request.state = Request_state.REQUESTED
    return mock_ev

def park_evs_at_parking_area(parking_area):
        #raw_env.reset()
    ev1 = create_mock_ev()
    ev1_field = 0
    ev1.charging_request.field_index = ev1_field
    ev2 = create_mock_ev()
    ev2_field = 19
    ev2.charging_request.field_index = ev2_field
    parking_area.park_new_ev_at_field(ev=ev1, field_index=ev1_field)
    parking_area.park_new_ev_at_field(ev=ev2, field_index=ev2_field)

@pytest.fixture(scope="function")
def raw_env():
    start_time = time.time()  # Start the timer
    gym_config = EnvConfig.load_env_config(config_file="test/env_config_test.json")
    custom_env= CustomEnv(config=gym_config)
    custom_env.time_manager.reset_time()
    end_time = time.time()  # Stop the timer
    elapsed_time = end_time - start_time
    print(f"Elapsed time for raw_env: {elapsed_time} seconds")
    return custom_env

import time

def test_request_handler_is_same(raw_env: CustomEnv):
    assert raw_env.charging_session_manager.request_handler.request_collector == raw_env.parking_area.request_collector


def test_request_handler_is_same_after_reset(raw_env: CustomEnv):
    raw_env.reset()
    assert raw_env.charging_session_manager.request_handler.request_collector == raw_env.parking_area.request_collector


def test_read_new_request(raw_env: CustomEnv):
    start_time = time.time()  # Start the timer

    #raw_env.reset()
    ev1 = create_mock_ev()
    ev1_field = 0
    ev1.charging_request.field_index = ev1_field
    ev2 = create_mock_ev()
    ev2_field = 19
    ev2.charging_request.field_index = ev2_field
    raw_env.parking_area.park_new_ev_at_field(ev=ev1, field_index=ev1_field)
    raw_env.parking_area.park_new_ev_at_field(ev=ev2, field_index=ev2_field)
    
    request_0 = raw_env.parking_area.request_collector.active_requests[0]
    request_19 = raw_env.parking_area.request_collector.active_requests[1]

    # The simulation should have made a request for the new random ev at spot 0
    assert request_0 is not None
    assert request_19 is not None
    assert request_0.state == Request_state.REQUESTED
    assert request_19.state == Request_state.REQUESTED

def test_read_new_request_commands(raw_env: CustomEnv):
    raw_env.reset()

    park_evs_at_parking_area(parking_area=raw_env.parking_area)

    request_0 = raw_env.parking_area.request_collector.active_requests[0]
    request_19 = raw_env.parking_area.request_collector.active_requests[1]
    request_0 = raw_env.parking_area.request_collector.active_requests[0]
    request_19 = raw_env.parking_area.request_collector.active_requests[1]

    # The answer should deny 19 and confirm 1
    answers = np.array([0 for i in range(len(raw_env.parking_area.parking_area_fields))])
    answers[0] = 1
    answers[19] = 2

    raw_env.charging_session_manager.set_request_commands(answers)
    #print(f"answers: {raw_env.charging_session_manager.request_handler.request_answers}")
    raw_env.charging_session_manager.request_handler.handle_requests()
    print(raw_env.parking_area.request_collector.active_requests)
    assert request_0.state == Request_state.CONFIRMED
    assert request_19.state == Request_state.DENIED



def test_read_new_gini_targets(raw_env):
    
    raw_env.reset()
    #we want to spread the ginis evenly over the fields
    requested_gini_fields=np.linspace(0, len(raw_env.parking_area.parking_area_fields), len(raw_env.gini_mover.ginis), endpoint=False, dtype=int)
    raw_env.gini_mover.set_gini_targets(requested_gini_fields)
    for i, gini in enumerate(raw_env.gini_mover.ginis):
        assert gini.target_field.index == requested_gini_fields[i]

def test_read_new_cs_max_limits(raw_env: CustomEnv):

    raw_env.reset()
    raw_env.parking_area.initialize_parking_area()
    requested_cs_max_limits=np.full(len(raw_env.parking_area.parking_area_fields), None)
    fields_with_chargers_index = [field.index for field in raw_env.parking_area.fields_with_chargers]
    #we just set the limit of the first charger to 5 kW
    field_index = fields_with_chargers_index[0]
    requested_cs_max_limits[field_index]=5000
    raw_env.parking_area.set_new_cs_max_limits(requested_cs_max_limits)
    fields: List[Field]=raw_env.parking_area.parking_area_fields 
    limit =    fields[field_index].get_charger().get_maximum_cs_charging_power()
    set_point = fields[field_index].get_charger().efficiency_map.get_output_power(PowerType(5, PowerTypeUnit.KW))
    assert limit== set_point

def test_read_new_gini_max_limits(raw_env:CustomEnv):

    raw_env.reset()
    requested_gini_max_limits=np.full(len(raw_env.gini_mover.ginis), None)
    requested_gini_max_limits[1]=5
    raw_env.gini_mover.set_new_gini_max_limits(requested_gini_max_limits)
    for i, gini in enumerate(raw_env.gini_mover.ginis):
        if i !=1:
            assert gini.get_maximum_cs_charging_power() > PowerType(5, PowerTypeUnit.W)

    assert raw_env.gini_mover.ginis[1].get_target_power() == PowerType(5, PowerTypeUnit.W)

def test_reset_env(raw_env: CustomEnv):
    raw_env.reset_raw()
    assert raw_env.parking_area.request_collector.active_requests == []
    assert raw_env.parking_area.departed_ev_list == []


@pytest.mark.skip(reason="This test is not working yet")
def test_reward_func(raw_env):
    # Create an instance of the GymEnvironment class
    env = raw_env

    env.raw_env_space_manager.weights_for_reward["weight_not_satisfied"]=10
    env.raw_env_space_manager.weights_for_reward["weight_rejection"]=50
    env.raw_env_space_manager.weights_for_reward["weight_energy_consumption"]=1

    ev=EV(arrival_time=datetime.now(),
                 stay_duration=timedelta(seconds=300),
                 energy_demand=EnergyType(energy_amount_in_j=10, 
                                          unit=EnergyTypeUnit.KWH)
                 )
    env.parking_area.departed_ev_list=[ev, ev]
    env.local_grid.energy_costs_step=2000
    env.charging_session_manager.denied_requests_amount_step=3
    
    assert -env.calculate_reward_raw() ==10*2*10 + 50*3 + 1*2000

def test_space_validator(raw_env):
    """
    the space validator checks, if actions(input) or observations
    (output) have the right form which is defined in the space init
    """
    #we take on 1 dimensional space and one zero dimensional space and a 2 dimensional space
    property_1_space=Box(low=0, high=100, dtype=np.int32)
    property_2_space=Box(low=np.zeros(10),high=np.full(10,100), dtype=np.float32)                                            
    property_3_space=Box(low=np.zeros([5,5]), high=np.full([5,5],100))
            
    test_space = Dict({
        "property_1": property_1_space,
        "property_2": property_2_space,
        "property_3": property_3_space
    })

    
    property_1_instance=np.array([2])
    property_2_instance=np.full(10,3)
    property_3_instance=np.full([5,5],3)

    test_instance ={
            "property_1": property_1_instance,
            "property_2": property_2_instance,
            "property_3": property_3_instance
    }

    #this first test should be successfull

    raw_env.raw_env_space_manager.validate_to_fit_space(test_space, test_instance)
    
    #for the next round, we validator should give a value error for the dimensions--------------------------------------
    property_1_space=Box(low=0, high=100, dtype=np.int32)
    property_2_space=Box(low=np.full(10, 0),high=np.full(10,100), dtype=np.float32)                                            
    property_3_space=Box(low=np.zeros([5,5]), high=np.full([5,5],100))
            
    test_space = Dict({
        "property_1": property_1_space,
        "property_2": property_2_space,
        "property_3": property_3_space
    })

    
    property_1_instance=np.array([2])
    property_2_instance=np.full(10,3)
    property_3_instance=np.full([5,3],3)

    test_instance ={
            "property_1": property_1_instance,
            "property_2": property_2_instance,
            "property_3": property_3_instance
    }

    #this first test should throw a value error for property_3's dimensions
    with pytest.raises(ValueError):
        raw_env.raw_env_space_manager.validate_to_fit_space(test_space, test_instance)

    
    #for the next round, we validator should give a value error for the break of a max--------------------------------------
    property_1_space=Box(low=0, high=100, dtype=np.int32)
    property_2_space=Box(low=np.full(10, 0),high=np.full(10,100), dtype=np.float32)                                            
    property_3_space=Box(low=np.zeros([5,5]), high=np.full([5,5],100))
            
    test_space = Dict({
        "property_1": property_1_space,
        "property_2": property_2_space,
        "property_3": property_3_space
    })

    
    property_1_instance=np.array([2])
    property_2_instance=np.full(10,3)
    property_3_instance=np.full([5,3],101)

    test_instance ={
            "property_1": property_1_instance,
            "property_2": property_2_instance,
            "property_3": property_3_instance
    }

    #this first test should throw a value error for property_3's too high values
    with pytest.raises(ValueError):
        raw_env.raw_env_space_manager.validate_to_fit_space(test_space, test_instance)


def test_type_pred_pv(raw_env: CustomEnv):
    observation = raw_env.raw_env_space_manager.write_observations()
    pred_power = observation["pred_pv_power"]
    assert all(isinstance(x, float) for x in pred_power)

def test_type_pred_building(raw_env: CustomEnv):
    observation = raw_env.raw_env_space_manager.write_observations()
    pred_power = observation["pred_building_power"]
    assert all(isinstance(x, float) for x in pred_power)