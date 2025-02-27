from SimulationModules.RequestHandling.RequestHandler import RequestHandler
from SimulationModules.RequestHandling.InterfaceRequester import InterfaceRequester
from SimulationModules.ParkingArea.ParkingArea import ParkingArea

from typing import List

def get_fields_with_parked_vehicle(parking_area: ParkingArea):
    return [field for field in parking_area.parking_area_fields if field.has_parked_vehicle()]

def provide_requests_from_parkingarea_to_request_handler(parking_area: ParkingArea, request_handler: RequestHandler):
    requests = []
    list_of_fields_with_vehicle = get_fields_with_parked_vehicle(parking_area)
    list_of_requesters: List[InterfaceRequester] = [vehicle for vehicle in list_of_fields_with_vehicle if isinstance(vehicle, InterfaceRequester)]
    for requester in list_of_requesters:
        request_handler.add_active_requests(requester.request)
    
