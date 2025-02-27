from gymnasium.spaces import Dict, Box, MultiBinary, Discrete

from Controller_Agent.InterfaceAgent import TemplateAgent
from Controller_Agent.Rule_based.ChargingPowerLimiter import ChargingPowerLimiter
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

class RuleBasedAgent_NoGini(TemplateAgent, ChargingPowerLimiter):

        def __init__(self,                
                     P_grid_max: PowerType):
                ChargingPowerLimiter.__init__(self, P_grid_max)
                super().__init__()
                self.initialized = False

        def handle_unanswered_requests(self):
                pass
        
        def limit_charging_power_if_required(self, raw_obs: Dict):
                ChargingPowerLimiter.limit_charging_power_if_required(self,raw_obs)

        def request_moving_ginis(self):
                pass

