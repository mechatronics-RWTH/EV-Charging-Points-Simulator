from gymnasium.spaces import Dict, Box, MultiBinary, Discrete

from config.logger_config import get_module_logger

from Controller_Agent.InterfaceAgent import InterfaceAgent, TemplateAgent
from SimulationModules.RequestHandling.Request import Request_state

from SimulationModules.Enums import TypeOfField, AgentRequestAnswer
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from Controller_Agent.Rule_based.ChargingPowerLimiter import ChargingPowerLimiter
from Controller_Agent.Rule_based.GiniMovementController import GiniMovementController


logger = get_module_logger(__name__)



class RuleBasedAgent_One(TemplateAgent,
                         ChargingPowerLimiter,
                         GiniMovementController):

    def __init__(self,                
                    P_grid_max: PowerType =PowerType(power_in_w=20, unit=PowerTypeUnit.KW)):
        ChargingPowerLimiter.__init__(self,P_grid_max)
        GiniMovementController.__init__(self) 
        super().__init__()
        self.initialized = False

  
    def handle_unanswered_requests(self):
            self._confirm_all_unanswered_requests()

    def _confirm_all_unanswered_requests(self):
        #at first, every not answered request is confirmed
        
        for i, request_state in enumerate(self.user_request):     
                if request_state==Request_state.REQUESTED.value:
                        self.action["request_answer"][i]=AgentRequestAnswer.CONFIRM.value

    def is_occupied_by_gini(self, charging_spot_index: int) -> bool:
        return GiniMovementController.is_occupied_by_gini(self, charging_spot_index)
    
    def request_moving_ginis(self):
        unoccupied_charging_spot_index = [charging_spot_index for charging_spot_index in self.charging_spot_list if not self.is_spot_occupied(charging_spot_index)]
        GiniMovementController.request_moving_ginis(self, unoccupied_charging_spot_index=unoccupied_charging_spot_index)
    
    def limit_charging_power_if_required(self, raw_obs: Dict):
        ChargingPowerLimiter.limit_charging_power_if_required(self,raw_obs)
    