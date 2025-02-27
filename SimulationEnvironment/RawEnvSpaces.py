"""
Observation- and Action Space are handled here.
"""
from typing import Union
from datetime import timedelta, datetime
import time

import gymnasium as gym
from gymnasium.spaces import Dict, Box, MultiBinary, Discrete
from ray.rllib.utils.spaces.repeated import Repeated
import numpy as np

from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ElectricityCost.ElectricyPrice import InterfacePriceTable
from SimulationModules.Enums import GiniModes, AgentRequestAnswer, TypeOfField, Request_state
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ParkingArea.GiniMover import GiniMover
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField
from typing import List
from SimulationModules.ElectricVehicle.EV import EV_modes
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from helpers.Diagnosis import timeit
from SimulationEnvironment.EnvConfig import EnvConfig

from config.logger_config import get_module_logger
logger = get_module_logger(__name__)
horizon=96

class RawEnvSpaceManager():

    def __init__(self, config: dict,
                 parking_area: ParkingArea,
                 charging_session_manager: ChargingSessionManager,
                 local_grid: LocalGrid,
                 gini_mover: GiniMover,
                 time_manager: InterfaceTimeManager):

        self.parking_area: ParkingArea=parking_area
        self.charging_session_manager: ChargingSessionManager=charging_session_manager
        self.local_grid: LocalGrid=local_grid
        self.gini_mover: GiniMover=gini_mover
        self.time_manager:InterfaceTimeManager = time_manager

        self.read_config(config, len(self.parking_area.parking_area_fields))
        
    def read_config(self, config: EnvConfig, area_size: int):

        self.area_size=area_size

        self.price_table: InterfacePriceTable = config.price_table
        #settings = config["settings"]
        self.step_time=config.step_time
        #self.settings = None if settings is None else settings
        self.start_time=config.start_datetime
        self.sim_duration=config.sim_duration
        self.price_table: InterfacePriceTable = None if self.price_table is None else self.price_table
        self.max_charging_power=config.max_charging_power.get_in_w().value
        self.max_grid_power=config.max_grid_power.get_in_w().value
        self.gini_starting_fields=config.gini_starting_fields
        self.max_building_power=config.max_building_power.get_in_w().value
        #self.pred_building_power=[p.get_in_w().value for p in config["pred_building_power"]]
        self.max_pv_power=config.max_pv_power.get_in_w().value
        #self.pred_pv_power=[p.get_in_w().value for p in config["pred_pv_power"]]
        self.max_parking_time=config.max_parking_time
        self.max_energy_request=config.max_energy_request.get_in_j().value
        self.max_ev_energy=config.max_ev_energy.get_in_j().value
        self.max_gini_energy=config.max_gini_energy.get_in_j().value
        self.max_price=500
        self.amount_ginis=len(self.gini_starting_fields)
        self.horizon = 1
        if not hasattr(config,"include_future_price"):
            self.include_future_price=False
        else:
            self.include_future_price = config.include_future_price
            if self.include_future_price:
                self.horizon = 12
        #the following value is the probability for a new customer to arrive every step_time:
        self.new_customer_prob=config.customers_per_hour/3600*self.step_time.total_seconds()
        self.customers_per_hour=config.customers_per_hour
        self.weights_for_reward=config.weights_for_reward

    def create_observation_space(self):

        obs_grid_power=Box(low=-self.max_grid_power, high=self.max_grid_power, dtype=np.float32)       
        obs_building_power=Box(low=-self.max_building_power, high=self.max_building_power, dtype=np.float32)             
        obs_pred_building_power=Box(low=np.zeros(horizon), 
                                    high=np.full(horizon,self.max_building_power), dtype=np.float32)
        obs_peak_grid_power=Box(low=-self.max_grid_power, high=self.max_grid_power, dtype=np.float32)
        #thats the electricity price in cents per kWh
        obs_el_price=Box(low=-self.max_price, high=self.max_price, dtype=np.int32)
        #the obs_price_table gives back the energy costs for the following 24 hours in 96 15-minute intervalls
        obs_price_table=Box(np.zeros(horizon), np.full(horizon, self.max_price), dtype=np.int16)
        obs_pv_power=Box(low=0, high=self.max_pv_power, dtype=np.float32)
        obs_pred_pv_power=Box(low=np.zeros(horizon), high=np.full(horizon,self.max_pv_power), dtype=np.float32)
        #the following observation gives back the dijkstra distances between to field indexes as a matrix
        obs_distances=Box(low=np.zeros([self.area_size,self.area_size]), high=np.full([self.area_size,self.area_size],200))
        #0=path, 1=normal parkingspot, 2=parkingspot with chargingstation, 3=obstacle
        obs_field_kinds=Box(low=np.zeros(self.area_size), high=np.full(self.area_size, 3), dtype=np.int8)
        #user rquests can be done theoretically on every field, the states are: 0=no request,
        #1=requested, 2=request confirmed, 3= rwquest denied, 4=charging, 5=satisfied
        obs_user_requests=Box(low=np.zeros(self.area_size), high=np.full(self.area_size, 5), dtype=np.int8)
        obs_estimated_parking_time=Box(low=np.zeros(self.area_size), 
                                       high=np.full(self.area_size, self.max_parking_time.total_seconds()),
                                       dtype=np.int16)
        obs_energy_requests=Box(low=np.zeros(self.area_size), 
                                high=np.full(self.area_size, self.max_energy_request),
                                dtype=np.float64)
        #every gini has a state. the states are: 0=IDLE,1=driving to ev, 2=returning to cs,
        #3=charging ev, 4=gets charged, 5=connected to ev, 6=connected to cs 
        obs_gini_states=Box(low=np.zeros(self.amount_ginis), high=np.full(self.amount_ginis, len(GiniModes)-1), dtype=np.int8)
        #the positions of the ginis is defined by the index of the field, not by its coordinates
        obs_field_indices_ginis=Box(low=np.zeros(self.amount_ginis, dtype=np.int32), 
                                high=np.full(self.amount_ginis,
                                            self.area_size), 
                                dtype=np.int32)
        obs_soc_ginis=Box(low=np.zeros(self.amount_ginis), 
                                high=np.full(self.amount_ginis,1), 
                                dtype=np.float32)
        obs_gini_charging_power=Box(low=np.full(self.amount_ginis,
                                            -self.max_charging_power),
                                            high=np.full(self.amount_ginis,
                                            self.max_charging_power), dtype=np.float32)
        obs_gini_energy=Box(low=np.zeros(self.amount_ginis),
                            high=np.full(self.amount_ginis, self.max_gini_energy),
                            dtype=np.float32)
        #for simplification, every field without a vehicle gets a cs of None,
        #thats the way an agents recognizes that there is not ev
        obs_charging_states=Box(low=np.zeros(self.area_size), 
                            high=np.full(self.area_size,1), dtype=np.float32)
        obs_ev_energy=Box(low=np.zeros(self.area_size),
                          high=np.full(self.area_size, self.max_ev_energy), dtype=np.float32)
        obs_cs_charging_power=Box(low=np.zeros(self.area_size, dtype=np.float32), 
                            high=np.full(self.area_size,self.max_charging_power), dtype=np.float32)
        #every cs' power is restricted physically an by the evs' properties. Additionally, 
        #it can be limited by the agent. The final, actual restriction is than stored in 
        #cs_charging_limits
        obs_cs_charging_limits=Box(low=np.zeros(self.area_size),
                                high=np.full(self.area_size, self.max_charging_power),
                                dtype=np.float64)
        obs_gini_requested_energy=Box(low=np.full(self.amount_ginis,
                                            -self.max_gini_energy),
                                            high=np.full(self.amount_ginis,
                                            self.max_gini_energy), dtype=np.float32)

        #the actual time is given by the amount of passed seconds
        obs_current_time=Box(low=0, high=self.sim_duration.total_seconds(), dtype=np.int32)
        
        soc_stat_battery = Box(low=0, high=1, dtype=np.float32)
        stat_battery_chrg_pwr_max = Box(low=0, high=100000, dtype=np.float32)
        stat_battery_dischrg_pwr_max = Box(low=-100000, high=100000, dtype=np.float32)
        stat_batt_pwr_actual = Box(low=-100000, high=100000, dtype=np.float32)

        
        observation_space_raw = Dict({
                "grid_power": obs_grid_power,
                "building_power": obs_building_power,
                "pred_building_power": obs_pred_building_power,
                "peak_grid_power": obs_peak_grid_power,
                "el_price": obs_el_price,
                "price_table": obs_price_table,
                "pv_power": obs_pv_power,
                "pred_pv_power": obs_pred_pv_power,
                "distances": obs_distances,
                "field_kinds": obs_field_kinds,

                "soc_stat_battery": soc_stat_battery,
                "stat_battery_chrg_pwr_max": stat_battery_chrg_pwr_max,
                "stat_battery_dischrg_pwr_max": stat_battery_dischrg_pwr_max,
                "stat_batt_power": stat_batt_pwr_actual,

                "user_requests": obs_user_requests,
                "estimated_parking_time": obs_estimated_parking_time,
                "energy_requests": obs_energy_requests,
                "ev_energy": obs_ev_energy,

                "field_indices_ginis": obs_field_indices_ginis,
                "gini_states": obs_gini_states,
                "soc_ginis": obs_soc_ginis,
                "gini_energy": obs_gini_energy,
                "gini_requested_energy": obs_gini_requested_energy,               
                "gini_charging_power": obs_gini_charging_power,

                "charging_states": obs_charging_states,                      
                "cs_charging_power": obs_cs_charging_power,
                "cs_charging_limits": obs_cs_charging_limits,
                "current_time": obs_current_time,
                })
        
        
        return observation_space_raw
    
    def create_action_space(self):

        act_requested_gini_field=Box(low=np.zeros(self.amount_ginis), 
                                 high=np.full(self.amount_ginis,self.area_size-1), 
                                 dtype=np.int32)
        act_requested_gini_power=Box(low=np.zeros(self.amount_ginis), 
                                 high=np.full(self.amount_ginis,self.max_charging_power), 
                                 dtype=np.int32)
        #these are just the wnated charging powers of the immobile 
        #charging stations in kW. Not the ginis
        act_target_charging_power=Box(low=np.full(self.area_size,-self.max_charging_power), 
                                  high=np.full(self.area_size,self.max_charging_power),
                                  dtype=np.float32)
        #request can be answered by: 0= no answer, 1=confirm, 2=deny
        act_request_answer=Box(low=np.zeros(self.area_size),
                               high=np.full(self.area_size, len(AgentRequestAnswer)-1),
                               dtype=np.int8)    
        
        act_target_stat_battery_power = Box(low=-1000000, 
                                  high=1000000,shape=(1,),
                                  dtype=np.float32)
            
        action_space_raw = Dict({
            "requested_gini_field": act_requested_gini_field,
            "requested_gini_power": act_requested_gini_power,
            "target_charging_power" : act_target_charging_power,
            "request_answer": act_request_answer,
            "target_stat_battery_charging_power": act_target_stat_battery_power
            })
        
        return action_space_raw
        
    def create_action_base(self):

        action_raw_base={
            "requested_gini_field": np.full(self.amount_ginis,None),
            "requested_gini_power": np.full(self.amount_ginis,None),
            "target_charging_power" : np.full(self.area_size,None),
            "request_answer": np.full(self.area_size,None),
            "target_stat_battery_charging_power" : [0]
        } 

        return action_raw_base
    
    def write_observations(self, 
                           ):
        """
        this method has the only purpose to transfer alle information from the sim
        into an observation, which can be used for this environment.
        """
        current_date_time = self.time_manager.get_current_time()
        passed_seconds=[(self.time_manager.get_current_time()-self.time_manager.get_start_time()).total_seconds()]

        fields: List[InterfaceField] =self.parking_area.parking_area_fields


        #self.local_grid.calculate_connection_point_load()
        grid_power=[self.local_grid.get_current_connection_load().get_in_w().value]
        building_power=[self.local_grid.building.get_power_contribution().get_in_w().value]
        pred_building_power=[power.get_in_w().value for power in self.local_grid.get_building_power_future()]
        peak_grid_power=[None]#self.local_grid.peak_grid_consumption.get_in_w().value]
        el_price=[self.price_table.get_price(current_date_time)]       
        price_in_future=self.price_table.get_price_future(date_time=current_date_time, horizon = horizon, step_time = timedelta(seconds=900))[0]
        pv_power=[self.local_grid.PV.get_power_contribution().get_in_w().value]
        pred_pv_power=[power.get_in_w().value for power in self.local_grid.get_pv_power_future()]
        distances_for_indices=np.array(self.parking_area.distances_for_indices)
        distances_for_indices[np.isinf(distances_for_indices)]=None
        distances=distances_for_indices
        field_kinds=self.parking_area.field_kinds


        user_requests=self.get_user_requests(fields)

        estimated_parking_time, energy_requests, charging_states, ev_energy=self.get_field_related_data(fields, current_date_time)
        
        field_indices_ginis, gini_states, soc_ginis, gini_energy, gini_requested_energy, gini_charging_power=self.get_gini_related_data()
          
        cs_charging_power, cs_charging_limits= self.get_charger_related_data(fields) 

        if self.local_grid.stationary_battery is not None:
            self.local_grid.stationary_battery._update_charging_power_limits() 
        soc_stat_battery = [self.local_grid.stationary_battery.get_soc()] if self.local_grid.stationary_battery is not None else None
        stat_battery_chrg_pwr_max = [self.local_grid.stationary_battery.maximum_grid_power.get_in_w().value] if self.local_grid.stationary_battery is not None else [0]
        stat_battery_dischrg_pwr_max = [self.local_grid.stationary_battery.minimum_grid_power.get_in_w().value] if self.local_grid.stationary_battery is not None else [0]
        stat_batt_pwr_actual = [self.local_grid.stationary_battery.actual_grid_power.get_in_w().value] if self.local_grid.stationary_battery is not None else [0]
        
        observation_raw={
            "grid_power": grid_power,
            "building_power": building_power,
            "pred_building_power": pred_building_power,
            "peak_grid_power": peak_grid_power,
            "el_price": el_price,
            "price_table": price_in_future,
            "pv_power": pv_power,
            "pred_pv_power": pred_pv_power,
            "distances": distances,
            "field_kinds": field_kinds,

            "soc_stat_battery": soc_stat_battery,
            "stat_battery_chrg_pwr_max": stat_battery_chrg_pwr_max,
            "stat_battery_dischrg_pwr_max": stat_battery_dischrg_pwr_max,
            "stat_batt_power": stat_batt_pwr_actual,

            "user_requests": user_requests,
            "estimated_parking_time": estimated_parking_time,
            "energy_requests": energy_requests,
            "ev_energy": ev_energy,

            "field_indices_ginis": field_indices_ginis,
            "gini_states": gini_states,
            "soc_ginis": soc_ginis,
            "gini_energy": gini_energy,
            "gini_requested_energy": gini_requested_energy,               
            "gini_charging_power": gini_charging_power,

            "charging_states": charging_states,                      
            "cs_charging_power": cs_charging_power,
            "cs_charging_limits": cs_charging_limits,
            "current_time": passed_seconds,

        }    
        info_string=""
        #info_string=f"Date Time {current_date_time}, Grid Power: {round(grid_power[0],1)} W, Building Power: {round(building_power[0],1)}"
        #info_string+=f"\n, PV Power: {round(pv_power[0],1)}, GINI States: {gini_states}, Gini Positions: {field_indices_ginis},"
        #cs_charging_power_comp=[(index, value) for index, value in enumerate(cs_charging_power) if value is not None]
        #info_string+=f"\nCS Power: {cs_charging_power_comp}"
        info_string+=f"\nStationary Battery SOC {soc_stat_battery}, Power {stat_batt_pwr_actual} W\n"
        #logger.info(info_string)


        return observation_raw

    #region translate to space data
  
    def get_user_requests(self, fields):
        user_requests=np.full(self.area_size, None)
        for requests in self.parking_area.request_collector.get_requests():
            if requests.state == Request_state.REQUESTED:
                user_requests[requests.field_index]=1
            elif requests.state == Request_state.CONFIRMED:
                user_requests[requests.field_index]=2
            elif requests.state == Request_state.DENIED:
                user_requests[requests.field_index]=3
            elif requests.state == Request_state.CHARGING:
                user_requests[requests.field_index]=4
            elif requests.state == Request_state.SATISFIED:
                user_requests[requests.field_index]=5
        
        return user_requests
    

    def get_field_related_data(self, fields, current_date_time):
        
        estimated_parking_time=np.full(self.area_size, None)
        energy_requests=np.full(self.area_size, None)
        charging_states=np.full(self.area_size, None)
        ev_energy=np.full(self.area_size, None)
        for field in fields:
            if field.has_parked_vehicle():
                ev=field.vehicle_parked
                energy_requests[field.index]=ev.current_energy_demand.get_in_j().value
                charging_states[field.index]=ev.get_soc()
                ev_energy[field.index]=ev.get_battery_energy().get_in_j().value
                estimated_parking_time[field.index]=max(ev.arrival_time+ev.stay_duration-current_date_time, timedelta(seconds=0)).total_seconds()

        return estimated_parking_time, energy_requests, charging_states, ev_energy
    

    def get_gini_related_data(self):
        field_indices_ginis=np.zeros(self.amount_ginis)
        gini_states=np.full(self.amount_ginis, None)
        soc_ginis=np.full(self.amount_ginis, None)
        gini_energy=np.full(self.amount_ginis, None)
        gini_requested_energy=np.full(self.amount_ginis, None)
        gini_charging_power=np.full(self.amount_ginis, None)
        for i, gini in enumerate(self.gini_mover.ginis):
            gini_states[i]=gini.status.value
            soc_ginis[i]=gini.get_soc()
            gini_energy[i]=gini.get_battery_energy().get_in_j().value
            gini_requested_energy[i]=gini.get_requested_energy().get_in_j().value
            field_indices_ginis[i]=gini.get_current_field().index
            gini_charging_power[i]=gini.actual_charging_power.get_in_w().value

        return field_indices_ginis, gini_states, soc_ginis, gini_energy, gini_requested_energy, gini_charging_power
    

    def get_charger_related_data(self, fields):
        cs_charging_power=np.full(self.area_size, None)
        cs_charging_limits=np.full(self.area_size, None)
        #sessions=[session for session in charging_session_manager.active_sessions if isinstance(session, ChargingSession)]
        
        for field in self.parking_area.fields_with_chargers:
            index=field.index
            charger = field.get_charger()
            cs_charging_power[index]=charger.get_power_contribution().get_in_w().value*(-1)
            cs_charging_limits[index]=charger.get_maximum_grid_power().get_in_w().value 

        return cs_charging_power, cs_charging_limits

    # endregion   

    def reset_obs(self, price_prediction: list):


        observation_raw={
            "grid_power": [0],
            "building_power": [0],
            "pred_building_power": np.zeros(self.horizon),
            "peak_grid_power": [0],
            "price_table": price_prediction,
            "pv_power": [0],
            "pred_pv_power": np.zeros(self.horizon),#self.pred_building_power,
            "distances": self.parking_area.distances_for_indices,
            "field_kinds": self.parking_area.field_kinds,

            "soc_stat_battery": [0],
            "stat_battery_chrg_pwr_max": [0],
            "stat_battery_dischrg_pwr_max": [0],
            "stat_batt_power": [0],

            "user_requests": np.ones(self.area_size),
            "estimated_parking_time": np.zeros(self.area_size),
            "energy_requests": np.zeros(self.area_size),
            "ev_energy": np.zeros(self.area_size),

            "field_indices_ginis": self.gini_starting_fields,
            "gini_states": np.zeros(self.amount_ginis),
            "soc_ginis": np.ones(self.amount_ginis)*100,
            "gini_energy": np.zeros(self.amount_ginis),
            "gini_requested_energy": np.zeros(self.amount_ginis),               
            "gini_charging_power": np.zeros(self.amount_ginis),

            "charging_states": np.full(self.area_size, None),                      
            "cs_charging_power": np.zeros(self.area_size),
            "cs_charging_limits": np.zeros(self.area_size),
            "current_time": 0,
        }

        return observation_raw


    def validate_to_fit_space(self, space: gym.Space, instance: any):
        """
        this method checks, if a space (action-/observation-space) fits a given instance.
        E.g. we can test, if the action given by the agent (the instance) is legit according to 
        the defines action space in the envs init-method (the space). The same test can be made with
        a translated observation and the defined observation space.
        """
        if instance is not None:
            if isinstance(space, gym.spaces.Discrete):
                #unit= Union[int, np.integer]
                if not isinstance(instance, int) and not isinstance(instance, np.integer):
                    sample=space.sample()
                    raise ValueError("The object does not correspond to discrete space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     " with type: "+str(type(instance))+"\nspace sample: "+str(sample)+" with type: "+str(type(sample)))
                if not space.contains(instance):
                    raise ValueError(f"The object {instance} is not contained in the discrete space.")

            elif isinstance(space, gym.spaces.MultiDiscrete):
                if not isinstance(instance, list) and not isinstance(instance, np.ndarray):
                    sample=space.sample()
                    raise ValueError("The object does not correspond to multidiscrete space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     " with type: "+str(type(instance))+"\nspace sample: "+str(sample)+" with type: "+str(type(sample)))
                if not space.contains(instance):
                    raise ValueError(f"The object {instance} is not contained in the multidiscrete space.")

            elif isinstance(space, gym.spaces.Box):
                if not isinstance(instance, (list, tuple, np.ndarray)):
                    raise ValueError("The object does not correspond to the box space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     "\nspace sample: "+str(space.sample()))
                if not np.array_equal(np.array(instance).shape, space.shape):
                    raise ValueError("The object does not have the right shape for the box space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     "\nspace sample: "+str(space.sample()))
            

            elif isinstance(space, gym.spaces.Tuple):
                if not isinstance(instance, (list, tuple)):
                    raise ValueError("The object does not correspond to the tuple space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     "\nspace sample: "+str(space.sample()))
                if len(space.spaces) != len(instance):
                    raise ValueError(f"The length of the object {len(instance)} does not match the number of spaces in the tuple space {len(space.spaces)}.")
                for subspace, subobj in zip(space.spaces, instance):
                    self.validate_to_fit_space(subspace, subobj)

            elif isinstance(space, gym.spaces.Sequence):
                #TODO
                #a sequnce is pretty hard to check, thats why
                if not isinstance(instance, (list, tuple, np.ndarray)):
                    raise ValueError("The object does not correspond to the Sequence space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance))   
                for subobj in instance:
                    self.validate_to_fit_space(space.feature_space, subobj)
            
            elif isinstance(space, Repeated):

                if not isinstance(instance, (list, np.ndarray)):
                    raise ValueError("The object does not correspond to the Repeated space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance))
                if len(instance) > space.max_len:
                    raise ValueError("Repeated instance is too long: "+"\nspace: "+str(space)+"\ninstance: "+str(instance))   
                for subobj in instance:
                    self.validate_to_fit_space(space.child_space, subobj)

            elif isinstance(space, gym.spaces.Dict):
                if not isinstance(instance, dict):
                    raise ValueError("The object does not correspond to the dict space: "+"\nspace: "+str(space)+"\ninstance: "+str(instance)+
                                     "\nspace sample: "+str(space.sample()))
                for key, subspace in space.spaces.items():
                    if key not in instance:
                        raise ValueError(f"The object does not contain the required key '{key}' for the dict space.")
                    self.validate_to_fit_space(subspace, instance[key])

            else:
                raise ValueError("Invalid space type: "+"\nspace: "+str(space)+"\ninstance: "+str(instance))

    


