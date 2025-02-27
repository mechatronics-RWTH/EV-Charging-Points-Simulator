from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid 
from SimulationModules.ElectricalGrid.BuildingDataLoader import BuildingDataLoader
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.PhotovoltaicDataLoader import PhotovoltaicDataLoader
from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from typing import List
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ElectricalGridConsumer
from SimulationModules.ElectricalGrid.FuturePowerMapCreator import InterfaceFuturePowerMap, FuturePowerMap
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationEnvironment.EnvConfig import EnvConfig

class LocalGridBuilder:
    @staticmethod
    def build(time_manager: InterfaceTimeManager,
                    config:EnvConfig,
                charging_station_list: List[ElectricalGridConsumer] =[] ) -> LocalGrid:
        

        
        local_grid: LocalGrid=LocalGrid(time_manager=time_manager,
                                        )
        # TODO: BuildingBuilder?
        yearly_building_consumption_in_kWh = EnergyType(config.yearly_building_consumption_in_kWh, unit=EnergyTypeUnit.KWH)
        building_data_loader= BuildingDataLoader(starttime=time_manager.get_start_time()-time_manager.get_step_time(),
                                endtime=time_manager.get_stop_time()+config.horizon*time_manager.get_step_time(),
                                step_time=time_manager.get_step_time(),
                                yearly_consumption=yearly_building_consumption_in_kWh)
        building_data_loader.generate_power_trajectory()
        future_power_map_building: InterfaceFuturePowerMap = FuturePowerMap(time_manager=time_manager,
                                                                            horizon_steps=config.horizon)
        future_power_map_building.create_from_trajectory(power_trajectory=building_data_loader.get_power_trajectory())

        building = Building(name="Supermarket",
                                future_power_map=future_power_map_building)
        local_grid.add_consumers(building)
        
        # TODO: PVBuilder?
        kw_peak_config = config.max_pv_power
        pv_data_loader= PhotovoltaicDataLoader(starttime=time_manager.get_start_time(),
                            endtime=time_manager.get_stop_time()+ config.horizon*time_manager.get_step_time(),
                            step_time=time_manager.get_step_time(),
                            kw_peak_config=kw_peak_config)
        pv_data_loader.generate_power_trajectory()
        future_power_map_PV: InterfaceFuturePowerMap = FuturePowerMap(time_manager=time_manager,
                                                                            horizon_steps=config.horizon)
        future_power_map_PV.create_from_trajectory(power_trajectory = pv_data_loader.get_power_trajectory())
        photovoltaic = PhotovoltaicArray(name="pv_1",
                                        future_power_map=future_power_map_PV)
                                            
        local_grid.add_consumers(photovoltaic)
        if config.stationary_batteries is not None:
                local_grid.add_consumers( config.stationary_batteries)
        for charging_station in charging_station_list:
            local_grid.connected_consumers.append(charging_station)
        return local_grid
    

