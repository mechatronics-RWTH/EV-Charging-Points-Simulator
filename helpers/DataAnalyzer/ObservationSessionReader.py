from typing import List
from helpers.DataAnalyzer.EvSessionPeriods import EvSessionPeriod
from SimulationModules.Enums import Request_state
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit

class ObservationSessionReader:
    def __init__(self, 
                 user_requests = [], 
                 energy_requests =[]):
        self.user_requests = user_requests
        self.energy_requests = energy_requests
        self.step = 0
        self.session_id = 0
        self.ev_session_periods: List[EvSessionPeriod] = []
        self.active_ev_sessions: List[EvSessionPeriod] = []
        self.fields_of_active_sessions = []
        self.active_energy_requests = []
        self.active_user_requests = []
        self.active_fields = []

    def set_user_requests(self, user_requests):
        self.user_requests = user_requests

    def set_energy_requests(self, energy_requests):
        self.energy_requests = energy_requests

    def check_user_requests_and_energy_requests(self):
        if len(self.user_requests) != len(self.energy_requests):
            raise ValueError(f"The number of energy requests ({len(self.energy_requests)}) and user requests ({len(self.user_requests)}) must be the same")

    def set_active_requests(self,index):
        self.active_energy_requests = self.energy_requests[index]
        self.active_user_requests = self.user_requests[index]
        if len(self.active_energy_requests) != len(self.active_user_requests):
            raise ValueError("The number of energy requests and user requests must be the same")
        
    def set_active_parking_fields(self):
        self.active_fields = [request[0] for request in self.active_user_requests]
        #print(f"{self.step} with fields {self.active_fields}")

    def get_user_request_by_field_index(self, field_index):
        return next((request[1] for request in self.active_user_requests if request[0] == field_index), None)

    def get_energy_request_by_field_index(self, field_index):
        return next((request[1] for request in self.active_energy_requests if request[0] == field_index), None)

    def get_last_status_from_session(self, ev_session: EvSessionPeriod):
        if len(ev_session.status) == 0:
            return 0 # to ensure that the session is stopped
        return ev_session.status[-1]


    def read_sessions_from_requests(self):
        self.check_user_requests_and_energy_requests()
        self.session_id = 0
        for time_index in range(len(self.user_requests)):
            self.step = time_index
            self.set_active_requests(self.step)
            self.set_active_parking_fields()
            if len(self.active_user_requests) == 0:
                continue
            self.update_sessions()
            self.start_sessions()
        
        for ev_session in self.active_ev_sessions:
            ev_session.add_end(self.step)
            ev_session.calculate_charged_energy()

    def start_sessions(self):
        for field_index in self.active_fields:
            if field_index not in self.fields_of_active_sessions:
                ev_session = EvSessionPeriod(id=self.session_id, field_index=field_index)
                self.add_energy_request_to_session(ev_session)
                self.add_user_request_to_session(ev_session)
                ev_session.add_start(self.step)
                self.ev_session_periods.append(ev_session)
                
                self.session_id += 1
        self.update_active_sessions()
        

    def update_sessions(self):
        self.update_active_sessions()
        for ev_session in self.active_ev_sessions:

            if ev_session.is_finished():
                continue
            self.check_for_session_end(ev_session)
            if ev_session.is_finished():
                continue           

            self.add_data_to_session(ev_session)
        #self.update_active_sessions()
        
        
    def update_active_sessions(self):
        self.active_ev_sessions = [ev_session for ev_session in self.ev_session_periods if not ev_session.is_finished()]
        self.fields_of_active_sessions= [session.field_index for session in self.active_ev_sessions]

    def add_energy_request_to_session(self, ev_session: EvSessionPeriod):
        energy_in_j = self.get_energy_request_by_field_index(ev_session.field_index)
        if energy_in_j is None:
            raise ValueError("Energy request must not be None")
        energy = EnergyType(energy_amount_in_j=energy_in_j, unit=EnergyTypeUnit.J).get_in_kwh()
        ev_session.energy_request.append(energy)
    
    def add_user_request_to_session(self, ev_session: EvSessionPeriod):
        user_request = self.get_user_request_by_field_index(ev_session.field_index)
        if user_request is None:
            raise ValueError("User request must not be None")
        ev_session.status.append(user_request)

    def add_data_to_session(self, ev_session: EvSessionPeriod):
        self.add_energy_request_to_session(ev_session)
        self.add_user_request_to_session(ev_session)

    def end_session_if_no_request(self, ev_session: EvSessionPeriod):
        if self.get_user_request_by_field_index(ev_session.field_index) is None:
            ev_session.add_end(self.step-1)
            ev_session.calculate_charged_energy()

    def end_session_if_request_below_last_status(self, ev_session: EvSessionPeriod):
        if self.get_user_request_by_field_index(ev_session.field_index) < self.get_last_status_from_session(ev_session):
            ev_session.add_end(self.step-1)
            ev_session.calculate_charged_energy()

    def end_session_if_request_satisfied(self, ev_session: EvSessionPeriod):
        if self.get_user_request_by_field_index(ev_session.field_index) == Request_state.SATISFIED:
            self.add_data_to_session(ev_session)
            ev_session.add_end(self.step)
            ev_session.calculate_charged_energy()

    def check_for_session_end(self,ev_session: EvSessionPeriod):
        end_checkers = [self.end_session_if_no_request, self.end_session_if_request_below_last_status, self.end_session_if_request_satisfied]
        for checker in end_checkers:
            checker(ev_session)
            if ev_session.is_finished():
                break    