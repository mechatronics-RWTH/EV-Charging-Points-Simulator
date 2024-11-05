import pytest 
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

@pytest.fixture()
def controlled_electrical_consumer() -> ControlledEletricalGridConsumer:
    return ControlledEletricalGridConsumer(name="test_consumer",
                                           maximum_charging_power=PowerType(10, PowerTypeUnit.KW),
                                           minimum_charging_power=PowerType(-10, PowerTypeUnit.KW))

def test_limit_grid_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    assert controlled_electrical_consumer.limit_grid_power(PowerType(15, PowerTypeUnit.KW)) == PowerType(10, PowerTypeUnit.KW)
    assert controlled_electrical_consumer.limit_grid_power(PowerType(-15, PowerTypeUnit.KW)) == PowerType(-10, PowerTypeUnit.KW)
    assert controlled_electrical_consumer.limit_grid_power(PowerType(5, PowerTypeUnit.KW)) == PowerType(5, PowerTypeUnit.KW)
    assert controlled_electrical_consumer.limit_grid_power(PowerType(-5, PowerTypeUnit.KW)) == PowerType(-5, PowerTypeUnit.KW)

def test_set_target_grid_charging_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    controlled_electrical_consumer.set_target_grid_charging_power(PowerType(5, PowerTypeUnit.KW))
    assert controlled_electrical_consumer.target_grid_power == PowerType(5, PowerTypeUnit.KW)

def test_get_target_grid_charging_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    controlled_electrical_consumer.set_target_grid_charging_power(PowerType(5, PowerTypeUnit.KW))
    assert controlled_electrical_consumer.get_target_grid_charging_power() == PowerType(5, PowerTypeUnit.KW)

def test_set_actual_consumer_charging_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    controlled_electrical_consumer.set_actual_consumer_charging_power(PowerType(5, PowerTypeUnit.KW))
    assert controlled_electrical_consumer.actual_consumer_power == PowerType(5, PowerTypeUnit.KW)

def test_get_actual_consumer_charging_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    controlled_electrical_consumer.set_actual_consumer_charging_power(PowerType(5, PowerTypeUnit.KW))
    assert controlled_electrical_consumer.get_actual_consumer_charging_power() == PowerType(5, PowerTypeUnit.KW)

def test_get_maximum_grid_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    assert controlled_electrical_consumer.get_maximum_grid_power() == PowerType(10, PowerTypeUnit.KW)

def test_get_minimum_grid_power(controlled_electrical_consumer: ControlledEletricalGridConsumer):
    assert controlled_electrical_consumer.get_minimum_grid_power() == PowerType(-10, PowerTypeUnit.KW)




