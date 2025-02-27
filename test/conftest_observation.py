
import pytest
import random
import numpy as np
from SimulationModules.Enums import Request_state, TypeOfField, AgentRequestAnswer

# #@pytest.fixture
# def area_size():
#     return 10

# #@pytest.fixture
# def amount_ginis():
#     return 5

area_size = 10
amount_ginis = 5

#@pytest.fixture
def raw_obs(area_size=area_size, amount_ginis=amount_ginis):    

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
    current_time=random.randint(0,100)
    for _ in range(area_size):
        field_kinds.append(random.choice([0,1,2,3,4]))
        user_requests.append(random.choice([0,1,2,3,4,5]))
        charging_states.append(random.choice([None, 50]))
        cs_charging_power.append(random.randint(0,100))
        cs_charging_limits.append(random.randint(0,100))
        #current_time.append(random.randint(0,100))

    for index, val in enumerate(field_kinds):
        if val != TypeOfField.ParkingSpot.value:
            user_requests[index] = Request_state.NO_REQUEST.value

    for _ in range(amount_ginis):
        field_indices_ginis.append(random.randint(0, area_size-1))
        gini_states.append(random.choice([0,1,2,3,4,5]))
        soc_ginis.append(random.randint(0,100))
        gini_energy.append(random.randint(0,100))
        gini_requested_energy.append(random.randint(0,100))
        gini_charging_power.append(random.randint(0,100))

    energy_requests=[]
    for request in user_requests:
        if request in [Request_state.REQUESTED,Request_state.CONFIRMED, Request_state.CHARGING]:
            energy_requests.append(random.randint(0,100))
        else:
            energy_requests.append(None)



    
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
            "energy_requests": energy_requests,
            "ev_energy": energy_requests,

            "field_indices_ginis": field_indices_ginis,
            "gini_states": gini_states,
            "soc_ginis": soc_ginis,
            "gini_energy": gini_energy,
            "gini_requested_energy": gini_requested_energy,               
            "gini_charging_power": gini_charging_power,

            "charging_states": charging_states,                      
            "cs_charging_power": cs_charging_power,
            "cs_charging_limits": cs_charging_limits,
            "current_time": [current_time],
        } 
    return observation_raw




def action_raw_base(area_size=area_size, amount_ginis=amount_ginis):    

    action_raw_base={
        "requested_gini_field": np.full(amount_ginis,None),
        "requested_gini_power": np.full(amount_ginis,None),
        "target_charging_power" : np.full(area_size,None),
        "request_answer": np.full(area_size,None),
        "target_stat_battery_charging_power": [0]
    }
    return action_raw_base
