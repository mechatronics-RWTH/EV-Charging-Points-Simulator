from SimulationModules.Gini.GiniBuilder import GiniBuilder
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

class TestGiniBuilder():


    def test_gini_battery_energy(self):
        starting_fields = [1,2,3]
        gini_builder =GiniBuilder()
        ginis = gini_builder.build(gini_starting_fields=starting_fields)
        assert ginis[0].battery.get_battery_energy_capacity() == EnergyType(35, EnergyTypeUnit.KWH)
        assert ginis[1].battery.get_battery_energy_capacity() == EnergyType(35, EnergyTypeUnit.KWH)
        assert ginis[2].battery.get_battery_energy_capacity() == EnergyType(35, EnergyTypeUnit.KWH)

    def test_gini_battery_power(self):
        starting_fields = [1]
        gini_builder =GiniBuilder()
        ginis = gini_builder.build(gini_starting_fields=starting_fields,
                                   present_energy=EnergyType(17.5, EnergyTypeUnit.KWH))

        assert ginis[0].battery.charging_power_map.get_maximum_charging_power(0.3) > PowerType(45, PowerTypeUnit.KW)
        assert ginis[0].battery.charging_power_map.get_maximum_charging_power(0.3) < PowerType(50, PowerTypeUnit.KW)
        assert ginis[0].battery.charging_power_map.get_maximum_charging_power(0.4) > PowerType(45, PowerTypeUnit.KW)
        assert ginis[0].battery.charging_power_map.get_maximum_charging_power(0.4) < PowerType(50, PowerTypeUnit.KW)
