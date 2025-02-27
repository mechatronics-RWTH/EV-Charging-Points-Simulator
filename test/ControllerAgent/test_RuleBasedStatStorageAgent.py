from Controller_Agent.Rule_based.Stationary_Battery_Controller.AdaptiveStationaryBatteryController import AdaptiveStationaryBatteryController
from Controller_Agent.Rule_based.RuleBasedNoGiniStatStorage import RuleBasedAgentStatStorage
import numpy as np
import pytest
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

def test_initialize_stationary_battery_controller():
    """
    this test checks if the stationary battery controller is initialized correctly
    """

    agent = RuleBasedAgentStatStorage()
    agent._initialize_stationary_battery_controller()
    assert isinstance(agent.stationary_battery_controller, AdaptiveStationaryBatteryController)

def test_calculate_action_stationary_battery_controller():
    """
    this test checks if the action is calculated correctly
    """

    agent = RuleBasedAgentStatStorage(soc_a_limit=0.8, soc_x_limit=0.95,soc_y_limit=0.3)
    action_raw_base={
            "requested_gini_field": np.full(0,None),
            "requested_gini_power": np.full(0,None),
            "target_charging_power" : np.full(0,None),
            "request_answer": np.full(0,None),
            "target_stat_battery_charging_power" : None
        }
    agent.initialize_action(action_raw_base)
    agent._initialize_stationary_battery_controller()
    raw_obs = {
        "pv_power": [10000],
        "building_power": [20000],
        "cs_charging_power": [None, 10000, 20000, None],
        "stat_battery_chrg_pwr_max": [50000],
        "stat_battery_dischrg_pwr_max": [600000],
        "peak_grid_power": [700000],
        "soc_stat_battery": [0.9],
        "energy_requests": [10],
        "user_requests": [None, 4, 4, None],
        "cs_charging_limits": [None, 20000, 30000, None]
    }
    agent.calculate_action_stationary_battery_controller(raw_obs)
    assert agent.action["target_stat_battery_charging_power"][0] == -40000


@pytest.mark.parametrize("raw_obs, expected_cs_power, ", [
                         ({
                            "energy_requests": [None, None, None, None, None, None],
                            "cs_charging_power": [None, None, None, None,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, None, None, None,  None, None],

                    },
                          PowerType(0),
                          ),
                         
                                                 ({
                            "energy_requests": [None, 3, None, None, None, None],
                            "cs_charging_power": [None, 100, None, None,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, 4, None, None,  None, None],

                    },
                          PowerType(100, PowerTypeUnit.W),
                          ),
                                                 ({
                            "energy_requests": [None, None, None, None, None, None],
                            "cs_charging_power": [None, None, 200, None,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, None, None, None,  None, None],

                    },
                          PowerType(0),
                          ),
                           ({
                            "energy_requests": [None, None, 5, None, None, None],
                            "cs_charging_power": [None, None, 400, None,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, None, 4, None,  None, None],

                    },
                          PowerType(400, PowerTypeUnit.W),
                          ),
                           ({
                            "energy_requests": [None, 100000, 200000, None, None, None],
                            "cs_charging_power": [None, 300, 400, 800,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, 4, 4, 5,  None, None],

                    },
                          PowerType(700, PowerTypeUnit.W),
                          ),
                          ({
                            "energy_requests": [None, 10000, 150000, 10000, 240000, None],
                            "cs_charging_power": [None, None, 400, None,  None, None],
                            "cs_charging_limits": [None, 100, 100, 100,  None, None],
                            "user_requests" : [None, 4, 4, 4,  None, None],

                    },
                          PowerType(600, PowerTypeUnit.W),
                          ),
                          ])
def test_determine_charging_station_power(raw_obs,
                                          expected_cs_power,
                                          ):
    agent = RuleBasedAgentStatStorage(soc_a_limit=0.8, soc_x_limit=0.95,soc_y_limit=0.3)
    sum_cs_power = agent.determine_charging_station_power(raw_obs=raw_obs)
    assert sum_cs_power == expected_cs_power


@pytest.mark.parametrize("raw_obs, expected_cs_power ", 
                            [
                                (
                                    { 
                                    "building_power": [-14436.666666666666],
                                    "current_time": [39000],
                                    "pv_power": [14987.733333333334],
                                    "soc_stat_battery": [0.8139190541313491],
                                    "stat_battery_chrg_pwr_max": [42836.99568776329],
                                    "stat_battery_dischrg_pwr_max": [-79360.04708571943],
                                    "stat_batt_power": [-10453.2001953125],
                                    "grid_power": [11004.266861979168],
                                    "peak_grid_power": [30000.000390625002],
                                    "el_price": [173.81],
                                    "ev_energy": [None, 181011495.99727282, None, None, None, None],
                                    "energy_requests": [None, 52988504.00272718, None, None, None, None],
                                    "cs_charging_power": [0, None, None, 0,  None, None],
                                    "cs_charging_limits": [11000, None, None, 11000,  None, None],
                                    "user_requests" : [None, 1, None, None,  None, None],
                                    "estimated_parking_time": [None, 0.0, None, None,  None, None],
                                    "charging_states": [None ,0.7735534016977471,  None, None,  None, None],

                                    }, 
                                    PowerType(600, PowerTypeUnit.W),
                                ),
                                                                (
                                    { 
                                    "building_power": [-14400],
                                    "current_time": [39000],
                                    "pv_power": [14946.8],
                                    "soc_stat_battery": [0.8244811418286961],
                                    "stat_battery_chrg_pwr_max": [42836.99568776329],
                                    "stat_battery_dischrg_pwr_max": [-79360.04708571943],
                                    "stat_batt_power": [-10453.2001953125],
                                    "grid_power": [11004.266861979168],
                                    "peak_grid_power": [30000.000390625002],
                                    "el_price": [173.81],
                                    "ev_energy": [None, 181011495.99727282, None, None, None, None],
                                    "energy_requests": [None, 52988504.00272718, None, None, None, None],
                                    "cs_charging_power": [0, None, None, 0,  None, None],
                                    "cs_charging_limits": [11000, None, None, 11000,  None, None],
                                    "user_requests" : [4, 1, None, 2,  None, None],
                                    "estimated_parking_time": [None, 0.0, None, None,  None, None],
                                    "charging_states": [None ,0.7735534016977471,  None, None,  None, None],

                                    }, 
                                    PowerType(600, PowerTypeUnit.W),
                                ),

                                
                            ]
                        )
def test_corner_cases(raw_obs,expected_cs_power):
    agent = RuleBasedAgentStatStorage()

    action_raw_base={
            "requested_gini_field": np.full(0,None),
            "requested_gini_power": np.full(0,None),
            "target_charging_power" : np.full(0,None),
            "request_answer": np.full(0,None),
            "target_stat_battery_charging_power" : None
        }
    agent.initialize_action(action_raw_base)
    agent._initialize_stationary_battery_controller()
    #print(agent.stationary_battery_controller.discharging_strategy)
    
    agent.stationary_battery_controller.context.hysteresis_val = 0.01
    #print(agent.stationary_battery_controller)
    agent.calculate_action_stationary_battery_controller(raw_obs)
    # print(f"Charging {agent.stationary_battery_controller.charging_strategy.calculate_charge()}")
    # print(f"Discharging: {agent.stationary_battery_controller.discharging_strategy.calculate_charge()}")
    print(agent.stationary_battery_controller.discharging_strategy)
    print(agent.action["target_stat_battery_charging_power"][0] -11000)




    

