from SimulationModules.RequestHandling.InterfaceRequester import InterfaceRequester
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.Enums import Request_state
import pytest

class RequesterWrong(InterfaceRequester):
    pass

class RequesterCorrect(InterfaceRequester):
    def __init__(self):
        self._request: Request = Request()

    @property
    def charging_request(self):
        pass


@pytest.fixture
def my_request():
    return Request()

class TestRequester:

    def test_requester_init_wrong(self):
        with pytest.raises(TypeError):
            requester = RequesterWrong()

    def test_requester_init_correct(self):
        requester = RequesterCorrect()
        assert requester._request is not None
    
    def test_request_confirm(self,
                             my_request: Request):
        my_request.confirm()
        assert my_request.state == Request_state.CONFIRMED

    def test_request_deny(self,
                            my_request: Request):
        my_request.deny()
        assert my_request.state == Request_state.DENIED

    def test_request_charge(self,
                            my_request: Request):
        my_request.set_to_charge()
        assert my_request.state == Request_state.CHARGING

    def test_request_pause(self,
                            my_request: Request):
        my_request.pause()
        assert my_request.state == Request_state.CONFIRMED
        