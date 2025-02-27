from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaBuilder import ParkingAreaBuilder
from SimulationModules.ParkingArea.GiniMover import GiniMover
from SimulationModules.TrafficSimulator.TrafficSimulatorBuilder import TrafficSimulatorBuilder
from SimulationModules.TrafficSimulator.InterfaceTrafficSimulator import InterfaceTrafficSimulator
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager, TimeManager
from SimulationModules.ElectricalGrid.LocalGridBuilder import LocalGridBuilder
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.StationaryStorageChargingSession import StationaryStorageChargingSession
from SimulationModules.RequestHandling.RequestHandler import RequestHandler
from SimulationModules.Reward.RewardBuilder import RewardBuilder
from SimulationModules.Reward.InterfaceReward import InterfaceReward
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from SimulationModules.Gini.GiniBuilder import GiniBuilder
from SimulationEnvironment.EnvConfig import EnvConfig
    




class EnvBuilder():
    def __init__(self, env_config: EnvConfig):
        self.env_config = env_config

        self.local_grid = None
        self.parking_area = None
        self.time_manager = None
        self.charging_session_manager = None
        self.electricity_cost = None
        self.traffic_simulator = None
        self.gini_mover = None


    def build_time_manager(self) -> InterfaceTimeManager:
        self.time_manager = TimeManager(start_time=self.env_config.start_datetime, 
                                   step_time=self.env_config.step_time,
                                   sim_duration=self.env_config.sim_duration)
        return self.time_manager
    
    def check_time_manager_is_build(self):
        if self.time_manager is None:
            raise Exception("Time manager must be built before building other components")

    def build_parking_area(self) -> ParkingArea:
        self.parking_area: ParkingArea= ParkingAreaBuilder.build(parking_lot_file_path=self.env_config.parking_lot_path,
                                    max_power_of_cs=self.env_config.max_charging_power)        
        return self.parking_area
    
    def build_traffic_simulator(self)-> InterfaceTrafficSimulator:
        self.check_time_manager_is_build()
        if self.parking_area is None:
            raise Exception("Parking area must be built before building traffic simulator")
        traffic_simulator = TrafficSimulatorBuilder.build(time_manager=self.time_manager,
                                                            parking_area=self.parking_area,
                                                            customers_per_hour=self.env_config.customers_per_hour,
                                                            assigner_mode=self.env_config.assigner_mode,
                                                            max_parking_time=self.env_config.max_parking_time,
                                                            recording_data_path=self.env_config.recording_data_path)
        return traffic_simulator

    def build_local_grid(self):
        self.check_time_manager_is_build()
        cs_list = self.parking_area.get_charging_station_list()
        if len(cs_list) == 0:
            raise Exception("No charging stations in parking area")
        self.local_grid = LocalGridBuilder.build(time_manager=self.time_manager,
                                                config= self.env_config,
                                                charging_station_list=cs_list)
        for consumer in self.local_grid.connected_consumers :
            if consumer is None: 
                raise Exception(f"Consumer in {self.local_grid.connected_consumers} is  None")
        return self.local_grid

    def build_charging_session_manager(self):
        self.check_time_manager_is_build()
        if self.parking_area is None:
            raise Exception("Parking area must be built before building charging session manager")
        request_handler = RequestHandler(request_collector=self.parking_area.request_collector)
        self.charging_session_manager = ChargingSessionManager(parking_area=self.parking_area,
                                                          time_manager=self.time_manager,
                                                          request_handler=request_handler)
        if self.local_grid.stationary_battery is not None:

            self.charging_session_manager.active_sessions.append(StationaryStorageChargingSession(battery_storage=self.local_grid.stationary_battery,
                                                                                         time_manager=self.time_manager))
        return self.charging_session_manager
    
    def build_electricity_cost(self):
        self.check_time_manager_is_build()
        if self.local_grid is None:
            raise Exception("Local grid must be built before building electricity cost")
        self.electricity_cost = ElectricityCost(price_table=self.env_config.price_table,
                               time_manager=self.time_manager,
                               local_grid=self.local_grid)
        return self.electricity_cost
    
    def build_gini_mover(self):
        self.check_time_manager_is_build()
        if self.parking_area is None:
            raise Exception("Parking area must be built before building gini mover")
        gini_list = GiniBuilder.build(self.env_config.gini_starting_fields)
        self.gini_mover = GiniMover(parking_area=self.parking_area,
                                   step_time=self.time_manager.get_step_time())
        self.gini_mover.add_ginis(gini_list)
        self.gini_mover.assign_gini_to_field(self.env_config.gini_starting_fields)
        return self.gini_mover
    
    def build_reward_system(self):
        if self.charging_session_manager is None:
            raise Exception("Charging session manager must be built before building reward system")
        if self.electricity_cost is None:
            raise Exception("Electricity cost must be built before building reward system")
        if self.gini_mover is None:
            raise Exception("Gini mover must be built before building reward system")
        
        reward_manager: InterfaceReward= RewardBuilder.build(config=self.env_config,
                                                                charging_session_manager=self.charging_session_manager,
                                                                electricity_cost=self.electricity_cost,
                                                                ginis=self.gini_mover.ginis)
        return reward_manager
    





    
    


