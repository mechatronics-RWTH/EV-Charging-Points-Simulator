from Controller_Agent.Rule_based.RuleBasedAgent import RuleBasedAgent_One, AgentRequestAnswer, TypeOfField
from SimulationModules.RequestHandling.Request import Request_state
from SimulationModules.Gini.Gini import GiniModes
import pytest
import random
import numpy as np
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

def test_rule_based_agent_init():
    rb_agent = RuleBasedAgent_One()
    assert isinstance(rb_agent, RuleBasedAgent_One)

@pytest.fixture
def rule_based_agent():
    return RuleBasedAgent_One()

@pytest.fixture
def area_size():
    return 10

@pytest.fixture
def amount_ginis():
    return 5

@pytest.fixture
def raw_obs(area_size, amount_ginis):    

    field_kinds=[]
    user_requests=[]
    field_indices_ginis=[]
    gini_states=[]
    soc_ginis=[]
    gini_energy=[]
    gini_requested_energy=[]
    gini_charging_power=[]
    charging_states=[]
    cs_charging_power=[]
    cs_charging_limits=[]
    current_time=[]
    for _ in range(area_size):
        field_kinds.append(random.choice([0,1,2,3,4]))
        user_requests.append(random.choice([0,1,2,3,4,5]))
        charging_states.append(random.choice([None, 50]))
        cs_charging_power.append(random.randint(0,100))
        cs_charging_limits.append(random.randint(0,100))
        current_time.append(random.randint(0,100))

    for _ in range(amount_ginis):
        field_indices_ginis.append(random.randint(0, area_size-1))
        gini_states.append(random.choice([0,1,2,3,4,5]))
        soc_ginis.append(random.randint(0,100))
        gini_energy.append(random.randint(0,100))
        gini_requested_energy.append(random.randint(0,100))
        gini_charging_power.append(random.randint(0,100))

    
    observation_raw={
            "grid_power": 1000,
            "building_power": 500,
            "pred_building_power": [500, 1000, 1500],
            "peak_grid_power": 1500,
            "price_table": [500, 1000, 1500],
            "pv_power": 10000,
            "pred_pv_power": [500, 1000, 1500],
            "distances": [5,10,20],
            "field_kinds": field_kinds,

            "soc_stat_battery": [0],
            "stat_battery_chrg_pwr_max": [0],
            "stat_battery_dischrg_pwr_max": [0],
            "stat_batt_power": 0,

            "user_requests": user_requests,
            "estimated_parking_time": [],
            "energy_requests": [],
            "ev_energy": [],

            "field_indices_ginis": field_indices_ginis,
            "gini_states": gini_states,
            "soc_ginis": soc_ginis,
            "gini_energy": gini_energy,
            "gini_requested_energy": gini_requested_energy,               
            "gini_charging_power": gini_charging_power,

            "charging_states": charging_states,                      
            "cs_charging_power": cs_charging_power,
            "cs_charging_limits": cs_charging_limits,
            "current_time": current_time,
        } 
    return observation_raw

@pytest.fixture
def action_raw_base(area_size, amount_ginis):
    action_raw_base={
        "requested_gini_field": np.full(amount_ginis,None),
        "requested_gini_power": np.full(amount_ginis,None),
        "target_charging_power" : np.full(area_size,None),
        "request_answer": np.full(area_size,None),
        "target_stat_battery_charging_power": None
    }
    return action_raw_base



def test_initialize_action(rule_based_agent: RuleBasedAgent_One,
                           action_raw_base):
    rule_based_agent.initialize_action(action_raw_base)

    assert rule_based_agent.action == action_raw_base

def test_initialize_observation_once(rule_based_agent: RuleBasedAgent_One, raw_obs):
    rule_based_agent.initialize_observation_once(raw_obs)
    assert rule_based_agent.type_of_field == raw_obs["field_kinds"]
    assert rule_based_agent.charging_spot_list == [j for j,field_kind in enumerate(raw_obs["field_kinds"]) if field_kind==2]

def test_initialize_observation(rule_based_agent: RuleBasedAgent_One, raw_obs):
    rule_based_agent.initialize_observation(raw_obs)
    assert rule_based_agent.user_request == raw_obs["user_requests"]
    assert rule_based_agent.gini_field_indices == raw_obs["field_indices_ginis"]
    assert rule_based_agent.gini_soc == raw_obs["soc_ginis"]
    assert rule_based_agent.charging_soc_state == raw_obs["charging_states"]
    assert rule_based_agent.gini_states == raw_obs["gini_states"]

@pytest.fixture
def initialized_agent(rule_based_agent: RuleBasedAgent_One, raw_obs, action_raw_base):
    rule_based_agent.initialize_action(action_raw_base)
    rule_based_agent.initialize_observation(raw_obs)
    return rule_based_agent

def test_rule_based_agent_confirm_all_unanswered_requests(initialized_agent: RuleBasedAgent_One, area_size):
    initialized_agent.user_request= [Request_state.REQUESTED.value]*area_size
    request_status = random.choices([AgentRequestAnswer.NO_ANSWER,AgentRequestAnswer.CONFIRM, AgentRequestAnswer.DENY], k=area_size)
    initialized_agent.action["request_answer"] = request_status
    initialized_agent._confirm_all_unanswered_requests()
    for index,request_state in enumerate(request_status):
        if request_state == AgentRequestAnswer.NO_ANSWER:
            assert initialized_agent.action["request_answer"][index] == AgentRequestAnswer.CONFIRM.value
        else:
            assert initialized_agent.action["request_answer"][index] == request_state


def test_rule_based_agent_is_agent_recharge_required(initialized_agent: RuleBasedAgent_One):
    initialized_agent.type_of_field = [TypeOfField.GiniChargingSpot, TypeOfField.GiniChargingSpot, TypeOfField.Obstacle]
    initialized_agent.gini_soc = [0.5, 0.08]
     
    initialized_agent.current_loop_index = 1 # SOC low 
    initialized_agent.current_pos = 2 #not at charging spot
    assert initialized_agent._is_agent_recharge_required()
    initialized_agent.current_loop_index = 0
    initialized_agent.current_pos = 0
    assert not initialized_agent._is_agent_recharge_required()

def test_no_vehicle_at_spot(initialized_agent: RuleBasedAgent_One):
    initialized_agent.charging_soc_state = [None, 100, None]
    assert not initialized_agent.is_vehicle_at_charging_spot(0)
    assert initialized_agent.is_vehicle_at_charging_spot(1)
    assert not initialized_agent.is_vehicle_at_charging_spot(2)


def test_rule_based_agent_is_not_occupied(initialized_agent: RuleBasedAgent_One):
    initialized_agent.charging_soc_state = [None, 100, None]
    initialized_agent.gini_field_indices = [0, 5, 7]
    assert initialized_agent.is_spot_occupied(0) # occupied by gini
    assert initialized_agent.is_spot_occupied(1) # occupied by vehicle
    assert not initialized_agent.is_spot_occupied(2) # not occupied

def test_rule_based_agent_is_confirmed_request_and_gini_idles(initialized_agent: RuleBasedAgent_One,
                                                              ):
    initialized_agent.user_request= [Request_state.REQUESTED.value, Request_state.CONFIRMED.value]
    initialized_agent.gini_states= [GiniModes.IDLE.value, GiniModes.IDLE.value, GiniModes.CHARGING.value]
    initialized_agent.current_loop_index = 0
    assert initialized_agent._is_confirmed_request_and_gini_idles()
    initialized_agent.user_request= [Request_state.REQUESTED.value, Request_state.DENIED.value]
    assert not initialized_agent._is_confirmed_request_and_gini_idles()
    initialized_agent.user_request= [Request_state.REQUESTED.value, Request_state.CONFIRMED.value]
    initialized_agent.gini_states= [GiniModes.CHARGING.value, GiniModes.CHARGING_EV.value, GiniModes.CHARGING.value]
    assert not initialized_agent._is_confirmed_request_and_gini_idles()


def test_rule_based_agent_ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(initialized_agent: RuleBasedAgent_One):
    initialized_agent.gini_field_indices= [1,4, 7]
    initialized_agent.action["requested_gini_field"] = [2 , 6]
    assert not initialized_agent._ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(0)
    assert initialized_agent._ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(1)
    assert initialized_agent._ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(2)
    assert not initialized_agent._ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(3)



def test_rule_based_agent_get_type_of_field(initialized_agent:  RuleBasedAgent_One):
    initialized_agent.action["requested_gini_field"]= [1,2,3] 
    
    initialized_agent.gini_field_indices = [10,0,3]
    initialized_agent.current_loop_index = 2
    assert initialized_agent._requested_is_current_field()
    initialized_agent.current_loop_index = 1
    assert not initialized_agent._requested_is_current_field()
    initialized_agent.current_loop_index = 0
    assert not initialized_agent._requested_is_current_field()



@pytest.mark.parametrize("building_power, pv_power, grid_max, expected_charging_power", [
                         ([10000],
                          [20000],
                          100,
                          110000,
                          ),
                         
                         ([30000],
                          [20000],
                          100,
                          90000,
                          ),
                         ([200000],
                          [0],
                          100,
                          0,
                          ),
                          ])
def test_determine_residual_power(initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  building_power,
                                  pv_power,
                                  grid_max,
                                  expected_charging_power):
    initialized_agent.P_grid_max = PowerType(grid_max, PowerTypeUnit.KW)
    raw_obs["building_power"] = building_power
    raw_obs["pv_power"] = pv_power
    P_res = initialized_agent.determine_residual_power(raw_obs)
    assert isinstance(P_res, PowerType)
    assert P_res.get_in_w().value == expected_charging_power


@pytest.mark.parametrize("building_power, pv_power, grid_max, battery_power, expected_charging_power", [
                         ([10000],
                          [20000],
                          100,
                          [-10000],
                          120000,
                          ),
                         
                         ([30000],
                          [20000],
                          100,
                          [-10000],
                          100000,
                          ),
                         ([200000],
                          [0],
                          100,
                          [-10000],
                          0,
                          ),
                          ])
def test_determine_residual_power_with_battery_power_discharging(
                                initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  building_power,
                                  pv_power,
                                  grid_max,
                                  expected_charging_power,
                                  battery_power):
    initialized_agent.action["target_stat_battery_charging_power"] = np.array(battery_power, dtype=np.float32)
    initialized_agent.P_grid_max = PowerType(grid_max, PowerTypeUnit.KW)
    raw_obs["building_power"] = building_power
    raw_obs["pv_power"] = pv_power
    P_res = initialized_agent.determine_residual_power(raw_obs)
    assert isinstance(P_res, PowerType)
    assert P_res.get_in_w().value == expected_charging_power

@pytest.mark.parametrize("building_power, pv_power, grid_max, battery_power, expected_charging_power", [
                         ([10000],
                          [20000],
                          100,
                          [10000],
                          100000,
                          ),
                         
                         ([30000],
                          [20000],
                          100,
                          [10000],
                          80000,
                          ),
                         ([200000],
                          [0],
                          100,
                          [10000],
                          0,
                          ),
                          ])
def test_determine_residual_power_with_battery_power_charging(
                                initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  building_power,
                                  pv_power,
                                  grid_max,
                                  expected_charging_power,
                                  battery_power):
    initialized_agent.action["target_stat_battery_charging_power"] = np.array(battery_power, dtype=np.float32)
    initialized_agent.P_grid_max = PowerType(grid_max, PowerTypeUnit.KW)
    raw_obs["building_power"] = building_power
    raw_obs["pv_power"] = pv_power
    P_res = initialized_agent.determine_residual_power(raw_obs)
    assert isinstance(P_res, PowerType)
    assert P_res.get_in_w().value == expected_charging_power


def test_set_cs_target_power(initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  action_raw_base:dict):
    P_res = PowerType(100, PowerTypeUnit.KW)
    cs_indices = [i for i, x in enumerate(raw_obs["charging_states"]) if x is not None]
    num_cs_charging = len(cs_indices)

    initialized_agent.occupied_charging_spot_index = cs_indices
    initialized_agent.initialize_action(action_raw_base)
    initialized_agent.set_cs_target_power(P_res)
    for index in cs_indices:
        assert initialized_agent.action["target_charging_power"][index] == P_res.get_in_w().value/num_cs_charging


    

def test_limit_charging_power_if_required(initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  action_raw_base:dict):
    initialized_agent.P_grid_max = PowerType(100, PowerTypeUnit.KW)
    raw_obs["building_power"] = [40000]
    raw_obs["pv_power"] = [10000]
    cs_indices = [i for i, x in enumerate(raw_obs["charging_states"]) if x is not None]
    num_cs_charging = len(cs_indices)

    initialized_agent.occupied_charging_spot_index = cs_indices
    initialized_agent.charging_spot_list = cs_indices
    initialized_agent.initialize_action(action_raw_base)
    
    initialized_agent.limit_charging_power_if_required(raw_obs)
    for index in cs_indices:
        assert initialized_agent.action["target_charging_power"][index] == 70000/num_cs_charging


def test_leave_charging_station_if_charged(initialized_agent: RuleBasedAgent_One,
                                  raw_obs: dict,
                                  action_raw_base:dict):
    raw_obs["field_kinds"][1]=TypeOfField.ParkingPath.value
    raw_obs["field_kinds"][2]=TypeOfField.ParkingPath.value
    raw_obs["field_kinds"][3]=TypeOfField.ParkingPath.value
    raw_obs["field_kinds"][4]=TypeOfField.ParkingPath.value
    raw_obs["field_kinds"][5]=TypeOfField.ParkingPath.value
    initialized_agent.initialize_observation_once(raw_obs)
    initialized_agent.field_to_go_to = None    
    index =3

    initialized_agent.current_loop_index =index
    initialized_agent.gini_states[index]= GiniModes.CHARGING.value
    initialized_agent.gini_soc[index]= index
    initialized_agent.gini_field_indices[index]= 0.95
    initialized_agent.action["requested_gini_field"][index]= index
    initialized_agent.leave_the_charging_station_if_charged()
    assert initialized_agent.field_to_go_to is not None 

def test_go_to_ev_if_required():
    user_request = np.array([Request_state.REQUESTED.value, Request_state.REQUESTED.value, Request_state.DENIED.value, Request_state.CONFIRMED.value, ])
    conf_req_index=next((j for j, req in enumerate(user_request) if req == Request_state.CONFIRMED.value), None)
    assert conf_req_index == 3




