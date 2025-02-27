from SimulationModules.datatypes.EnergyType import EnergyType
from config.logger_config import get_module_logger
from SimulationModules.Reward.InterfaceUserSatisfactionRecord import InterfaceUserSatisfactionRecord

logger = get_module_logger(__name__)

class UserSatisfactionRecord(InterfaceUserSatisfactionRecord):
    def __init__(self, session_id: str,
                 energy_request_initial: EnergyType,
                 energy_request_final: EnergyType,
                 denied: bool):
        self.session_id = session_id
        self.xi_user_satisfaction = None
        self.xi_user_satisfaction_denied = None
        self.xi_user_satisfaction_charge_missing = None
        self.xi_user_satisfaction_confirmed_but_not_charged = None
        self.energy_request_initial: EnergyType = energy_request_initial
        self.energy_request_final: EnergyType = energy_request_final
        self.denied: bool = denied
        self.assumped_fee_per_kwh = 0.5
        self.penalty_factor_denied =1.2
        self.penalty_factor_charge_missing = 1.5
        self.penalty_confirmed_but_not_charged = 10 

    
    def get_xi_user_satisfaction(self):
        return self.xi_user_satisfaction
    
    def get_xi_user_satisfaction_denied(self):
        return self.xi_user_satisfaction_denied
    
    def get_xi_user_satisfaction_charge_missing(self):
        return self.xi_user_satisfaction_charge_missing
    
    def get_xi_user_satisfaction_confirmed_but_not_charged(self):
        return self.xi_user_satisfaction_confirmed_but_not_charged
    
    def calculate_user_satisfaction_denied(self):
        if self.denied:
            self.xi_user_satisfaction_denied = -(self.energy_request_initial.get_in_kwh().value * self.penalty_factor_denied* self.assumped_fee_per_kwh)
        else:
            self.xi_user_satisfaction_denied = 0

    
    def calculate_user_satisfaction_charge_missing(self):
        if not self.denied and self.energy_request_final.get_in_kwh().value > 0:
            self.xi_user_satisfaction_charge_missing = -(self.energy_request_final.get_in_kwh().value * self.penalty_factor_charge_missing * self.assumped_fee_per_kwh)
        else:
            self.xi_user_satisfaction_charge_missing = 0

    def calculate_user_satisfaction_confirmed_but_not_charged(self):
        if not self.denied and self.energy_request_final == self.energy_request_initial:
            self.xi_user_satisfaction_confirmed_but_not_charged = -self.penalty_confirmed_but_not_charged
        else:
            self.xi_user_satisfaction_confirmed_but_not_charged = 0
    
    def calculate_xi_user_satisfaction(self):        
        self.calculate_user_satisfaction_denied()
        self.calculate_user_satisfaction_charge_missing()
        self.calculate_user_satisfaction_confirmed_but_not_charged()
        logger.debug(f"{self}")
        self.xi_user_satisfaction = self.xi_user_satisfaction_denied + self.xi_user_satisfaction_charge_missing + self.xi_user_satisfaction_confirmed_but_not_charged

    def __str__(self):
        return f"Session ID: {self.session_id}, Energy Request Initial: {self.energy_request_initial}, Energy Request Final: {self.energy_request_final}, Denied: {self.denied}, User Satisfaction: {self.xi_user_satisfaction}, User Satisfaction Denied: {self.xi_user_satisfaction_denied}, User Satisfaction Charge Missing: {self.xi_user_satisfaction_charge_missing}, User Satisfaction Confirmed But Not Charged: {self.xi_user_satisfaction_confirmed_but_not_charged}"