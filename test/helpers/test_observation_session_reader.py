import pytest
from helpers.DataAnalyzer.ObservationSessionReader import ObservationSessionReader
from helpers.DataAnalyzer.DataAnalyzer import EvSessionPeriod
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit

@pytest.fixture
def user_request():
    user_requests = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
                 [], [], [], [], [], [], [], [], [[16, 1]], [[16, 2]], [[16, 2]], [[16, 4]], [[16, 4]], [[16, 4]], [[16, 4]], [[16, 4]], 
                 [[16, 4]], [[16, 4]], [[16, 5]], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
                 [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [[20, 1]], [[20, 2]], [[20, 2]], [[20, 4]], [[14, 1], 
                [20, 4]], [[14, 2], [20, 5]]]
    return user_requests

@pytest.fixture
def energy_request():
    energy_requests = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [[16.0, 152564003.251509]], [[16.0, 152564003.251509]], [[16.0, 152564003.251509]], 
    [[16.0, 149264003.251509]], [[16.0, 145964003.25150904]], [[16.0, 142664003.25150907]], [[16.0, 139364003.25150907]], 
    [[16.0, 136064003.25150907]], [[16.0, 132764003.25150909]], [[16.0, 129464003.2515091]], [[16.0, 126164003.2515091]], [], [], 
    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
    [], [], [], [[20.0, 77758107.10796835]], [[20.0, 77758107.10796835]], [[20.0, 77758107.10796835]], [[20.0, 74458107.10796836]], 
    [[14.0, 98069997.13681188], [20.0, 71158107.10796838]], [[14.0, 98069997.13681188], [20.0, 67858107.10796838]]]
    return energy_requests


@pytest.fixture
def observation_session_reader(user_request: list, energy_request: list):
    return ObservationSessionReader(user_requests=user_request, energy_requests=energy_request)


class TestObservationSessionReader:

    def test_init(self):
        observation_session_reader = ObservationSessionReader()
        assert observation_session_reader.user_requests == []
        assert observation_session_reader.energy_requests == []


    def test_set_user_requests(self, user_request: list):
        observation_session_reader = ObservationSessionReader()
        observation_session_reader.set_user_requests(user_request)
        assert observation_session_reader.user_requests == user_request

    
    def test_set_energy_requests(self, energy_request: list):
        observation_session_reader = ObservationSessionReader()
        observation_session_reader.set_energy_requests(energy_request)
        assert observation_session_reader.energy_requests == energy_request
    
    def test_set_active_requests(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.set_active_requests(0)
        assert observation_session_reader.active_energy_requests == []
        assert observation_session_reader.active_user_requests == []

    def test_set_active_requests_non_empty(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.set_active_requests(40)
        assert len(observation_session_reader.active_energy_requests) >0
        assert len(observation_session_reader.active_user_requests) >0

    def test_end_session_if_no_requests(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        observation_session_reader.step = step
        #observation_session_reader.ev_session_periods= 
        observation_session_reader.active_user_requests = [[4 ,5],[1, 1]]
        observation_session_reader.end_session_if_no_request(ev_session=ev_session)
        assert ev_session.end_index == step- 1
    

    def test_end_session_if_request_below_last_status(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.status = [1, 2, 4, 4, 4]
        observation_session_reader.step = step
        #observation_session_reader.ev_session_periods= 
        observation_session_reader.active_user_requests = [[4 ,5],[3, 1]]
        observation_session_reader.active_energy_requests = [[4 ,15*3600*1000],[3, 15*3600*1000]]
        observation_session_reader.end_session_if_request_below_last_status(ev_session=ev_session)
        assert ev_session.end_index == step- 1

    def test_end_session_if_request_satisfied(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.status = [1, 2, 4, 4, 4]
        observation_session_reader.step = step
        #observation_session_reader.ev_session_periods= 
        observation_session_reader.active_user_requests = [[4 ,5],[3, 5]]
        observation_session_reader.active_energy_requests = [[4 ,15*3600*1000],[3, 15*3600*1000]]
        observation_session_reader.end_session_if_request_satisfied(ev_session=ev_session)
        assert ev_session.end_index == step

    def test_end_session_if_request_satisfied_additional_request(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.status = [1, 2, 4, 4, 4]
        ev_session.energy_request = [EnergyType(0),
                                        EnergyType(0),
                                        EnergyType(0),
                                        EnergyType(0),
                                        EnergyType(0)]
        energy_request_length = len(ev_session.energy_request)
        status_length = len(ev_session.status)
        observation_session_reader.step = step
        #observation_session_reader.ev_session_periods= 
        observation_session_reader.active_user_requests = [[4 ,5],[3, 5]]
        observation_session_reader.active_energy_requests = [[4 ,15*3600*1000],[3, 15*3600*1000]]
        observation_session_reader.end_session_if_request_satisfied(ev_session=ev_session)
        assert len(ev_session.status) == status_length + 1
        assert len(ev_session.energy_request) == energy_request_length + 1

    def test_check_for_session_end_satisfied(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.status = [1, 2, 4, 4, 4]
        observation_session_reader.step = step
        observation_session_reader.active_user_requests = [[4 ,5],[3, 5]]
        observation_session_reader.active_energy_requests = [[4 ,15*3600*1000],[3, 15*3600*1000]]
        observation_session_reader.check_for_session_end(ev_session)
        assert ev_session.end_index == step

    def test_check_for_session_end_no_request(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.status = [1, 2, 4, 4, 4]
        observation_session_reader.step = step
        observation_session_reader.active_user_requests = [[4 ,5]]
        observation_session_reader.active_energy_requests = [[4 ,15*3600*1000],[3, 15*3600*1000]]
        observation_session_reader.check_for_session_end(ev_session)
        assert ev_session.end_index == step-1

    def test_add_data_to_session(self, observation_session_reader: ObservationSessionReader):
        step = 5
        ev_session = EvSessionPeriod(id=0, start_index=0, field_index=3)
        ev_session.energy_request = [EnergyType(EnergyTypeUnit.KWH, 10), 
                                     EnergyType(EnergyTypeUnit.KWH, 20),
                                     EnergyType(EnergyTypeUnit.KWH, 30)]
        ev_session.status = [1, 2, 4]
        observation_session_reader.step = step
        observation_session_reader.active_user_requests = [[3 ,4]]
        observation_session_reader.active_energy_requests = [[3 ,15*3600*1000]]
        observation_session_reader.add_data_to_session(ev_session)
        assert len(ev_session.energy_request) == 4
        assert len(ev_session.status) == 4
        assert ev_session.energy_request[-1] == EnergyType(15,EnergyTypeUnit.KWH)
        assert ev_session.status[-1] == 4

    def test_update_active_sessions(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.ev_session_periods = [EvSessionPeriod(id=0, start_index=0, field_index=1),
                                                        EvSessionPeriod(id=1, start_index=0, field_index=2)]
        observation_session_reader.update_active_sessions()
        assert len(observation_session_reader.active_ev_sessions) == 2
    
    def test_update_active_sessions_session_has_end(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.ev_session_periods = [EvSessionPeriod(id=0, start_index=0, field_index=1),
                                                        EvSessionPeriod(id=1, start_index=0, field_index=2)]
        observation_session_reader.ev_session_periods[0].end_index = 5
        observation_session_reader.update_active_sessions()
        assert len(observation_session_reader.active_ev_sessions) == 1


    def test_start_new_sessions(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.active_fields = [1, 2, 3, 4, 5]
        observation_session_reader.active_ev_sessions = [EvSessionPeriod(id=0, start_index=0, field_index=1),
                                                        EvSessionPeriod(id=1, start_index=0, field_index=2)]
        observation_session_reader.active_energy_requests = [[1 ,15*3600*1000],
                                                             [2, 15*3600*1000],
                                                             [3, 15*3600*1000],
                                                                [4, 15*3600*1000],
                                                                [5, 15*3600*1000]]
        observation_session_reader.active_user_requests = [[1 ,5],
                                                              [2, 5],
                                                                [3, 5],
                                                                [4, 5],
                                                                [5, 5]]
        
        observation_session_reader.start_sessions()
        assert len(observation_session_reader.active_ev_sessions) == 5
        assert observation_session_reader.ev_session_periods[-1].field_index == 5
        assert observation_session_reader.ev_session_periods[-1].id == 4

    def test_start_new_sessions_new_fields(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.active_fields = [1, 2]
        observation_session_reader.fields_of_active_sessions = []
        observation_session_reader.active_energy_requests = [[1 ,15*3600*1000],[2, 15*3600*1000]]
        observation_session_reader.active_user_requests = [[1 ,5],
                                                              [2, 5],]
        observation_session_reader.start_sessions()
        assert len(observation_session_reader.active_ev_sessions) == 2

    def test_start_new_sessions_no_new_fields_based_on_sessions(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.active_fields = [1, 2]
        observation_session_reader.ev_session_periods = [EvSessionPeriod(id=0, start_index=0, field_index=1),
                                                        EvSessionPeriod(id=1, start_index=0, field_index=2)]
        observation_session_reader.update_active_sessions()       
        observation_session_reader.start_sessions()        
        assert len(observation_session_reader.active_ev_sessions) == 2

    def test_read_sessions_from_requests(self, observation_session_reader: ObservationSessionReader):
        observation_session_reader.read_sessions_from_requests()
        
        assert len(observation_session_reader.ev_session_periods) ==3
        assert len(observation_session_reader.active_ev_sessions) == 1

        

    



    

