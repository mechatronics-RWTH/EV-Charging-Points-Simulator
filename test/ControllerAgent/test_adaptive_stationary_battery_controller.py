import pytest
from Controller_Agent.Rule_based.Stationary_Battery_Controller.AdaptiveStationaryBatteryController import AdaptiveStationaryBatteryController
from Controller_Agent.Rule_based.Stationary_Battery_Controller.OperatingStrategy import (ChargingStrategy, 
                                                                                         DischargingStrategy, 
                                                                                         OperatingStrategy,
                                                                                         OptimizingSelfConsumption,
                                                                                         SurplusCharging,
                                                                                         LocalCharging,
                                                                                         GridCharging,
                                                                                         LimitingPeakLoad)
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit


def test_init():
    adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController = AdaptiveStationaryBatteryController(soc_a_limit=0.5, soc_x_limit=0.3, soc_y_limit=0.8)
    assert adaptive_stationary_battery_controller.soc_a_limit == 0.5
    assert adaptive_stationary_battery_controller.soc_x_limit == 0.3
    assert adaptive_stationary_battery_controller.soc_y_limit == 0.8
    assert isinstance(adaptive_stationary_battery_controller.charging_strategy, ChargingStrategy)
    assert isinstance(adaptive_stationary_battery_controller.discharging_strategy, DischargingStrategy)

@pytest.fixture
def adaptive_stationary_battery_controller():
    return AdaptiveStationaryBatteryController(soc_a_limit=0.5, soc_x_limit=0.3, soc_y_limit=0.8)

def test_update_state(adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController):
    current_soc=0.7
    P_prod=PowerType(10, unit=PowerTypeUnit.KW)
    P_load=PowerType(50, unit=PowerTypeUnit.KW)
    P_batt_max=PowerType(30, unit=PowerTypeUnit.KW)
    P_grid_max=PowerType(20, unit=PowerTypeUnit.KW)
    adaptive_stationary_battery_controller.update_state(P_prod=P_prod, 
                                                        P_load=P_load, 
                                                        P_batt_chrg_max=P_batt_max, 
                                                        P_batt_dischrg_max=P_batt_max, 
                                                        P_grid_max=P_grid_max, 
                                                        current_soc=current_soc)
    assert adaptive_stationary_battery_controller.charging_strategy.context.P_prod == P_prod
    assert adaptive_stationary_battery_controller.charging_strategy.context.P_load == P_load
    assert adaptive_stationary_battery_controller.charging_strategy.context.P_batt_chrg_max == P_batt_max
    assert adaptive_stationary_battery_controller.charging_strategy.context.P_grid_max == P_grid_max
    assert adaptive_stationary_battery_controller.charging_strategy.context.battery_soc == current_soc

    assert adaptive_stationary_battery_controller.discharging_strategy.context.P_prod == P_prod
    assert adaptive_stationary_battery_controller.discharging_strategy.context.P_load == P_load
    assert adaptive_stationary_battery_controller.discharging_strategy.context.P_batt_dischrg_max == P_batt_max
    assert adaptive_stationary_battery_controller.discharging_strategy.context.P_grid_max == P_grid_max
    assert adaptive_stationary_battery_controller.discharging_strategy.context.battery_soc == current_soc


def test_determine_charging_strategy(adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController):
    adaptive_stationary_battery_controller.charging_strategy.context.battery_soc = 0.2

    adaptive_stationary_battery_controller.determine_charging_strategy()
    assert isinstance(adaptive_stationary_battery_controller.charging_strategy, LocalCharging)
    adaptive_stationary_battery_controller.charging_strategy.context.battery_soc = 0.2
    adaptive_stationary_battery_controller.determine_charging_strategy()
    assert isinstance(adaptive_stationary_battery_controller.charging_strategy, GridCharging)

def test_determine_discharging_strategy(adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController):
    adaptive_stationary_battery_controller.discharging_strategy.context.battery_soc = 0.2
    adaptive_stationary_battery_controller.determine_discharging_strategy()
    assert isinstance(adaptive_stationary_battery_controller.discharging_strategy, LimitingPeakLoad)



def test_calculate_charge(adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController):
    P_prod=PowerType(10, unit=PowerTypeUnit.KW)
    P_load=PowerType(50, unit=PowerTypeUnit.KW)
    P_batt_max=PowerType(30, unit=PowerTypeUnit.KW)
    P_grid_max=PowerType(20, unit=PowerTypeUnit.KW)
    current_soc=0.7
    adaptive_stationary_battery_controller.update_state(P_prod=P_prod, 
                                                        P_load=P_load, 
                                                P_batt_chrg_max=P_batt_max,
                                                P_batt_dischrg_max=P_batt_max,
                                                        P_grid_max=P_grid_max, 
                                                        current_soc=current_soc)
    
    adaptive_stationary_battery_controller.calculate_charge()
    assert adaptive_stationary_battery_controller.charge_power == PowerType(30, unit=PowerTypeUnit.KW)*(-1)


    
@pytest.mark.parametrize("P_prod, P_load, P_batt_max, P_grid_max, current_soc, expected_charging_power, expected_discharging_power",[
                         (PowerType(10, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          0.7,
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW)),
                         
                         (PowerType(20, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(200, PowerTypeUnit.KW),
                          PowerType(100, PowerTypeUnit.KW),
                          0.2,
                          PowerType(20, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW)),

                         (PowerType(5, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          0.7,
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(5, PowerTypeUnit.KW)),

                         (PowerType(10, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          0.6,
                          PowerType(0, PowerTypeUnit.KW),
                            PowerType(0, PowerTypeUnit.KW)),
                        
                         (PowerType(10, PowerTypeUnit.KW),
                          PowerType(100, PowerTypeUnit.KW),
                          PowerType(200, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          0.9,
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(90, PowerTypeUnit.KW)),])

def test_step(adaptive_stationary_battery_controller: AdaptiveStationaryBatteryController,
              P_prod: PowerType,
              P_load: PowerType,
              P_batt_max: PowerType,
              P_grid_max: PowerType,
              current_soc: float,
              expected_charging_power: PowerType,
              expected_discharging_power: PowerType):
    adaptive_stationary_battery_controller.step(current_soc=current_soc,
                                                P_prod=P_prod,
                                                P_load=P_load,
                                                P_batt_chrg_max=P_batt_max,
                                                P_batt_dischrg_max=P_batt_max,
                                                P_grid_max=P_grid_max)
    
    assert adaptive_stationary_battery_controller.charging_strategy.calculate_charge() == expected_charging_power
    assert adaptive_stationary_battery_controller.discharging_strategy.calculate_charge() == expected_discharging_power
    assert adaptive_stationary_battery_controller.charge_power == expected_charging_power + expected_discharging_power*(-1)
    

