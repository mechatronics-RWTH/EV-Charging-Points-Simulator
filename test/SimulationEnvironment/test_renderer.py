import pytest
from SimulationEnvironment.Renderer.Renderer import PygameRenderer
from SimulationEnvironment.GymEnvironment import CustomEnv
from unittest.mock import MagicMock, Mock
from SimulationModules.ParkingArea.ParkingAreaElements import(Obstacle,
    ParkingPath,
    ParkingSpot,
    GiniChargingSpot)
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ElectricVehicle.EV import EV 
from SimulationModules.Gini.Gini import GINI
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.Enums import Request_state
import time
import pygame


@pytest.fixture()
def mock_gini():
    mock_gini = Mock(wraps=GINI)
    mock_gini.get_soc.return_value = 0.5
    return mock_gini

@pytest.fixture()
def mock_parking_area(mock_gini) -> ParkingArea:
    mock_parking_area = Mock(wraps=ParkingArea)
    mock_parking_area.parking_area_size = (10, 10)
    mock_parking_area.get_gini_by_field_index.return_value = mock_gini
    
    return mock_parking_area

@pytest.fixture()
def mock_charging_session_manager():
    charging_session_manager = Mock(spec=ChargingSessionManager)
    charging_session_manager.get_request_object_by_field_index.return_value = Request_state.REQUESTED
    return charging_session_manager

@pytest.fixture()
def mock_custom_env(mock_parking_area,mock_charging_session_manager):
    mock_env = Mock(wraps=CustomEnv)
    mock_env.parking_area = mock_parking_area
    mock_env.charging_session_manager = mock_charging_session_manager
    return mock_env


#@pytest.fixture()
def mock_obstacle_field():
    return Obstacle(position=(0, 0), index=0)

#@pytest.fixture()
def mock_parking_path_field():
    return ParkingPath(position=(0, 0), index=0)


#@pytest.fixture()
def mock_parking_spot_field():

    parking_spot = ParkingSpot(position=(0, 0), index=0)
    mock_ev = MagicMock(spec=EV)
    mock_ev.get_soc.return_value = 0.5
    parking_spot.vehicle_parked = mock_ev
    return parking_spot

#@pytest.fixture()
def mock_gini_charging_spot_field():
    
    return GiniChargingSpot(position=(0, 0), index=0)



@pytest.mark.skip('Renderer tests are not yet implemented')
@pytest.mark.parametrize("field", [mock_obstacle_field(),
                                   mock_parking_path_field(), 
                                   mock_parking_spot_field(), 
                                   mock_gini_charging_spot_field()])
def test_create_parking_area_field_based_on_type_obstacle(mock_custom_env,
                                                          field):
    mock_renderer = PygameRenderer(render_environment= mock_custom_env)
    mock_renderer.x = 0
    mock_renderer.y = 0
    mock_renderer._create_parking_area_field_based_on_type(field=field)



@pytest.mark.skip('Renderer tests are not yet implemented')
@pytest.mark.parametrize("field", [mock_obstacle_field(),
                                   mock_parking_path_field(), 
                                   mock_parking_spot_field(), 
                                   mock_gini_charging_spot_field()])
def test_create_soc_bar(mock_custom_env,
                        field):
    mock_renderer = PygameRenderer(render_environment= mock_custom_env)
    mock_renderer.x = 0
    mock_renderer.y = 0
    mock_renderer._create_soc_bar(field)

    # Add assertion here
@pytest.mark.skip('Renderer tests are not yet implemented')
@pytest.mark.parametrize("field", [mock_obstacle_field(),
                                   mock_parking_path_field(), 
                                   mock_parking_spot_field(), 
                                   mock_gini_charging_spot_field()])
def test_create_gini_icons(mock_custom_env,
                        field):
    mock_renderer = PygameRenderer(render_environment= mock_custom_env)
    mock_renderer.x = 0
    mock_renderer.y = 0
    mock_renderer._create_gini_icons(field)
    # Add assertion here

@pytest.mark.skip('Renderer tests are not yet implemented')
@pytest.mark.parametrize("field", [mock_obstacle_field(),
                                   mock_parking_path_field(), 
                                   mock_parking_spot_field(), 
                                   mock_gini_charging_spot_field()])
def test_show_request_status(mock_custom_env,
                        field):
    mock_renderer = PygameRenderer(render_environment= mock_custom_env)
    mock_renderer.x = 0
    mock_renderer.y = 0
    mock_renderer._show_request_status(field)
    # Add assertion here

# def test_get_soc_bar(mock_renderer):
#     soc = 0.5
#     mock_renderer._get_soc_bar(soc)
#     # Add assertion here

# def test_assign_icons(mock_renderer):
#     mock_renderer._assign_icons()
#     # Add assertion here

# def test_define_area_sizing(mock_renderer):
#     screen_width = 1000
#     parking_area_screen_height = 450
#     supermarket_screen_height = 100
#     mock_renderer._define_area_sizing(screen_width, parking_area_screen_height, supermarket_screen_height)
#     # Add assertion here

# def test_render(mock_renderer):
#     mock_renderer.render()
#     # Add assertion here

# def test_render_parking_area(mock_renderer):
#     mock_renderer._render_parking_area()
#     # Add assertion here