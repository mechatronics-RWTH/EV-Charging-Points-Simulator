from SimulationModules.Enums import AgentRequestAnswer
from dataclasses import dataclass

@dataclass
class RequestAnswer:
    field_index: int = None
    answer: AgentRequestAnswer=None 