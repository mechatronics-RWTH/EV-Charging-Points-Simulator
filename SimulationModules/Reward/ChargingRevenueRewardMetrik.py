from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.datatypes.EnergyType import EnergyType 
from SimulationModules.ElectricVehicle.EV import EV
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class ChargingRevenueRewardMetrik(InterfaceRewardMetrik):

    def __init__(self, 
                 metrik_name: str = "charging_revenue", 
                 cost: float = 0,
                 charging_session_manager: ChargingSessionManager =None):
        self.metrik_name = metrik_name
        self.step_cost = cost
        self.total_cost = 0
        self.charging_session_manager: ChargingSessionManager =charging_session_manager

    def get_name(self):
        return self.metrik_name

    def calculate_total_cost(self):
        self.total_cost += self.step_cost
        logger.info(f"Total Charging Revenue of {self}: {self.total_cost}")

    def get_step_cost(self):
        return self.step_cost 

    def get_total_cost(self):
        return self.total_cost  
    
    def calculate_step_cost(self):
        self.step_cost = 0
        for active_session in self.charging_session_manager.active_sessions:
            if isinstance(active_session,ChargingSession) and isinstance(active_session.ev, EV):
                energy_value: EnergyType = active_session.power_transfer_trajectory.get_last_energy_value()
                self.step_cost += energy_value.get_in_kwh().value * 0.5
                logger.info(f"Charging Revenue: {self.step_cost}")
                try:
                    active_session.power_transfer_trajectory.check_charged_energy()
                except Exception as e:
                    logger.error(f"Error in session {active_session.session_id}:  {e}")

    def __str__(self):
        return self.metrik_name

