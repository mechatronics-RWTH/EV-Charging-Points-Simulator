from abc import ABC, abstractmethod
import numbers
from SimulationEnvironment.GymEnvironment import CustomEnv
import pygame
from SimulationModules.ParkingArea.ParkingAreaElements import(
    Field,
    ParkingSpot,
    GiniChargingSpot,
    Obstacle,
    ParkingPath,
    ChargingSpot

)
import math 
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Gini.Gini import GINI
from SimulationModules.RequestHandling.Request import Request_state
from config.logger_config import get_module_logger
from config.definitions import ROOT_DIR
import pathlib
from typing import List
import numpy as np
from SimulationEnvironment.Renderer.ArrowToRender import ArrowToRender
from SimulationEnvironment.Renderer.ObjectToRender import ObjectToRender
import imageio
import os
from SimulationEnvironment.Renderer.VideoCreator import VideoCreator, InterfaceVideoCreator
from matplotlib import image

logger = get_module_logger(__name__)
relativePathCar =pathlib.Path(r"SimulationEnvironment/image/EV_pictogram.png")
FILEPATH = pathlib.Path(ROOT_DIR).joinpath(relativePathCar)
car_logo = image.imread(FILEPATH)

logo_building = pygame.image.load(pathlib.Path(ROOT_DIR) / "SimulationEnvironment" / "image" / "Building" / "Building.png")
logo_grid = pygame.image.load(pathlib.Path(ROOT_DIR) / "SimulationEnvironment" / "image" / "Local_Grid_pic_v2.png")
logo_PV = pygame.image.load(pathlib.Path(ROOT_DIR) / "SimulationEnvironment" / "image" / "PV_Array.svg")
logo_charger = pygame.image.load(pathlib.Path(ROOT_DIR) / "SimulationEnvironment" / "image" / "ChargingStation" / "Charging_Station_MMP.png")
logo_stationary_battery = pygame.image.load(pathlib.Path(ROOT_DIR) / "SimulationEnvironment" / "image" / "StationaryStorage" / "StationaryStorage.png")

parking_spot_logo = pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/ParkingSpot_v3.png")))
charging_spot_logo = pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment\\image\\ChargingStation\\Charging_Station_MMP_only_GINI.png")))
obstacle_logo = pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Obstacle/tree-1578.png")))
path_logo = pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Path.jpg")))
ev_logo =  pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(relativePathCar))
gini_logo = pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Gini_pictogram.png")))

def get_field_by_position(position: List[int],
                          parking_area) -> Field:
    return next((field for field in parking_area.parking_area_fields if field.position == position), None)


class InterfaceRenderer(ABC):
         
    @abstractmethod
    def __init__(self, render_environment: CustomEnv):
        pass
     
    @abstractmethod
    def render(self, close: bool=False):
        pass

class Renderer(InterfaceRenderer):
    def __init__(self, render_environment: CustomEnv):
        self.render_environment=render_environment



class PygameRenderer(Renderer):

    def __init__(self,
                 render_environment: CustomEnv,
                 screen_width: int=1000,
                 parking_area_screen_height: int=450,
                 SUPERMARKET_SCREEN_HEIGTH: int=300,
                 supermarket_screen_width_share: numbers.Number = 0.6,
                 video_path = None,
                 ):
        super().__init__(render_environment)
        pygame.init()
        self.field_border_width =1
        
        self._define_area_sizing(screen_width, parking_area_screen_height, SUPERMARKET_SCREEN_HEIGTH)

        self._define_colors()        
        self._assign_icons()
        self.screen=pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))
        self.screen.fill(self.colors["white"])
        self.pygame_initialized=True
        self.text_size = 25
        self._render_parking_area()
        self._render_power_consumers()
        if video_path:
            self.video_creator: InterfaceVideoCreator = VideoCreator(filepath=video_path)
            self.frame_number = 0
        else:
            self.video_creator = None
      
    def render(self, close:bool =False):

        if close:
            self.save_video()
            pygame.quit()
            return
        self._render_parking_area()
        self._draw_power_arrows()
        self.update_time()
        self.update_stationary_storage()

        #region update display
        
        pygame.display.update()
        self.create_video_frames()

    def create_video_frames(self):
        if self.video_creator:
            self.video_creator.add_frame(frame = pygame.surfarray.array3d(self.screen))
            self.frame_number +=1


    def save_video(self):
        self.video_creator.save_video()
        logger.info(f"Video saved at {self.video_creator.fullfilename}")






    def _render_parking_area(self):
        
        
        pygame.draw.rect(self.screen, 
                            self.colors["white"], 
                            (0, self.SUPERMARKET_SCREEN_HEIGTH, 
                            self.SCREEN_WIDTH, self.PARKING_SCREEN_HEIGHT))
                    
        for field in self.render_environment.parking_area.parking_area_fields:
            
            self.x=self.parking_area_field_width*field.position[0]
            self.y=self.SUPERMARKET_SCREEN_HEIGTH+ self.parking_area_field_heigth*field.position[1]
            self._create_parking_area_field_based_on_type(field)

        self._create_ev()
        self._create_gini_icons()

    def _render_power_consumers(self):
        self.SUPERMARKET_SCREEN_HEIGTH
        self.SUPERMARKET_SCREEN_WIDTH 
        
        self.grid_consumers_rendering = ObjectToRender(name = "grid_consumers",
                                                       screen= self.screen,
                                                    x_midpoint = 70,
                                                    y_midpoint= 50,
                                                    height= 100,
                                                    width=60,
                                                    logo= logo_grid)
        

        
        self.building_consumers_rendering = ObjectToRender(name = "building_consumers",
                                                           screen= self.screen,
                                                        x_midpoint= 300,
                                                        y_midpoint = 70,
                                                        height= 140,
                                                        width=140,
                                                        logo = logo_building)
        
        self.pv_consumers_rendering = ObjectToRender(name = "pv_consumers",
                                                     screen= self.screen,
                                                x_midpoint= 600,
                                                y_midpoint= 40,
                                                height= 80,
                                                width=80,
                                                logo = logo_PV)
        try:
            stat_soc=self.render_environment.observation_raw["soc_stat_battery"][0]
        except Exception as e:
            stat_soc = None
            logger.error(e)
        self.stationary_storage = ObjectToRender(name = "stationary_storage",
                                                    screen= self.screen,
                                                    x_midpoint= 600,
                                                    y_midpoint= 120,
                                                    height= 50,
                                                    width=40,
                                                    logo = logo_stationary_battery,
                                                    soc=stat_soc)
        
        grid_build_x_midpoint = self.grid_consumers_rendering.x_end + (self.building_consumers_rendering.x_start- self.grid_consumers_rendering.x_end)/2
        self.grid_building_arrow = ArrowToRender(self.screen, 
                                            x_midpoint=grid_build_x_midpoint,
                                            y_midpoint=self.grid_consumers_rendering.y_midpoint, 
                                            length=100, 
                                            max_length=100, 
                                            point_direction='r', 
                                            arrow_width=30,)
        build_pv_x_midpoint = self.building_consumers_rendering.x_end + (self.pv_consumers_rendering.x_start- self.building_consumers_rendering.x_end)/2
        self.pv_building_arrow = ArrowToRender(self.screen, 
                                            x_midpoint=build_pv_x_midpoint,
                                            y_midpoint=self.pv_consumers_rendering.y_midpoint, 
                                            length=100, 
                                            max_length=100, 
                                            point_direction='l', 
                                            arrow_width=30,)
        
        self.building_charging_arrow = ArrowToRender(self.screen, 
                                    x_midpoint=self.building_consumers_rendering.x_midpoint,
                                    y_midpoint=self.building_consumers_rendering.y_end+60, 
                                    length=80, 
                                    max_length=80, 
                                    point_direction='u', 
                                    arrow_width=30,)
        
        self.building_storage_arrow = ArrowToRender(self.screen, 
                            x_midpoint=build_pv_x_midpoint,
                            y_midpoint=self.stationary_storage.y_midpoint, 
                            length=100, 
                            max_length=100, 
                            point_direction='r', 
                            arrow_width=30,)
        

        
        self.grid_consumers_rendering.create()
        self.building_consumers_rendering.create()
        self.pv_consumers_rendering.create()
        if self.render_environment.observation_raw["soc_stat_battery"] is not None:
            self.stationary_storage.create()
                                                      

    def update_stationary_storage(self):
        if self.render_environment.observation_raw["soc_stat_battery"] is not None:
            soc = self.render_environment.observation_raw["soc_stat_battery"][0]
            self.stationary_storage.update_soc(soc)


    def _draw_power_arrows(self):
        self._draw_grid_power_arrow()
        self._draw_pv_power_arrow()
        self._draw_cs_power_arrow()
        if self.render_environment.local_grid.stationary_battery is not None:
            #pass
            self._draw_stationary_storage_arrow()


    def _draw_grid_power_arrow(self):
        grid_power = self.render_environment.observation_raw["grid_power"][0]/1000
        
        if grid_power < 0:
            direction = 'r'
            absolute_grid_power = grid_power*(-1)
        else:
            direction = 'l'
            absolute_grid_power = grid_power
        max_grid_pwr = self.render_environment.raw_env_space_manager.max_grid_power
        max_grid_pwr =100
        length = np.min([100 * absolute_grid_power/max_grid_pwr, 100])
        length = np.max([length, 20])

        txt = f"Grid Power = {round(absolute_grid_power,1) } kW"
        self.grid_building_arrow.add_text(txt, text_size=14)
        self.grid_building_arrow.set_pointing_direction(direction)
        self.grid_building_arrow.update(length)

    def _draw_pv_power_arrow(self):
        pv_power = self.render_environment.observation_raw["pv_power"][0]/1000
        max_pv_power = 30
        max_length = self.pv_building_arrow.max_length
        length = np.min([max_length * pv_power/max_pv_power, max_length])
        length = np.max([length, 20])
        self.pv_building_arrow.add_text(f"PV Power = {round(pv_power,1)} kW", text_size=14)
        self.pv_building_arrow.update(length)

    def _draw_cs_power_arrow(self):      
        length =50
        direction = 'u'
        cs_power = 0
        cs_power = sum(x for x in self.render_environment.observation_raw["cs_charging_power"] if x is not None)/1000
        max_length=100
        max_cs_power = 300
        length = np.min( [max_length, max_length * cs_power/max_cs_power])
        length = np.max([length, 20])
        self.building_charging_arrow.add_text(f"Charging Power = {round(cs_power,1)} kW", text_size=14)
        self.building_charging_arrow.set_pointing_direction(direction)
        self.building_charging_arrow.update(length)

    def _draw_stationary_storage_arrow(self):
        stat_batt_power = self.render_environment.observation_raw["stat_batt_power"][0]/1000
        length =50
        if stat_batt_power < 0:
            direction = 'l'
            absolute_stat_batt_power = stat_batt_power*(-1)
        else:
            direction = 'r'
            absolute_stat_batt_power = stat_batt_power
        max_length=100
        max_statt_batt_power = 100
        length = np.min( [max_length, max_length * absolute_stat_batt_power/max_statt_batt_power])
        length = np.max([length, 20])
        self.building_storage_arrow.add_text(f"ESS Power = {round(absolute_stat_batt_power,1)} kW", text_size=14)

        self.building_storage_arrow.set_pointing_direction(direction)
        self.building_storage_arrow.update(length)
        stat_soc=self.render_environment.observation_raw["soc_stat_battery"][0]

       

    def update_time(self):
        pos = (700, 20)
        pygame.draw.rect(self.screen, (255,255,255), (pos[0], pos[1]-100, pos[0]+100,pos[1]+100))
        font = pygame.font.Font(None, 32)
        text = font.render(f"{self.render_environment.time_manager.get_current_time()}", True, (0, 0, 0))
        self.screen.blit(text, pos)


    
    def _create_parking_area_field_based_on_type(self, field: Field):
            try:
                 
                self.screen.blit(self.type_to_icon_mapping[type(field)], (self.x,self.y))
            except KeyError:
                raise KeyError(f"Field type {type(field)} not supported")

    def _create_ev(self):
        fields_with_ev: List[ParkingSpot] = self.render_environment.parking_area.get_fields_with_parked_vehicle()
        shift = 0 #0.7 * self.parking_area_field_width 
        for field in fields_with_ev:
            self.x=self.parking_area_field_width*field.position[0]
            self.y=self.SUPERMARKET_SCREEN_HEIGTH+ self.parking_area_field_heigth*field.position[1]                               
            #paint vehicles and their soc
            if not isinstance(field.vehicle_parked, EV):
                continue 
            else:
                soc = field.vehicle_parked.get_soc()
                soc_demand=  field.vehicle_parked.soc_demand     

            self.screen.blit(self.scaled_images["ev_logo"], (self.x, self.y))
            #and the loading bar:
            self._get_soc_bar(soc, shift=shift, soc_demand=soc_demand)
            self._show_request_status(field)

    def _create_gini_icons(self):
        shift= 0 # To not overlap gini and vehicle/charging station
        fields_with_gini = [gini.get_current_field() for gini in self.render_environment.gini_mover.ginis]
        for field in fields_with_gini:
            self.x=self.parking_area_field_width*field.position[0]
            self.y=self.SUPERMARKET_SCREEN_HEIGTH+ self.parking_area_field_heigth*field.position[1]
            gini = field.get_mobile_charger()   
            soc = gini.get_soc()
            self._apply_shift(field)                   

            self.screen.blit(self.scaled_images["gini_logo"], (self.x+shift,self.y))
            self._get_soc_bar(soc, shift=shift)

    def _apply_shift(self,field: ParkingSpot, shift_factor: numbers.Number=0.7):
        if field.has_parked_vehicle() or field.has_charging_station():
            shift = -shift_factor*self.parking_area_field_width # Usually we place the GINI to the left if the field is not occupied
            if field.position[0]== 0: # if the vehicle is parked on the very left side
                shift = shift*(-1)

            else:
                position = [field.position[0]-1,field.position[1]]
                field_to_the_left = get_field_by_position(position=position, parking_area=self.render_environment.parking_area)
                if isinstance(field_to_the_left,ParkingSpot) or isinstance(field_to_the_left,GiniChargingSpot): # if the field to the left is occupied
                    shift = shift*(-1)
            self.x=self.parking_area_field_width*field.position[0]+shift
             
    def _show_request_status(self, field: Field):
        self.x=self.parking_area_field_width*field.position[0]
        self.y=self.SUPERMARKET_SCREEN_HEIGTH+ self.parking_area_field_heigth*field.position[1]   
        if not field.has_parked_vehicle():
            return
        field_request= next((request for request in self.render_environment.parking_area.request_collector.active_requests if request.field_index == field.index), None)
        
        if field_request is not None:
            field_request_state = field_request.state
            req_param=self.request_to_icon_mapping[field_request_state]
            
            self.screen.blit(pygame.font.Font(None, self.text_size).render(req_param[0], True, req_param[1]), 
                             (self.x+0.1*self.parking_area_field_width,self.y))    

    def _get_soc_bar(self, 
                     soc: numbers.Number, 
                     shift: int=0,
                     soc_demand= None):
        (bar_height, bar_width)=(self.parking_area_field_heigth*0.7,self.parking_area_field_width*0.3)
        pygame.draw.rect(self.screen, self.colors["white"], (self.x+shift, self.y, bar_width, bar_height))                
        fill_height = int(soc * bar_height)
        pygame.draw.rect(self.screen,  self.colors["green"], (self.x+shift, int(self.y+bar_height*(1-soc)), bar_width, fill_height))
        if soc_demand is not None:
            demand_y = int(self.y + bar_height * (1 - soc_demand))
            pygame.draw.line(self.screen, self.colors["blue"], 
                            (self.x + shift, demand_y), 
                            (self.x + shift + bar_width, demand_y), 2)



    def _assign_icons(self):
        self.scaled_images={
            "parking_spot_logo" : pygame.transform.scale(parking_spot_logo,self.parking_area_field_size),
            "charging_spot_logo" : pygame.transform.scale(charging_spot_logo,self.parking_area_field_size),
            "obstacle_logo" : pygame.transform.scale(obstacle_logo,self.parking_area_field_size),
            "path_logo" : pygame.transform.scale(path_logo,self.parking_area_field_size),
            "gini_logo" : pygame.transform.scale(gini_logo,self.parking_area_field_size),
            "ev_logo" : pygame.transform.scale(ev_logo,self.parking_area_field_size),

        }

        self.type_to_icon_mapping={ParkingSpot: self.scaled_images["parking_spot_logo"],
                                   GiniChargingSpot: self.scaled_images["charging_spot_logo"],
                                   Obstacle: self.scaled_images["obstacle_logo"],
                                   ParkingPath: self.scaled_images["path_logo"],
                                   GINI: self.scaled_images["gini_logo"],
                                   EV: self.scaled_images["ev_logo"],
                                   ChargingSpot:pygame.transform.scale(logo_charger,self.parking_area_field_size),
        }
        self.request_to_icon_mapping={Request_state.REQUESTED: ["RE", self.colors["black"]],
                                Request_state.CONFIRMED: ["CO", self.colors["green"]],
                                Request_state.DENIED: ["DE", self.colors["red"]],
                                Request_state.CHARGING: ["CH", self.colors["blue"]],
                                Request_state.SATISFIED: ["SA", self.colors["white"]],}

    def _define_area_sizing(self,
                            screen_width: int,
                            parking_area_screen_height: int,
                            SUPERMARKET_SCREEN_HEIGTH: int,
                            supermarket_width_share: float =0.6):
        self.SCREEN_WIDTH=screen_width
        self.SCREEN_HEIGHT=parking_area_screen_height + SUPERMARKET_SCREEN_HEIGTH
        self.PARKING_SCREEN_HEIGHT = parking_area_screen_height
        self.SUPERMARKET_SCREEN_HEIGTH = SUPERMARKET_SCREEN_HEIGTH
        self.SUPERMARKET_SCREEN_WIDTH = self.SCREEN_WIDTH *supermarket_width_share
        self.parking_area_fields_x= self.render_environment.parking_area.parking_area_size[0]
        self.parking_area_fields_y= self.render_environment.parking_area.parking_area_size[1]
        self.screen=pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))


        self.parking_area_field_width=self.SCREEN_WIDTH/ self.parking_area_fields_x
        self.parking_area_field_heigth=self.PARKING_SCREEN_HEIGHT/self.parking_area_fields_y
        self.parking_area_field_size = (self.parking_area_field_width,self.parking_area_field_heigth)


    def _define_colors(self):
        self.colors = {"field_bg_color": (255,255,255),
                       "gini_charging_spot_Color": (109,55,200),
                       "parking_spot_color": (200,200,200),
                       "obstacle_color": (1,1,1),
                       "path_color": (80,80,80),
                       "vehicle_color": (44,200,11),
                       "gini_color": (255,100,0),
                       "field_border_color": (255,255,255),
                       "green": (0, 255, 0),
                       "red": (255,0,0),
                       "blue": (0,0,255),
                       "black": (0,0,0),
                       "white": (255,255,255),
                       }

    def render_salabim(close: bool=False):
        raise NotImplementedError