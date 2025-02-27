from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.Gini.Gini import GINI
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class GiniChargingCostRewardMetrik(InterfaceRewardMetrik):
    def __init__(self, 
                 metrik_name: str, 
                 cost: float = 0,
                 charging_session_manager: ChargingSessionManager = None,
                 gini: GINI = None,
                 electricity_cost: ElectricityCost = None,                                
                 ):
        self.metrik_name = metrik_name
        self.step_cost = cost
        self.total_cost = 0
        self.charging_session_manager: ChargingSessionManager =charging_session_manager
        self.electricity_cost: ElectricityCost =electricity_cost 
        self.gini: GINI = gini  

    
    def get_name(self):
        return self.metrik_name

    
    def get_name(self):
        return self.metrik_name

    def calculate_total_cost(self):
        self.total_cost +=self.step_cost

    def get_step_cost(self):
        return self.step_cost
    
    def get_total_cost(self):
        return self.total_cost
    
    def calculate_step_cost(self):
        self.step_cost = 0
        for active_session in self.charging_session_manager.active_sessions:
            if isinstance(active_session,ChargingSession) and active_session.ev == self.gini:
                energy_value: EnergyType = active_session.power_transfer_trajectory.get_last_energy_value()
                self.step_cost = energy_value.get_in_kwh().value * self.electricity_cost.get_average_energy_costs_step()

     