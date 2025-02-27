from SimulationModules.ChargingSession.EnergyTransferSession import (EnergyTransferSession, 
                                                                     InterfaceEnergyTransferSession,
                                                                        ChargeMode)
import pytest
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricVehicle.EV import InterfaceEV
#from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from unittest.mock import MagicMock
from datetime import timedelta


@pytest.fixture
def mock_ev():
    return MagicMock(spec=InterfaceEV)

@pytest.fixture
def mock_cs():
    return MagicMock(spec=InterfaceChargingStation)

@pytest.fixture
def energy_transfer_session(mock_ev: InterfaceEV, mock_cs: InterfaceChargingStation):
    return EnergyTransferSession(charging_station=mock_cs, electric_vehicle=mock_ev)




class TestEnergyTransferSession: 

    def test_init(self, mock_ev: InterfaceEV, mock_cs: InterfaceChargingStation):
        energy_transfer_session = EnergyTransferSession(charging_station=mock_cs, electric_vehicle=mock_ev)
        assert isinstance(energy_transfer_session, InterfaceEnergyTransferSession)


    @pytest.mark.parametrize("target_power_ev, target_power_cs, expected_setpoint", [
        (PowerType(10,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW)),
        (PowerType(4,PowerTypeUnit.KW), PowerType(8,PowerTypeUnit.KW), PowerType(4,PowerTypeUnit.KW)),
        (PowerType(-10,PowerTypeUnit.KW), PowerType(-5,PowerTypeUnit.KW), PowerType(-5,PowerTypeUnit.KW)),
        (PowerType(-5,PowerTypeUnit.KW), PowerType(-8,PowerTypeUnit.KW), PowerType(-5,PowerTypeUnit.KW)),
        (PowerType(-3,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW)),
        (PowerType(3,PowerTypeUnit.KW), PowerType(-2,PowerTypeUnit.KW), PowerType(3,PowerTypeUnit.KW)),
        (None, PowerType(5,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW)),
        (PowerType(10,PowerTypeUnit.KW), None, PowerType(10,PowerTypeUnit.KW)),
        (None, None, None),
    ])
    def test_calculate_setpoint_both_targets(self, 
                                             energy_transfer_session: EnergyTransferSession,
                                             target_power_ev: PowerType,
                                             target_power_cs: PowerType,
                                             expected_setpoint: PowerType):
        energy_transfer_session.charging_station.get_target_power.return_value = target_power_cs
        energy_transfer_session.electric_vehicle.get_target_power.return_value = target_power_ev
        energy_transfer_session.calculate_setpoint()
        assert energy_transfer_session.setpoint == expected_setpoint
    

    @pytest.mark.parametrize("setpoint, max_cs_power, max_ev_power, expected_setpoint", [
        (PowerType(10,PowerTypeUnit.KW),PowerType(10,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW)),
        (PowerType(10,PowerTypeUnit.KW),PowerType(4,PowerTypeUnit.KW), PowerType(8,PowerTypeUnit.KW), PowerType(4,PowerTypeUnit.KW)),
        (None,PowerType(6,PowerTypeUnit.KW), PowerType(4,PowerTypeUnit.KW), PowerType(4,PowerTypeUnit.KW)),
        (None,None, PowerType(5,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW)),
    ])
    def test_limit_power_setpoint_charging(self,
                                       energy_transfer_session: EnergyTransferSession,
                                        setpoint: PowerType,
                                       max_cs_power: PowerType,
                                       max_ev_power: PowerType,
                                       expected_setpoint: PowerType):
        energy_transfer_session.setpoint = setpoint
        energy_transfer_session.charging_station.get_maximum_cs_charging_power.return_value = max_cs_power
        energy_transfer_session.electric_vehicle.get_maximum_charging_power.return_value = max_ev_power
        energy_transfer_session.limit_power_setpoint_charging()
        assert energy_transfer_session.setpoint == expected_setpoint


    @pytest.mark.parametrize("setpoint, max_cs_power, max_ev_power, expected_setpoint", [
        (PowerType(-10,PowerTypeUnit.KW),PowerType(10,PowerTypeUnit.KW), PowerType(5,PowerTypeUnit.KW), PowerType(-5,PowerTypeUnit.KW)),
        (PowerType(-5,PowerTypeUnit.KW),PowerType(-4,PowerTypeUnit.KW), PowerType(-8,PowerTypeUnit.KW), PowerType(-4,PowerTypeUnit.KW)),
        (PowerType(-4,PowerTypeUnit.KW),PowerType(4,PowerTypeUnit.KW), PowerType(8,PowerTypeUnit.KW), PowerType(-4,PowerTypeUnit.KW)),
        (PowerType(-1,PowerTypeUnit.KW),PowerType(2,PowerTypeUnit.KW), PowerType(3,PowerTypeUnit.KW), PowerType(-1,PowerTypeUnit.KW)),
        (None,PowerType(6,PowerTypeUnit.KW), PowerType(4,PowerTypeUnit.KW), PowerType(-4,PowerTypeUnit.KW)),
        (None,None, PowerType(5,PowerTypeUnit.KW), PowerType(-5,PowerTypeUnit.KW)),
    ])
    def test_limit_power_setpoint_discharging(self,
                                       energy_transfer_session: EnergyTransferSession,
                                        setpoint: PowerType,
                                       max_cs_power: PowerType,
                                       max_ev_power: PowerType,
                                       expected_setpoint: PowerType):
        energy_transfer_session.setpoint = setpoint
        energy_transfer_session.charging_station.get_maximum_cs_feedback_power.return_value = max_cs_power
        energy_transfer_session.electric_vehicle.get_maximum_discharging_power.return_value = max_ev_power
        energy_transfer_session.limit_power_setpoint_discharging()
        assert energy_transfer_session.setpoint == expected_setpoint

    def test_limit_power_setpoint_discharging_positive_setpoint(self,
                                                                energy_transfer_session: EnergyTransferSession):
        energy_transfer_session.setpoint = PowerType(10,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_maximum_cs_feedback_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.electric_vehicle.get_maximum_discharging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        with pytest.raises(ValueError):
            energy_transfer_session.limit_power_setpoint_discharging()


    def test_determine_charge_mode_charging(self, 
                                   energy_transfer_session: EnergyTransferSession):
        energy_transfer_session.setpoint = PowerType(10,PowerTypeUnit.KW)
        energy_transfer_session.determine_charge_mode()
        assert energy_transfer_session.mode == energy_transfer_session.mode.CHARGING

    def test_determine_charge_mode_discharging(self, 
                                   energy_transfer_session: EnergyTransferSession):

        energy_transfer_session.setpoint = PowerType(-10,PowerTypeUnit.KW)
        energy_transfer_session.determine_charge_mode()
        assert energy_transfer_session.mode == energy_transfer_session.mode.DISCHARGING

    def test_determine_charge_mode_idle(self, 
                                   energy_transfer_session: EnergyTransferSession):
        energy_transfer_session.setpoint = PowerType(0,PowerTypeUnit.KW)
        energy_transfer_session.determine_charge_mode()
        assert energy_transfer_session.mode == energy_transfer_session.mode.IDLE
    

    def test_calculate_power_setpoint_charging(self, 
                                      energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.electric_vehicle.get_target_power.return_value = PowerType(10,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_target_power.return_value = None
        energy_transfer_session.electric_vehicle.get_maximum_charging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_maximum_cs_charging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.calculate_power_setpoint()
        assert energy_transfer_session.setpoint == PowerType(5,PowerTypeUnit.KW)

    def test_calculate_power_setpoint_no_setpoint(self, 
                                      energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.electric_vehicle.get_target_power.return_value = None
        energy_transfer_session.charging_station.get_target_power.return_value = None
        energy_transfer_session.electric_vehicle.get_maximum_charging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_maximum_cs_charging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.calculate_power_setpoint()
        assert energy_transfer_session.setpoint == PowerType(5,PowerTypeUnit.KW)

    def test_calculate_power_setpoint_discharging(self, 
                                      energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.electric_vehicle.get_target_power.return_value = PowerType(-10,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_target_power.return_value = None
        energy_transfer_session.electric_vehicle.get_maximum_discharging_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.charging_station.get_maximum_cs_feedback_power.return_value = PowerType(5,PowerTypeUnit.KW)
        energy_transfer_session.calculate_power_setpoint()
        assert energy_transfer_session.setpoint == PowerType(-5,PowerTypeUnit.KW)

    
   
    def test_calculate_energy_setpoint_positive(self,
                                       energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.setpoint = PowerType(10,PowerTypeUnit.KW)
        energy_transfer_session.step_time_size = timedelta(hours=1)
        energy_transfer_session.calculate_energy_setpoint()
        assert energy_transfer_session.energy_setpoint == EnergyType(10,EnergyTypeUnit.KWH)

    def test_calculate_energy_setpoint_positive(self,
                                       energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.setpoint = PowerType(-10,PowerTypeUnit.KW)
        energy_transfer_session.step_time_size = timedelta(hours=1)
        energy_transfer_session.calculate_energy_setpoint()
        assert energy_transfer_session.energy_setpoint == EnergyType(-10,EnergyTypeUnit.KWH)
    
    def test_limit_energy_setpoint_limited(self,
                                   energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.energy_setpoint = EnergyType(10,EnergyTypeUnit.KWH)
        energy_transfer_session.electric_vehicle.get_maximum_receivable_energy.return_value = EnergyType(5,EnergyTypeUnit.KWH)
        energy_transfer_session.charging_station.get_maximum_transferable_energy.return_value = EnergyType(5,EnergyTypeUnit.KWH)
        energy_transfer_session.limit_energy_setpoint()
        assert energy_transfer_session.energy_setpoint == EnergyType(5,EnergyTypeUnit.KWH)

    def test_limit_energy_setpoint_unlimited(self,
                                   energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.energy_setpoint = EnergyType(10,EnergyTypeUnit.KWH)
        energy_transfer_session.electric_vehicle.get_maximum_receivable_energy.return_value = EnergyType(15,EnergyTypeUnit.KWH)
        energy_transfer_session.charging_station.get_maximum_transferable_energy.return_value = EnergyType(15,EnergyTypeUnit.KWH)
        energy_transfer_session.limit_energy_setpoint()
        assert energy_transfer_session.energy_setpoint == EnergyType(10,EnergyTypeUnit.KWH)
    
    def test_calculate_transfered_energy(self,
                                         energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.energy_setpoint = EnergyType(10,EnergyTypeUnit.KWH)
        energy_transfer_session.calculate_transfered_energy()
        assert energy_transfer_session.transfered_energy == EnergyType(10,EnergyTypeUnit.KWH)
    
    def test_calculate_actual_power(self,
                                     energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.transfered_energy = EnergyType(10,EnergyTypeUnit.KWH)
        energy_transfer_session.step_time_size = timedelta(hours=1)
        energy_transfer_session.calculate_actual_power()
        assert energy_transfer_session.actual_power == PowerType(10,PowerTypeUnit.KW)
    
    def test_transfer_energy(self, 
                             energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.transfer_energy()
        energy_transfer_session.electric_vehicle.charge_ev_with_energy.assert_called_once_with(energy_transfer_session.transfered_energy)
        energy_transfer_session.charging_station.give_charging_energy_over_time.assert_called_once()
        
        
    def test_perform_energy_transfer_time_is_zero(self, 
                                     energy_transfer_session: InterfaceEnergyTransferSession):
        energy_transfer_session.step_time_size = timedelta(seconds=0)
        energy_transfer_session.perform_energy_transfer()
        assert energy_transfer_session.get_transfered_energy() == EnergyType(0,EnergyTypeUnit.KWH)
        assert energy_transfer_session.get_actual_power() == PowerType(0,PowerTypeUnit.KW)

