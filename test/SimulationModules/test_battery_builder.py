from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.Batteries.PowerMap import TypeOfChargingCurve
from unittest.mock import MagicMock

class TestBatteryBuilder:

    def test_battery_builder(self):
        battery_builder = BatteryBuilder()
        assert True

    def test_set_maximum_power_limits_by_c_rate(self):
        battery_builder = BatteryBuilder()
        battery_builder.set_maximum_power_limits_by_c_rate(battery_energy=EnergyType(50, EnergyTypeUnit.KWH), 
                                                           maximum_charging_c_rate=1.5, 
                                                           maximum_discharging_c_rate=1.5)
        assert battery_builder.maximum_charging_power == PowerType(75, PowerTypeUnit.KW)
        assert battery_builder.maximum_discharging_power == PowerType(75, PowerTypeUnit.KW)

    def test_derive_power_map(self):
        battery_builder = BatteryBuilder()
        battery_builder.maximum_charging_power = PowerType(75, PowerTypeUnit.KW)
        battery_builder.maximum_discharging_power = PowerType(75, PowerTypeUnit.KW)
        battery_builder.derive_power_map(power_map_type=TypeOfChargingCurve.LIMOUSINE)
        assert battery_builder.charging_power_map is not None

    def test_create_battery(self):
        battery_builder = BatteryBuilder()
        battery_builder.battery_energy = EnergyType(50, EnergyTypeUnit.KWH)
        battery_builder.present_energy = EnergyType(30, EnergyTypeUnit.KWH)
        mock_map = MagicMock()
        battery_builder.charging_power_map =mock_map
        battery = battery_builder.create_battery()
        assert battery.battery_energy == EnergyType(50, EnergyTypeUnit.KWH)
        assert battery.present_energy == EnergyType(30, EnergyTypeUnit.KWH)
        assert battery.charging_power_map == mock_map

    def test_build_battery(self):
        battery =BatteryBuilder().build_battery(power_map_type=TypeOfChargingCurve.LIMOUSINE,
                                       battery_energy=EnergyType(50, EnergyTypeUnit.KWH),
                                       present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                                       maximum_charging_c_rate=1.5,
                                       maximum_discharging_c_rate=1.5)
        assert battery is not None
        
