from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class EnergyCostRewardMetrik(InterfaceRewardMetrik):

    def __init__(self, 
                 metrik_name: str = "energy_cost", 
                 cost: float = 0,
                 electricity_cost: ElectricityCost=None,):
        self.metrik_name = metrik_name
        self.step_cost = cost
        self.total_cost = 0
        self.electricity_cost: ElectricityCost =electricity_cost

    def get_name(self):
        return self.metrik_name

    def calculate_total_cost(self):
        self.total_cost +=self.step_cost

    def get_step_cost(self):
        return self.step_cost
    
    def get_total_cost(self):
        return self.total_cost
    
    def calculate_step_cost(self):
        
        cost=self.electricity_cost.get_energy_costs_step()
        if cost is None:
            self.step_cost=0
        else:
            self.step_cost=cost        
        

    
