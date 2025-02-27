from dataclasses import dataclass, field
from typing import Union
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit

@dataclass
class EvPredictionData:

    soc: float = None
    requested_energy: EnergyType = None

    arrival_time: float = None
    stay_duration: float = None
    id: int = None
    parking_spot_id: int = None
    has_arrived: bool = False
    _requested_energy: EnergyType = field(default=None, init=False)

    @property
    def requested_energy(self) -> EnergyType:
        return self._requested_energy

    @requested_energy.setter
    def requested_energy(self, value: EnergyType):
        if not isinstance(value, EnergyType) and value is not None:
            raise TypeError(f"requested_energy must be a EnergyType not {type(value)}")
        self._requested_energy = value

    def set_by_other(self, other):
        self.soc = self.set_soc(other.soc)
        self.requested_energy = self.set_requested_energy(other.requested_energy)
        self.arrival_time = self.set_arrival_time(other.arrival_time)
        self.stay_duration = self.set_stay_duration(other.stay_duration)
        self.id = self.set_id(other.id)
        self.parking_spot_id = self.set_parking_spot_id(other.parking_spot_id)
        self.has_arrived = self.set_has_arrived(other.has_arrived)


    def set_soc(self, soc):
        if isinstance(soc, (float,int)):
            self.soc = soc
        else:
            raise TypeError("SOC must be a float")

    # def set_requested_energy(self, requested_energy):
    #     if isinstance(requested_energy,(float,int)):
    #         self.requested_energy = requested_energy
    #     else:
    #         raise TypeError("Requested energy must be a float")

    def set_arrival_time(self, arrival_time):
        if isinstance(arrival_time, (float,int)):
            self.arrival_time = arrival_time
        else:
            raise TypeError("Arrival time must be a float  ")

    def set_stay_duration(self, stay_duration):
        if isinstance(stay_duration, (float,int)):
            self.stay_duration = stay_duration
        else:
            raise TypeError("Stay duration must be a float")
        

    def set_id(self, id):
        if isinstance(id, int):
            self.id = id
        else:
            raise TypeError("ID must be an int")
    
    def set_parking_spot_id(self, parking_spot_id):
        if isinstance(parking_spot_id, int):
            self.parking_spot_id = parking_spot_id
        else:
            raise TypeError("Parking spot ID must be an int")

    def set_has_arrived(self, has_arrived):
        if isinstance(has_arrived, bool):
            self.has_arrived = has_arrived
        else:
            raise TypeError("Has arrived must be a bool")
