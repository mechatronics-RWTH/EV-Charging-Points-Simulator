from typing import List
from SimulationModules.Enums import Request_state
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class EvSessionPeriod:

    def __init__(self,
                 id: int,
                 start_index = None,
                 end_index = None,
                 field_index = None) -> None:
        self.id = id
        self.start_index= start_index
        self.end_index= end_index
        self.field_index = field_index
        self.user_request = []
        self.energy_request: List[EnergyType] = []
        self.status =[]
        self.charged_energy: EnergyType = None 


    def add_start(self, index):
        self.start_index= index

    def add_end(self, index):
        self.end_index= index
    
    def calculate_charged_energy(self):
        if len(self.energy_request)==0:
            self.charged_energy = EnergyType(0,EnergyTypeUnit.KWH)
            return
        
        departure_energy_request = self.get_departure_energy_request()
        self.charged_energy = self.energy_request[0] -departure_energy_request
        if self.charged_energy < 0:
            logger.error(f"Charged energy ({self.charged_energy}) is negative for {self}")
            logger.error(f"Energy request {self.energy_request}")
            logger.error(f"Status {self.status}")

    def get_charged_energy(self):
        if self.charged_energy is None:
            self.calculate_charged_energy()
        return self.charged_energy

    def get_departure_energy_request(self):
        return self.energy_request[-1]
    
    def is_finished(self):
        return self.end_index is not None

    def __repr__(self) -> str:
        return f"Session {self.id} from {self.start_index} to {self.end_index} with field index {self.field_index} and charged energy {self.charged_energy}"

