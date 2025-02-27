from Controller_Agent.Rule_based.Stationary_Battery_Controller.OperatingStrategy import (ChargingStrategy, 
    DischargingStrategy, 
    OperatingStrategy,
    SurplusCharging,
    LocalCharging,
    GridCharging,
    LimitingPeakLoad,
    OptimizingSelfConsumption,
    Context)
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import pytest

@pytest.fixture
def parameters_for_operating_strategy():
    return Context(P_prod=PowerType(0, PowerTypeUnit.W),
                    P_load=PowerType(0, PowerTypeUnit.W),
                    P_batt_chrg_max=PowerType(0, PowerTypeUnit.W),
                    P_batt_dischrg_max=PowerType(0, PowerTypeUnit.W),
                    P_grid_max=PowerType(10, PowerTypeUnit.W),
                    battery_soc=0.5,
                    soc_a_limit=0.8,
                    soc_x_limit=0.5,
                    soc_y_limit=0.4,
                    hysteresis_val=0.01)
    

@pytest.fixture
def surplus_charging(parameters_for_operating_strategy):  
    return SurplusCharging(parameters_for_operating_strategy)

@pytest.fixture
def local_charging(parameters_for_operating_strategy):  
    return LocalCharging(parameters_for_operating_strategy)

@pytest.fixture
def grid_charging(parameters_for_operating_strategy):  
    return GridCharging(parameters_for_operating_strategy)


@pytest.fixture
def limiting_peak_lead(parameters_for_operating_strategy):  
    return LimitingPeakLoad(parameters_for_operating_strategy)

@pytest.fixture
def optimize_self_comsumption(parameters_for_operating_strategy):  
    return OptimizingSelfConsumption(parameters_for_operating_strategy)

def test_surplus_charging_calculate_charge(surplus_charging: OperatingStrategy):

    surplus_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    surplus_charging.context.P_load = PowerType(50, PowerTypeUnit.KW)
    surplus_charging.context.P_batt_chrg_max = PowerType(100, PowerTypeUnit.KW)
    assert surplus_charging.calculate_charge() == PowerType(50, PowerTypeUnit.KW)
    surplus_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    surplus_charging.context.P_load = PowerType(50, PowerTypeUnit.KW)
    surplus_charging.context.P_batt_chrg_max = PowerType(30, PowerTypeUnit.KW)
    assert surplus_charging.calculate_charge() == PowerType(30, PowerTypeUnit.KW)
    surplus_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    surplus_charging.context.P_load = PowerType(150, PowerTypeUnit.KW)
    surplus_charging.context.P_batt_chrg_max = PowerType(30, PowerTypeUnit.KW)
    assert surplus_charging.calculate_charge() == PowerType(0, PowerTypeUnit.KW)



def test_surplus_charging_process(surplus_charging: OperatingStrategy):
    surplus_charging.context.battery_soc = 0.9
    assert isinstance(surplus_charging.process(), SurplusCharging)
    surplus_charging.context.battery_soc = 0.45
    assert isinstance(surplus_charging.process(), LocalCharging)
    surplus_charging.context.battery_soc = 0.85
    assert isinstance(surplus_charging.process(), SurplusCharging)


def test_local_charging_calculate_charge(local_charging: OperatingStrategy):
    local_charging.context.P_prod = PowerType(400, PowerTypeUnit.KW)
    local_charging.context.P_load = PowerType(300, PowerTypeUnit.KW)
    local_charging.context.P_batt_chrg_max = PowerType(30, PowerTypeUnit.KW)
    local_charging.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    print(local_charging.calculate_charge())
    assert local_charging.calculate_charge() == PowerType(30, PowerTypeUnit.KW)
    local_charging.context.P_prod = PowerType(400, PowerTypeUnit.KW)
    local_charging.context.P_load = PowerType(300, PowerTypeUnit.KW)
    local_charging.context.P_batt_chrg_max = PowerType(500, PowerTypeUnit.KW)
    local_charging.context.P_grid_max = PowerType(320, PowerTypeUnit.KW)
    assert local_charging.calculate_charge() == PowerType(400, PowerTypeUnit.KW)
    local_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    local_charging.context.P_load = PowerType(300, PowerTypeUnit.KW)
    local_charging.context.P_batt_chrg_max = PowerType(500, PowerTypeUnit.KW)
    local_charging.context.P_grid_max = PowerType(100, PowerTypeUnit.KW)
    assert local_charging.calculate_charge() == PowerType(0, PowerTypeUnit.KW)

def test_local_charging_process(local_charging: OperatingStrategy):
    local_charging.context.battery_soc = 0.9
    assert isinstance(local_charging.process(), SurplusCharging)
    local_charging.context.battery_soc = 0.45
    assert isinstance(local_charging.process(), LocalCharging)
    local_charging.context.battery_soc = 0.4
    assert isinstance(local_charging.process(), LocalCharging)


def test_grid_charging_calculate_charge(grid_charging: OperatingStrategy):
    grid_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_load = PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_batt_chrg_max = PowerType(30, PowerTypeUnit.KW)
    grid_charging.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert grid_charging.calculate_charge() == PowerType(30, PowerTypeUnit.KW)
    grid_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_load = PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_batt_chrg_max = PowerType(120, PowerTypeUnit.KW)
    grid_charging.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert grid_charging.calculate_charge() == PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    grid_charging.context.P_load = PowerType(300, PowerTypeUnit.KW)
    grid_charging.context.P_batt_chrg_max = PowerType(120, PowerTypeUnit.KW)
    grid_charging.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert grid_charging.calculate_charge() == PowerType(0, PowerTypeUnit.KW)

def test_grid_charging_process(grid_charging: OperatingStrategy):
    grid_charging.context.battery_soc = 0.5
    assert isinstance(grid_charging.process(), LocalCharging)
    grid_charging.context.battery_soc = 0.3
    assert isinstance(grid_charging.process(), GridCharging)
    grid_charging.context.battery_soc = 0.4
    assert isinstance(grid_charging.process(), GridCharging)

def test_optimizing_self_consumption_calculate_charge(optimize_self_comsumption: OperatingStrategy):
    optimize_self_comsumption.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_load = PowerType(200, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_batt_dischrg_max = PowerType(30, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert optimize_self_comsumption.calculate_charge() == PowerType(30, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_prod = PowerType(100, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_load = PowerType(200, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_batt_dischrg_max = PowerType(130, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert optimize_self_comsumption.calculate_charge() == PowerType(100, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_prod = PowerType(300, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_load = PowerType(200, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_batt_dischrg_max = PowerType(130, PowerTypeUnit.KW)
    optimize_self_comsumption.context.P_grid_max = PowerType(200, PowerTypeUnit.KW)
    assert optimize_self_comsumption.calculate_charge() == PowerType(0, PowerTypeUnit.KW)


def test_optimizing_self_consumption_process(optimize_self_comsumption: OperatingStrategy):
    optimize_self_comsumption.context.battery_soc = 0.9
    assert isinstance(optimize_self_comsumption.process(), OptimizingSelfConsumption)
    optimize_self_comsumption.context.battery_soc = 0.3
    assert isinstance(optimize_self_comsumption.process(), LimitingPeakLoad)
    optimize_self_comsumption.context.battery_soc = 0.8
    assert isinstance(optimize_self_comsumption.process(), OptimizingSelfConsumption)


def test_limiting_peak_load_calculate_charge(limiting_peak_lead: OperatingStrategy):
    limiting_peak_lead.context.P_prod = PowerType(20, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_load = PowerType(200, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_batt_dischrg_max = PowerType(200, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_grid_max = PowerType(20, PowerTypeUnit.KW)
    assert limiting_peak_lead.calculate_charge() == PowerType(160, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_prod = PowerType(20, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_load = PowerType(200, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_batt_dischrg_max = PowerType(30, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_grid_max = PowerType(20, PowerTypeUnit.KW)
    assert limiting_peak_lead.calculate_charge() == PowerType(30, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_prod = PowerType(20, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_load = PowerType(200, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_batt_dischrg_max = PowerType(30, PowerTypeUnit.KW)
    limiting_peak_lead.context.P_grid_max = PowerType(190, PowerTypeUnit.KW)
    assert limiting_peak_lead.calculate_charge() == PowerType(0, PowerTypeUnit.KW) 

def test_limiting_peak_load_process(limiting_peak_lead: OperatingStrategy):
    limiting_peak_lead.context.battery_soc = 0.9
    assert isinstance(limiting_peak_lead.process(), OptimizingSelfConsumption)
    limiting_peak_lead.context.battery_soc = 0.3
    assert isinstance(limiting_peak_lead.process(), LimitingPeakLoad)
    limiting_peak_lead.context.battery_soc = 0.5
    assert isinstance(limiting_peak_lead.process(), LimitingPeakLoad)



@pytest.mark.parametrize("P_prod, P_load, P_batt_max, P_grid_max, expected_charging_power", [
                         (PowerType(10, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          ),
                         
                         (PowerType(20, PowerTypeUnit.KW),
                          PowerType(0, PowerTypeUnit.KW),
                          PowerType(200, PowerTypeUnit.KW),
                          PowerType(100, PowerTypeUnit.KW),                          
                          PowerType(20, PowerTypeUnit.KW),),

                        (PowerType(10, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),
                          PowerType(1000, PowerTypeUnit.KW),
                          PowerType(10, PowerTypeUnit.KW),),
                          ])
def test_local_charging(local_charging: OperatingStrategy,
    P_prod, 
    P_load, 
    P_batt_max, 
    P_grid_max, 
    expected_charging_power):
    local_charging.context.P_prod = P_prod
    local_charging.context.P_load = P_load
    local_charging.context.P_batt_chrg_max = P_batt_max
    local_charging.context.P_grid_max = P_grid_max

    assert local_charging.calculate_charge()== expected_charging_power
     