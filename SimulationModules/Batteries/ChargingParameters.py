from dataclasses import dataclass
from SimulationModules.datatypes import PowerType
from SimulationModules.datatypes import EnergyType

@dataclass
class ChargingParameters:
    """
    Those are the charging parameters that can be used by the ChargeParameterDiscoveryReq
    """
    maximum_charging_power: PowerType
    maximum_discharging_power: PowerType
    maximum_energy: EnergyType
    minimum_energy: EnergyType
