from abc import ABC, abstractmethod
from SimulationModules.ElectricVehicle.EV import InterfaceEV
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from enum import IntEnum
from datetime import timedelta
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

class ChargeMode(IntEnum):
    IDLE = 0
    CHARGING = 1
    DISCHARGING = 2
    

class InterfaceEnergyTransferSession(ABC):

    @abstractmethod
    def perform_energy_transfer(self):
        raise NotImplementedError

    @abstractmethod
    def calculate_power_setpoint(self):
        raise NotImplementedError

    @abstractmethod
    def determine_charge_mode(self):
        raise NotImplementedError
    
    @abstractmethod
    def calculate_setpoint(self):
        raise NotImplementedError
    
    @abstractmethod
    def limit_power_setpoint_charging(self):

        raise NotImplementedError
    
    @abstractmethod
    def limit_power_setpoint_discharging(self):
        raise NotImplementedError
    
    @abstractmethod
    def calculate_energy_setpoint(self):
        raise NotImplementedError
    
    @abstractmethod
    def limit_energy_setpoint(self):
        raise NotImplementedError
    
    @abstractmethod
    def calculate_transfered_energy(self):
        raise NotImplementedError
    
    @abstractmethod
    def calculate_actual_power(self):
        raise NotImplementedError
    
    @abstractmethod
    def transfer_energy(self):
        raise NotImplementedError
    
    @abstractmethod
    def update_time_step_size(self, step_time_size: timedelta):
        raise NotImplementedError
    
    @abstractmethod
    def get_actual_power(self) -> PowerType:
        raise NotImplementedError
    
    @abstractmethod
    def get_transfered_energy(self) -> EnergyType:
        raise NotImplementedError
    

class EnergyTransferSession(InterfaceEnergyTransferSession):

    def __init__(self,
                 charging_station: InterfaceChargingStation,
                 electric_vehicle: InterfaceEV):
        self.charging_station: InterfaceChargingStation = charging_station
        self.electric_vehicle: InterfaceEV = electric_vehicle
        self.mode = ChargeMode.IDLE
        self.setpoint = PowerType(0, PowerTypeUnit.KW)
        self.step_time_size: timedelta = None
        self.actual_power = PowerType(0, PowerTypeUnit.KW)
        self.transfered_energy = EnergyType(0, EnergyTypeUnit.KWH)

    def update_time_step_size(self, step_time_size: timedelta):
        self.step_time_size = step_time_size


    def perform_energy_transfer(self):
        if self.step_time_size is None:
            raise ValueError("Step time size must be set before performing energy transfer")
        if self.step_time_size.total_seconds() == 0:
            logger.warning("Step time size is zero, no energy transfer will be performed")
            self.actual_power = PowerType(0, PowerTypeUnit.KW)
            self.transfered_energy = EnergyType(0, EnergyTypeUnit.KWH)
            return         
        self.calculate_power_setpoint()  
        self.calculate_energy_setpoint()         
        self.limit_energy_setpoint()
        self.calculate_transfered_energy()
        self.calculate_actual_power()
        self.transfer_energy()     


    def calculate_power_setpoint(self):
        # Get the target power from the charging station and the EV
        self.calculate_setpoint()
        # Determine the charge mode
        self.determine_charge_mode()
        if self.mode == ChargeMode.CHARGING or self.mode == ChargeMode.IDLE:
            self.limit_power_setpoint_charging()
        elif self.mode == ChargeMode.DISCHARGING:
            self.limit_power_setpoint_discharging()
        


    def determine_charge_mode(self):
        if self.setpoint is None:
            self.mode = ChargeMode.IDLE
            return 
        if self.setpoint > 0:
            self.mode = ChargeMode.CHARGING
        elif self.setpoint < 0:
            self.mode = ChargeMode.DISCHARGING
        else:
            self.mode = ChargeMode.IDLE


    def calculate_setpoint(self):
        targets = [self.charging_station.get_target_power(), self.electric_vehicle.get_target_power()]
        valid_targets = [target for target in targets if target is not None]
        
        if not valid_targets:
            self.setpoint = None
        else:
            positive_targets = [target for target in valid_targets if target >= 0]
            negative_targets = [target for target in valid_targets if target < 0]
            
            if positive_targets:
                self.setpoint = min(positive_targets)
            elif negative_targets:
                self.setpoint = min(negative_targets, key=abs)
            else:
                self.setpoint = None  # or some default value

    def limit_power_setpoint_charging(self):
        max_powers = [self.setpoint, 
                      self.charging_station.get_maximum_cs_charging_power(), 
                      self.electric_vehicle.get_maximum_charging_power()]
        valid_max_powers = [max_power for max_power in max_powers if max_power is not None]
        self.setpoint = min(valid_max_powers)

    def limit_power_setpoint_discharging(self):
        if self.setpoint is not None and self.setpoint>0:
            raise ValueError(f"Discharging power must be negative, setpoint is {self.setpoint}")
        min_powers = [self.setpoint, 
                      self.charging_station.get_maximum_cs_feedback_power(), 
                      self.electric_vehicle.get_maximum_discharging_power()]
        valid_min_powers = [min_power * -1 if min_power > 0 else min_power for min_power in min_powers if min_power is not None]      
        self.setpoint = max(valid_min_powers)  
        
    def calculate_energy_setpoint(self):
        self.energy_setpoint = self.setpoint * self.step_time_size

    def limit_energy_setpoint(self):
        self.energy_setpoint = min(self.energy_setpoint, 
                         self.charging_station.get_maximum_transferable_energy(),
                         self.electric_vehicle.get_maximum_receivable_energy()
                         )
        
    def calculate_transfered_energy(self):
        self.transfered_energy = self.energy_setpoint
    
    def calculate_actual_power(self):
        self.actual_power = self.transfered_energy / self.step_time_size

    def transfer_energy(self):
        txt = (
            f"Energy transferred: {self.transfered_energy.get_in_kwh().value} kWh and actual power: {self.actual_power.get_in_kw().value} kW \n"
            f"with setpoints {self.setpoint.get_in_kw().value} kW and CS max: {self.charging_station.get_maximum_cs_charging_power()} kW and EV max: {self.electric_vehicle.get_maximum_charging_power()} kW"
            f"max receivable energy {self.electric_vehicle.get_maximum_receivable_energy()}"
        )
        logger.info(txt)
        self.charging_station.set_actual_charging_power(-self.actual_power)
        self.electric_vehicle.set_actual_charging_power(self.actual_power)
        self.charging_station.give_charging_energy_over_time(self.transfered_energy, self.step_time_size)
        self.electric_vehicle.charge_ev_with_energy(self.transfered_energy)



    def get_actual_power(self) -> PowerType:
        return self.actual_power
    
    def get_transfered_energy(self) -> EnergyType:
        return self.transfered_energy

