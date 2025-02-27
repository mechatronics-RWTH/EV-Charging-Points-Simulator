from SimulationModules.ElectricVehicle.EV import InterfaceEV
from datetime import datetime, timedelta
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from typing import Union
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from abc import ABC, abstractmethod
from SimulationModules.ChargingSession.PowerTransferTrajectory import InterfacePowerTransferTrajectory, PowerTransferTrajectory
from SimulationModules.ChargingSession.ChargingStateTrajectory import InterfaceChargingStateTrajectory, ChargingStateTrajectory
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from SimulationModules.ChargingSession.EnergyTransferSession  import InterfaceEnergyTransferSession, EnergyTransferSession
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class IChargingSession(ABC):
    power_transfer_trajectory: InterfacePowerTransferTrajectory
    state_trajectory: InterfaceChargingStateTrajectory
    session_id: str
    ev: InterfaceEV
    charging_station: InterfaceChargingStation

    @abstractmethod
    def step(self, step_time: timedelta, agent_power_setpoint: PowerType = None):
        raise NotImplementedError

    @abstractmethod
    def end_session(self):
        raise NotImplementedError
    





class ChargingSession(IChargingSession,
                      InterfaceTimeDependent):
    """
    This class represents a charging session between a charging station and an 
    electric vehicle (or in this context charging robot GInI). A charging session
    is composed of an EV/Gini, a charging station (CS) and (optionally) a charging controller. 

    The delivered power is calculated based on the capabilities of the EV that is being charged
    (or discharged in case of bidi charging) and the capabilities of the charging station. 
    In case a charging controller is present, it can provide a setpoint within the limits of the 
    CS and the EV.

    Since multiple charging session can run in parallel in one environment it makes sense to define 
    asynchronous methods for it

    """

    def __init__(self,
                 ev: InterfaceEV,
                 charging_station: InterfaceChargingStation,
                 time_manager: InterfaceTimeManager,
                 field_index: int,

                 ):
        self._time_manager: InterfaceTimeManager = time_manager
        self.power_transfer_trajectory: InterfacePowerTransferTrajectory = PowerTransferTrajectory()
        self.state_trajectory: InterfaceChargingStateTrajectory = ChargingStateTrajectory()
        
        self.ev : InterfaceEV= ev
        self.field_index=field_index
        self.charging_station : Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charging_station
        self.energy_transfer_session: InterfaceEnergyTransferSession = EnergyTransferSession(charging_station=self.charging_station, 
                                                                                             electric_vehicle=self.ev) 
        
    def start(self):
        self.ev.connect_cs()
        self.charging_station.connect_ev()
        self.departure_time = self.ev.get_departure_time() if self.ev.get_departure_time() is not None else None
        self.time = self.time_manager.get_start_time()
        self.session_id = self.time.strftime("%Y%m%d%H%M") + "EV" + \
                        str(self.ev.id) + "CS" + \
                        str(self.charging_station.get_cs_id())
        #self.actual_charging_power = PowerType(0)
        self.charging_station.set_to_charging_ev()
        self.ev.set_to_charging()
        self.is_moveable_charging_station=isinstance(self.charging_station, InterfaceMobileChargingStation)
        self.power_transfer_trajectory.add_entry(power=self.energy_transfer_session.get_actual_power(),
                                            energy=self.energy_transfer_session.get_transfered_energy(),
                                            requested_energy=self.ev.get_requested_energy(),
                                            time=self.time_manager.get_current_time())

    @property
    def time_manager(self)->InterfaceTimeManager:
        return self._time_manager

    def step(self):
        

        time_to_charge=self.check_time_to_charge(self.time_manager.get_step_time())
        time_to_charge = self.get_time_to_charge_based_on_departure(time_to_charge)
        self.energy_transfer_session.update_time_step_size(time_to_charge)
        self.energy_transfer_session.perform_energy_transfer()
        self.power_transfer_trajectory.add_entry(power=self.energy_transfer_session.get_actual_power(),
                                            energy=self.energy_transfer_session.get_transfered_energy(),
                                            requested_energy=self.ev.get_requested_energy(),
                                            time=self.time_manager.get_current_time())
        

    def end_session(self):
        #here happens everything that has to be done when the session ends.
        self.ev.disconnect_from_cs()
        self.charging_station.set_actual_charging_power(PowerType(power_in_w=0, unit=PowerTypeUnit.W))
        self.charging_station.disconnect_ev()
        self.power_transfer_trajectory.add_entry(power=self.energy_transfer_session.actual_power,
                                            energy=EnergyType(energy_amount_in_j=0),
                                            requested_energy=self.ev.get_requested_energy(),
                                            time=self.time)

    def check_time_to_charge(self, step_time: timedelta):
        time_to_charge=step_time   
        if self.is_moveable_charging_station:
            mcs: InterfaceMobileChargingStation = self.charging_station
            mcs.time_step_remainder = step_time
            if mcs.is_traveling():
                mcs.update_remaining_travel_time(step_time)
            if mcs.is_traveling():
                time_to_charge=timedelta(seconds=0)
            else:
                time_to_charge= mcs.get_time_step_remainder()
        return time_to_charge
    
    def get_time_to_charge_based_on_departure(self, time_to_charge: timedelta):
        if self.departure_time is None:
            return time_to_charge
        max_time = self.departure_time - self.time_manager.get_current_time()
        min_time = min(time_to_charge, max_time)
        if min_time < timedelta(seconds=0):
            logger.warning(f"Time to charge is negative: {min_time}, departure seems to be in the past")
            min_time = timedelta(seconds=0)
        return min_time
    
    def is_session_stop_signalized(self):
        return self.ev.wants_interruption_ev() or self.charging_station.wants_interruption_cs()

