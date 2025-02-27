from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from SimulationModules.Enums import Request_state
from typing import List



class InterfaceChargingStateTrajectory(ABC):
    charging_state_trajectory: List[Request_state]
    time_trajectory: List[datetime]

    @abstractmethod
    def add_entry(self, 
                  charging_state: Request_state, 
                  time: datetime):
        pass

class ChargingStateTrajectory(InterfaceChargingStateTrajectory):
    def __init__(self):
        self.charging_state_trajectory = []
        self.time_trajectory = []

    def add_entry(self, 
                  charging_state: Request_state, 
                  time: datetime):
        if not isinstance(charging_state, Request_state):
            raise ValueError("Invalid charging state")
        if not isinstance(time, datetime):
            raise ValueError(f"Invalid time of type: {type(time)}")
        self.charging_state_trajectory.append(charging_state)
        self.time_trajectory.append(time)





