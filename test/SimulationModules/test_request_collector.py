from SimulationModules.RequestHandling.RequestCollector import InterfaceRequestCollector, RequestCollector
from SimulationModules.RequestHandling.Request import Request
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def request_collector():
    return RequestCollector()

@pytest.fixture
def my_request():
    return MagicMock(spec=Request)


class TestRequestCollector:

    def test_init(self):
        request_collector = RequestCollector()
        assert isinstance(request_collector, InterfaceRequestCollector)

    def test_add_request(self,
                         request_collector: RequestCollector,
                         my_request: Request):

        request_collector.add_request(my_request)
        assert len(request_collector.active_requests) == 1

    def test_add_request_multiple(self,
                         request_collector: RequestCollector,
                         ):
        request_collector.active_requests = []
        request1 = Request()
        request2 = Request()
        request_collector.add_request(request1)
        request_collector.add_request(request2)
        assert len(request_collector.active_requests) == 2

    def test_add_request_duplicate(self,
                            request_collector: RequestCollector,
                            my_request: Request):
    
            request_collector.add_request(my_request)
            with pytest.raises(ValueError):
                request_collector.add_request(my_request)

    def test_add_request_wrong_type(self,
                            request_collector: RequestCollector,
                            my_request: Request):

            with pytest.raises(TypeError):
                request_collector.add_request("my_request")
    
    def test_get_requests(self,
                         request_collector: RequestCollector,
                         my_request: Request):

        request_collector.active_requests = [Request() for _ in range(3)]
        assert len(request_collector.get_requests()) == 3

    def test_remove_request(self,
                            request_collector: RequestCollector,
                            my_request: Request):

        request_collector.active_requests = [my_request]
        request_collector.remove_request(my_request)
        assert len(request_collector.active_requests) == 0

    def test_remove_request_not_found(self,
                            request_collector: RequestCollector,
                            my_request: Request):
        request1 = Request()
        request_collector.active_requests = [my_request]
        with pytest.raises(ValueError):
            request_collector.remove_request(request1)


