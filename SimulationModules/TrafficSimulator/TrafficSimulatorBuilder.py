from SimulationModules.TrafficSimulator.TrafficSimulator import TrafficSimulator
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import ParkingSpotAssignerBuilder
from SimulationModules.TrafficSimulator.InterfaceTrafficSimulator import InterfaceTrafficSimulator
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.EvBuilder.EvBuilderFactory import EvBuilderFactory
from SimulationModules.TrafficSimulator.EvFromParkingSpotRemover import EvFromParkingSpotRemover
from datetime import timedelta,datetime
from typing import Optional
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager



class TrafficSimulatorBuilder:
    @staticmethod
    def build(time_manager: InterfaceTimeManager,
              parking_area: ParkingArea,
              customers_per_hour: float,
              assigner_mode: str = "random",
              max_parking_time: Optional[timedelta] = None,
              recording_data_path: Optional[str] = None) -> InterfaceTrafficSimulator:
        
        ev_builder = EvBuilderFactory.create(ev_builder_option="base" if recording_data_path is None else "from_recording",
                                                time_manager=time_manager,
                                             max_parking_time=max_parking_time,
                                             recording_data_path=recording_data_path,
                                             customers_per_hour=customers_per_hour)
        
        parking_spot_assigner = ParkingSpotAssignerBuilder.build_assigner(assigner_mode, parking_area=parking_area)
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                                time_manager=time_manager)

        return TrafficSimulator(ev_builder=ev_builder,
                                parking_spot_assigner=parking_spot_assigner,
                                ev_from_parking_spot_remover=ev_from_parking_spot_remover)



