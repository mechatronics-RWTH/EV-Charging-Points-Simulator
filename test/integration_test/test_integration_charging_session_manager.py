import random
import pytest
import datetime

import numpy as np
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ElectricVehicle.Vehicle import ConventionalVehicle
from SimulationModules.Enums import AgentRequestAnswer
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField
from SimulationModules.ParkingArea.ParkingAreaElements import GiniChargingSpot, ChargingSpot,ParkingSpot
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.Gini.Gini import GINI, GiniModes
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingStation.ChargingStation import ChargingStation, CS_modes
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.Batteries.PowerMap import TypeOfChargingCurve
from SimulationModules.Enums import Request_state
from unittest.mock import Mock, MagicMock
from config.logger_config import get_module_logger
from test.SimulationModules.conftest import time_manager

logger = get_module_logger(__name__)

@pytest.fixture
def mock_ev():
    mock_ev = EV(arrival_time=datetime.datetime.now(),
                 stay_duration=datetime.timedelta(minutes=1000),
                 energy_demand=EnergyType(20, EnergyTypeUnit.KWH))
    return mock_ev

@pytest.fixture
def my_parking_area() -> ParkingArea:
    parking_area=MagicMock(spec=ParkingArea)
    parking_area.parking_spot_list =[]
    parking_area.fields_with_chargers =[]
    path="test/Parking_lot_test.txt"
    return parking_area

@pytest.fixture
def my_charging_session_manager(my_parking_area) -> ChargingSessionManager:
    return ChargingSessionManager(parking_area=my_parking_area, 
                                  time_manager=time_manager  )

@pytest.fixture
def start_energy() -> EnergyType:
    return EnergyType(30, EnergyTypeUnit.KWH)

@pytest.fixture
def my_gini(start_energy) -> GINI:
    
    # my_gini_battery=Battery(battery_energy= EnergyType(50, EnergyTypeUnit.KWH),
    #              present_energy=start_energy)
    my_gini_battery=BatteryBuilder().build_battery(
                                        battery_energy=EnergyType(50, EnergyTypeUnit.KWH),
                                        present_energy=start_energy,
                                        maximum_charging_c_rate=1.5,
                                        maximum_discharging_c_rate=1.5)
    my_gini=GINI(battery=my_gini_battery)
    return my_gini 

@pytest.fixture
def mock_charging_station() -> ChargingStation:
    return ChargingStation()

class TestIntegrationChargingSessionManager():

    def test_session_created_with_ev_and_cs(self,
                                            my_charging_session_manager: ChargingSessionManager,
                                            mock_charging_station: ChargingStation,
                                            mock_ev: EV,
                                            ):
        mock_charging_station.is_ready_start_session = MagicMock(return_value=True)
        mock_ev.is_ready_start_session = MagicMock(return_value=True)
        field = MagicMock(spec=InterfaceField)
        field.charger = mock_charging_station
        field.vehicle_parked = mock_ev
        field.has_parked_vehicle.return_value = True
        field.has_charging_station.return_value = True
        field.has_mobile_charging_station.return_value = False
        field.get_parked_vehicle.return_value = mock_ev
        field.get_charger.return_value = mock_charging_station
        participants =my_charging_session_manager.check_for_participants(field)
        assert participants.ev == mock_ev
        assert participants.charger == mock_charging_station


    
    def test_session_created_with_gini_and_cs(self,
                                              my_charging_session_manager: ChargingSessionManager,
                                            mock_charging_station: ChargingStation,
                                            my_gini: GINI,
                                            ):
        mock_charging_station.is_ready_start_session = MagicMock(return_value=True)
        my_gini.is_ready_start_session = MagicMock(return_value=True)
        field = MagicMock(spec=InterfaceField)
        field.charger = mock_charging_station
        field._mobile_charger = my_gini
        field.has_mobile_charging_station.return_value = True
        field.has_charging_station.return_value = True
        field.has_parked_vehicle.return_value = False
        field.get_mobile_charger.return_value = my_gini
        field.get_charger.return_value = mock_charging_station
        participants =my_charging_session_manager.check_for_participants(field)
        assert participants.ev == my_gini
        assert participants.charger == mock_charging_station

    
    def test_session_created_with_gini_and_ev(self,
                                              my_charging_session_manager: ChargingSessionManager,
                                            mock_ev: EV,
                                            my_gini: GINI,
                                            ):
        my_gini.is_ready_start_session = MagicMock(return_value=True)
        mock_ev.is_ready_start_session = MagicMock(return_value=True)
        field = MagicMock(spec=InterfaceField)
        field._mobile_charger = my_gini
        field.vehicle_parked = mock_ev
        field.has_parked_vehicle.return_value = True
        field.has_charging_station.return_value = True
        field.has_charging_station.return_value = False
        field.get_parked_vehicle.return_value = mock_ev
        field.get_mobile_charger.return_value = my_gini
        participants =my_charging_session_manager.check_for_participants(field)
        assert participants.ev == mock_ev
        assert participants.charger == my_gini

    def test_session_created_with_cs_and_gini(self,
                                              my_charging_session_manager: ChargingSessionManager,
                                            mock_charging_station: ChargingStation,
                                            my_gini: GINI,
                                            ):
        my_gini.is_ready_start_session = MagicMock(return_value=True)
        mock_charging_station.is_ready_start_session = MagicMock(return_value=True)
        field = GiniChargingSpot(index=1, position=[0,0])
        field.place_mobile_charger(my_gini)
        field._charger = mock_charging_station
        participants =my_charging_session_manager.check_for_participants(field)
        assert participants.ev == my_gini
        assert participants.charger == mock_charging_station

    def test_session_run_with_cs_and_gini(self, 
                                            my_charging_session_manager: ChargingSessionManager,
                                            mock_charging_station: ChargingStation,
                                            my_gini: GINI,
                                            ):
        my_gini.is_ready_start_session = MagicMock(return_value=True)
        mock_charging_station.is_ready_start_session = MagicMock(return_value=True)
        field = GiniChargingSpot(index=1, position=[0,0])
        field.place_mobile_charger(my_gini)
        field._charger = mock_charging_station
        my_charging_session_manager.charging_session_fields = [field]
        my_charging_session_manager.start_sessions()
        assert len(my_charging_session_manager.active_sessions) == 1
        




    

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_gini_at_charging_station(my_charging_session_manager: ChargingSessionManager,
                                  my_gini: GINI ,
                                  start_energy: EnergyType):   
    

    my_gini_charging_spot =my_charging_session_manager.parking_area._get_field_by_position(position=[8,7])
    assert isinstance(my_gini_charging_spot, GiniChargingSpot)

    assert my_gini.status == GiniModes.IDLE
    assert my_gini_charging_spot.charger.status==CS_modes.IDLE
    assert my_gini_charging_spot.charger.get_power_contribution().value==0

    session = ChargingSession(ev=my_gini, 
                              charging_station=my_gini_charging_spot.charger,
                              field_index=1,
                              departure_time=my_gini.get_departure_time(),
                                global_time=datetime.datetime.now())
    
    session.charging_station.set_target_grid_charging_power(PowerType(10, PowerTypeUnit.KW))
                              
    my_charging_session_manager.start_session(session)
    my_charging_session_manager.active_sessions[0].step(datetime.timedelta(minutes=60))

    assert my_gini.status == GiniModes.CHARGING
    assert my_gini_charging_spot.charger.status==CS_modes.CHARGING_EV
    assert my_gini_charging_spot.charger.get_power_contribution().value<0

    my_charging_session_manager.end_charging_session(position=[8,7])
    assert my_gini.status==GiniModes.IDLE or my_gini.status==GiniModes.MOVING
    assert my_gini_charging_spot.charger.status==CS_modes.IDLE
    assert my_gini_charging_spot.charger.get_power_contribution().value==0

    assert my_gini.battery.present_energy > start_energy
    assert len(my_charging_session_manager.active_sessions)==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_gini_at_charging_station_sessionend_by_field_index(my_charging_session_manager: ChargingSessionManager,
                                                            my_gini: GINI ,
                                                            start_energy: EnergyType):

    
    my_gini_charging_spot=my_charging_session_manager.parking_area._get_field_by_index(index=1)
    assert isinstance(my_gini_charging_spot, GiniChargingSpot)

    assert my_gini.status == GiniModes.IDLE
    assert my_gini_charging_spot.charger.status==CS_modes.IDLE

    session = ChargingSession(ev=my_gini, 
                            charging_station=my_gini_charging_spot.charger,
                            field_index=1,
                            departure_time=my_gini.get_departure_time(),
                            global_time=datetime.datetime.now())
    
    session.charging_station.set_target_grid_charging_power(PowerType(10, PowerTypeUnit.KW))
    my_charging_session_manager.start_session(session)
    my_charging_session_manager.active_sessions[0].step(datetime.timedelta(minutes=60))

    assert my_gini.status == GiniModes.CHARGING
    assert my_gini_charging_spot.charger.status==CS_modes.CHARGING_EV

    my_charging_session_manager.end_charging_session(field_index=1)

    assert my_gini.status == my_gini.status==GiniModes.IDLE or my_gini.status==GiniModes.MOVING
    assert my_gini_charging_spot.charger.status==CS_modes.IDLE

    assert my_gini.battery.present_energy > start_energy
    assert len(my_charging_session_manager.active_sessions)==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_session_end_by_sessionid(my_charging_session_manager: ChargingSessionManager,
                                                            ):
    assert len(my_charging_session_manager.active_sessions)==0
    myGini=GINI(starting_field_index=1)
    myChargingStation=ChargingStation()
    session = ChargingSession(ev=myGini, 
                            charging_station=myChargingStation,
                            field_index=1,
                            departure_time=myGini.get_departure_time(),
                            global_time=datetime.datetime.now())
    my_charging_session_manager.start_session(session)
    assert len(my_charging_session_manager.active_sessions)==1
    my_charging_session_manager.active_sessions[0].step(datetime.timedelta(minutes=60))
    my_charging_session_manager.end_charging_session(session_id=my_charging_session_manager.active_sessions[0].session_id)

    assert len(my_charging_session_manager.active_sessions)==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_session_end_by_ev(my_charging_session_manager: ChargingSessionManager,
                                                            ):

    assert len(my_charging_session_manager.active_sessions)==0
    myGini=GINI(starting_field_index=1)
    myChargingStation=ChargingStation()
    session = ChargingSession(ev=myGini, 
                            charging_station=myChargingStation,
                            field_index=1,
                            departure_time=myGini.get_departure_time(),
                            global_time=datetime.datetime.now())
    my_charging_session_manager.start_session(session)
    assert len(my_charging_session_manager.active_sessions)==1
    my_charging_session_manager.active_sessions[0].step(datetime.timedelta(minutes=60))
    my_charging_session_manager.end_charging_session(ev=myGini)

    assert len(my_charging_session_manager.active_sessions)==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_ev_charged_by_gini(my_charging_session_manager: ChargingSessionManager
                                                            ):

    gini_start_energy=EnergyType(30, EnergyTypeUnit.KWH)
    ev_start_energy=EnergyType(30, EnergyTypeUnit.KWH)
    my_gini_battery=Battery(battery_energy= EnergyType(50, EnergyTypeUnit.KWH),
                 present_energy=gini_start_energy)
    my_ev_battery=Battery(battery_energy= EnergyType(50, EnergyTypeUnit.KWH),
                 present_energy=ev_start_energy)
    my_gini=GINI(battery=my_gini_battery, starting_field_index=1)
    my_ev=EV(arrival_time=datetime.datetime.now(), 
      stay_duration=datetime.timedelta(minutes=1000),
      energy_demand=EnergyType(20, EnergyTypeUnit.KWH),
      battery=my_ev_battery
      )
    assert my_gini.status == GiniModes.IDLE
    assert my_ev.status==  EV_modes.IDLE
    session = ChargingSession(ev=my_ev, 
                            charging_station=my_gini,
                            field_index=1,
                            departure_time=my_ev.get_departure_time(),
                            global_time=datetime.datetime.now())
    my_charging_session_manager.start_session(session)
    my_charging_session_manager.sessions_step(datetime.timedelta(minutes=5))

    assert my_gini.battery.present_energy < gini_start_energy 
    assert my_ev.battery.present_energy > ev_start_energy 
    
    my_charging_session_manager.sessions_step(datetime.timedelta(minutes=5000))
    assert my_gini.battery.present_energy.value>0
    assert my_ev.battery.present_energy.value == 50 

    assert my_gini.status == GiniModes.CHARGING_EV
    assert my_ev.status==  EV_modes.CHARGING

    my_charging_session_manager.end_charging_session(ev=my_ev)

    assert my_gini.status == GiniModes.IDLE
    assert my_ev.status==  EV_modes.IDLE

    assert len(my_charging_session_manager.active_sessions)==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_ev_request_handled_by_gini(mock_ev,
                                    my_charging_session_manager: ChargingSessionManager):
    
    
    #we let the manager look on the parkingarea for evs and making requests if 
    #existing
    my_charging_session_manager.handle_requests()
    #there shouldnt be any by now
    assert len(my_charging_session_manager.active_requests)==0
    assert len(my_charging_session_manager.active_sessions)==0
    
    #now we let one ev park random
    available_field_idx=my_charging_session_manager.parking_area.parking_spot_not_occupied[0].index
    my_charging_session_manager.parking_area.park_new_ev_at_field(mock_ev,
                                field_index=available_field_idx)
    my_charging_session_manager.handle_requests()
    #the manager should have made a request by now, whose state is
    #"REQUESTED"
    field_index=my_charging_session_manager.active_requests[0].field_index
    assert len(my_charging_session_manager.active_requests)==1
    assert len(my_charging_session_manager.active_sessions)==0
    request=my_charging_session_manager.active_requests[0]
    assert request.state==Request_state.REQUESTED

    
    #now we confirm the request via agent:
    request_commands=np.zeros(len(my_charging_session_manager.parking_area.parking_area_fields))
    request_commands[request.field_index]=AgentRequestAnswer.CONFIRM
    my_charging_session_manager.set_request_commands(request_commands)
    my_charging_session_manager.handle_requests()
    assert request.state==Request_state.CONFIRMED

    
    #now we let a gini charge the EV
    gini_start_energy=EnergyType(100, EnergyTypeUnit.KWH)
    my_gini_battery=Battery(battery_energy= EnergyType(100, EnergyTypeUnit.KWH),
                 present_energy=gini_start_energy)
    my_gini=GINI(battery=my_gini_battery,starting_field_index=field_index)


    session = ChargingSession(ev=request.ev, 
                            charging_station=my_gini,
                            field_index=field_index,
                            global_time=datetime.datetime.now(),
                            departure_time=request.ev.get_departure_time())    
    my_charging_session_manager.start_session(session)
    assert len(my_charging_session_manager.active_requests)==1
    assert len(my_charging_session_manager.active_sessions)==1
    assert request.state==Request_state.CHARGING

    #now we end the session again and the request state should switch to 
    #confirmed again because the demanded energy hasnt been delivered yet
    my_charging_session_manager.end_charging_session(field_index=field_index)
    my_charging_session_manager.handle_requests()
    assert len(my_charging_session_manager.active_requests)==1
    assert len(my_charging_session_manager.active_sessions)==0
    assert request.state==Request_state.CONFIRMED

    #now the session is restarted, run for 10 hours and ended then.
    #the state of the request should be "SATISFIED" then

    session = ChargingSession(ev=request.ev, 
                            charging_station=my_gini,
                            field_index=field_index,
                            departure_time=request.ev.get_departure_time(),
                            global_time=datetime.datetime.now()) 
    my_charging_session_manager.start_session(session)
    my_charging_session_manager.active_sessions[0].step(datetime.timedelta(hours=10))
    my_charging_session_manager.end_charging_session(field_index=field_index)
    my_charging_session_manager.handle_requests()
    assert len(my_charging_session_manager.active_requests)==1
    assert len(my_charging_session_manager.active_sessions)==0
    assert request.state==Request_state.SATISFIED

    #now we remove the ev from the parkingLot and the
    my_charging_session_manager.parking_area.remove_vehicle(request.ev)
    logger.info("index: "+str(field_index))
    my_charging_session_manager.handle_requests()
    assert len(my_charging_session_manager.active_requests)==0
    assert len(my_charging_session_manager.active_sessions)==0
    assert len(my_charging_session_manager.request_archive)==1

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_automatic_gini_charging_on_field(my_charging_session_manager: ChargingSessionManager,
                                                            my_gini: GINI ,
                                                            ):


    charging_spot=my_charging_session_manager.parking_area._get_field_by_index(index=1)
    my_charging_session_manager.parking_area.ginis.append(my_gini)   
    assert my_charging_session_manager.get_session_object_by_field_index(index=1) is None
    assert isinstance(charging_spot, GiniChargingSpot)
    assert my_gini.field_index == 1
    assert charging_spot.has_charging_station()
    assert my_gini.status==GiniModes.IDLE
    assert charging_spot.charger.status==CS_modes.IDLE
    my_gini.set_target_field(target_field_index=1)
    #now the cs_manager should be able to find out by itself, that there is an
    #idle giniat a chargingspot that should be charged
    step_time=datetime.timedelta(seconds=120)
    my_charging_session_manager.step(step_time=step_time)

    assert my_gini.status==GiniModes.CHARGING
    assert charging_spot.charger.status==CS_modes.CHARGING_EV

    #now the Gini gets a new target field and wants to leave
    my_gini.set_target_field(target_field_index=2)
    my_gini.update_state()

    assert my_gini.status==GiniModes.INTERRUPTING

    #the cs_manager recognises that and end the session
    step_time=datetime.timedelta(seconds=120)
    my_charging_session_manager.step(step_time=step_time)

    assert my_gini.status==GiniModes.IDLE or my_gini.status==GiniModes.MOVING
    assert charging_spot.charger.status==CS_modes.IDLE

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_start_session_with_ev_and_cs(my_charging_session_manager: ChargingSessionManager,
                                    mock_ev: EV,
                                    ):
    my_charging_session_manager.parking_area.parking_area_fields[1] = ChargingSpot(index=1, position=[0,0])
    my_charging_session_manager.parking_area.update_field_states()
    added_chargingspot = my_charging_session_manager.parking_area._get_field_by_index(index=1)
    assert added_chargingspot in my_charging_session_manager.parking_area.parking_spot_not_occupied
    assert added_chargingspot in my_charging_session_manager.parking_area.parking_spot_with_free_charger
    logger.debug(my_charging_session_manager.parking_area.parking_spot_with_free_charger)
    assert isinstance(my_charging_session_manager.parking_area.parking_area_fields[1], ChargingSpot)
    assert isinstance(my_charging_session_manager.parking_area.parking_area_fields[1], ParkingSpot)
    my_charging_session_manager.parking_area.park_new_ev_at_field(mock_ev,
                                field_index=1)
    assert mock_ev.status==EV_modes.IDLE
    step_time=datetime.timedelta(seconds=120)
    my_charging_session_manager.step(step_time=step_time)
    assert mock_ev.status==EV_modes.CHARGING

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_request_commands_by_agent(mock_ev,
                                    my_charging_session_manager: ChargingSessionManager):
    
    available_field_ids=[field.index for field in my_charging_session_manager.parking_area.parking_spot_not_occupied]
    used_spots=[]
    amount_new_evs=6
    for i in range(amount_new_evs):
        field_index=random.choice(available_field_ids)
        my_charging_session_manager.parking_area.park_new_ev_at_field(mock_ev,
                                field_index=field_index)
        available_field_ids.remove(field_index)
        used_spots.append(field_index)

    my_charging_session_manager.handle_requests()

    assert len(my_charging_session_manager.active_requests) == amount_new_evs
    assert my_charging_session_manager.confirmed_requests_amount_step==0
    assert my_charging_session_manager.denied_requests_amount_step==0

    request_commands=np.zeros(len(my_charging_session_manager.parking_area.parking_area_fields))

    for i in range(amount_new_evs):
        if i<amount_new_evs/2:
            request_commands[used_spots[i]]=AgentRequestAnswer.CONFIRM
        else:
            request_commands[used_spots[i]]=AgentRequestAnswer.DENY

    
    my_charging_session_manager.set_request_commands(request_commands)
    my_charging_session_manager.handle_requests()
    assert len(my_charging_session_manager.active_requests) == amount_new_evs
    assert my_charging_session_manager.confirmed_requests_amount_step==np.count_nonzero(request_commands == AgentRequestAnswer.CONFIRM)
    assert my_charging_session_manager.denied_requests_amount_step==np.count_nonzero(request_commands == AgentRequestAnswer.DENY)

    my_charging_session_manager.handle_requests()
    assert len(my_charging_session_manager.active_requests) == amount_new_evs
    assert my_charging_session_manager.confirmed_requests_amount_step==0
    assert my_charging_session_manager.denied_requests_amount_step==0

@pytest.mark.skip(reason="Needs to be double checked after intensive refactoring")
def test_step_time_advances(my_charging_session_manager: ChargingSessionManager):
    step_time=datetime.timedelta(seconds=120)
    current_time=my_charging_session_manager.time
    my_charging_session_manager.step(step_time=step_time)
    assert my_charging_session_manager.time == current_time+step_time

#TODO test this thoughly
@pytest.mark.skip(reason="No tests in place yet")
def test_start_sessions(my_charging_session_manager: ChargingSessionManager,
                        mock_ev: EV):
    raise NotImplementedError   

