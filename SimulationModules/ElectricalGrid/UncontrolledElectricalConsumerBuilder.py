from SimulationModules.ElectricalGrid.ElectricalGridConsumer import UncontrolledElectricalGridConsumer
from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricalGrid.BuildingDataLoader import BuildingDataLoader
from 

from enum import IntEnum, Enum

class UncontrolledElectricalConsumerType(IntEnum):
    PhotovoltaicArray = 1
    Building = 2

class UncontrolledElectricalGridConsumerFactory:
    raise NotImplementedError

    # @staticmethod
    # def create(type_of_consumer: UncontrolledElectricalConsumerType,
    #            time_manager) -> UncontrolledElectricalGridConsumer:
    #     if type_of_consumer == UncontrolledElectricalConsumerType.PhotovoltaicArray:

    #         return PhotovoltaicArray()
    #     elif type_of_consumer == UncontrolledElectricalConsumerType.Building:
    #         building_data_loader= BuildingDataLoader(starttime=time_manager.get_start_time()-time_manager.get_step_time(),
    #                             endtime=time_manager.get_stop_time()+building.horizon_steps*time_manager.get_step_time(),
    #                             step_time=time_manager.get_step_time(),
    #                             yearly_consumption=yearly_building_consumption_in_kWh)
    #         building_data_loader.generate_power_trajectory()

    #         
    #         yearly_building_consumption_in_kWh = EnergyType(config["yearly_building_consumption_in_kWh"], unit=EnergyTypeUnit.KWH)
    #         building_data_loader= BuildingDataLoader(starttime=time_manager.get_start_time()-time_manager.get_step_time(),
    #                             endtime=time_manager.get_stop_time()+building.horizon_steps*time_manager.get_step_time(),
    #                             step_time=time_manager.get_step_time(),
    #                             yearly_consumption=yearly_building_consumption_in_kWh)
    #         building_data_loader.generate_power_trajectory()

    #         building.set_power_trajectory(building_data_loader.get_power_trajectory())
    #         building.create_future_power_map()
    #         return Building()
    #     else:
    #         raise ValueError("Invalid type of consumer")
