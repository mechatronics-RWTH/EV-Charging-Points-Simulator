from dataclasses import dataclass
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
import numbers

class AcceptedEvRecordCollection(list):
    """RecordAcceptedEvsCollection class is used to record the number of EVs that are accepted by the aggregator in each episode.
    
    Attributes:
    - accepted_evs: int: The number of EVs that are accepted by the aggregator in each episode.
    """
    def __init__(self, *args):
        super().__init__(*args)

    def add_record(self, 
               field_index: int,
               target_energy: float,
               energy_request: float):
        self.append(RequestEvRecord(field_index, target_energy, energy_request))

    def remove_record_by_field(self, field_index: int):
        for record in self:
            if record.field_index == field_index:
                self.remove(record)

    def insert(self, index, item):
        self._validate(item)
        super().insert(index, item)

    def _validate(self, item):
        if not isinstance(item, RequestEvRecord):
            raise TypeError(f"Only AcceptedEvRecord instances can be added, got {type(item).__name__}")
        
    def extend(self, iterable):
        for item in iterable:
            self._validate(item)
        super().extend(iterable)

#@dataclass
class RequestEvRecord:
    """RecordAcceptedEvs class is used to record the number of EVs that are accepted by the aggregator in each episode.
    
    Attributes:
    - accepted_evs: int: The number of EVs that are accepted by the aggregator in each episode.
    """
    def __init__(self, 
                 field_index: int,
                 target_energy: float,
                 energy_request: float,
                 status=None):
        self.field_index: int = field_index 
        if not isinstance(target_energy, numbers.Number):
            raise ValueError(f"target_energy must be of type float")
        if not isinstance(energy_request, numbers.Number):
            raise ValueError(f"energy_request must be of type float")
        self.target_energy: EnergyType = EnergyType(target_energy, EnergyTypeUnit.J)
        self.energy_request: EnergyType = EnergyType(energy_request, EnergyTypeUnit.J)
        self.status = status
