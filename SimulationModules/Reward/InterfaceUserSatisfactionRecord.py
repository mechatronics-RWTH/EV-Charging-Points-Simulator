from abc import ABC, abstractmethod
from SimulationModules.datatypes.EnergyType import EnergyType


class InterfaceUserSatisfactionRecord(ABC):
    session_id: str
    xi_user_satisfaction: float
    xi_user_satisfaction_denied: float
    xi_user_satisfaction_charge_missing: float
    xi_user_satisfaction_confirmed_but_not_charged: float
    energy_request_initial: EnergyType
    energy_request_final: EnergyType
    denied: bool
    assumped_fee_per_kwh: float
    penalty_factor_denied: float
    penalty_factor_charge_missing: float
    penalty_confirmed_but_not_charged:float


    @abstractmethod
    def get_xi_user_satisfaction(self):
        raise NotImplementedError 
    
    @abstractmethod
    def calculate_xi_user_satisfaction(self):
        raise NotImplementedError