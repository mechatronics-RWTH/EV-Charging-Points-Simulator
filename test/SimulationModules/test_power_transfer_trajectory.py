import pytest
from SimulationModules.ChargingSession.PowerTransferTrajectory import PowerTransferTrajectory
from datetime import datetime
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.datatypes.EnergyType import EnergyType

NUM_ENTRIES = 10    

@pytest.fixture
def power_transfer_trajectory():
    power_transfer_trajectory = PowerTransferTrajectory()
    for _ in range(NUM_ENTRIES):
        power_transfer_trajectory.add_entry(power=PowerType(10),
                                            time=datetime.now(),
                                            requested_energy=EnergyType(10),
                                            energy=EnergyType(10))
    return power_transfer_trajectory


class TestPowerTransferTrajectory:

    def test_power_transfer_trajectory(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        assert power_transfer_trajectory.time_trajectory == []
        assert power_transfer_trajectory.power_trajectory == []
        assert power_transfer_trajectory.energy_trajectory == []
        assert power_transfer_trajectory.requested_energy_trajectory == []

    def test_add_entry_wrong_datetime(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        with pytest.raises(ValueError):
            power_transfer_trajectory.add_entry(power=PowerType(10), 
                                                time="2021-01-01 00:00:00",
                                                requested_energy=EnergyType(10),
                                                energy=EnergyType(10))

    def test_add_entry_wrong_power(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        with pytest.raises(ValueError):
            power_transfer_trajectory.add_entry(power=10, 
                                                time=datetime.now(),
                                                requested_energy=EnergyType(10),
                                                energy=EnergyType(10))
            
    def test_add_entry_wrong_energy(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        with pytest.raises(ValueError):
            power_transfer_trajectory.add_entry(power=PowerType(10), 
                                                time=datetime.now(),
                                                requested_energy=EnergyType(10),
                                                energy=10)
            
    def test_add_entry_wrong_requested_energy(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        with pytest.raises(ValueError):
            power_transfer_trajectory.add_entry(power=PowerType(10), 
                                                time=datetime.now(),
                                                requested_energy=10,
                                                energy=EnergyType(10))


    def test_add_entry_correct(self):
        power_transfer_trajectory = PowerTransferTrajectory()
        power_transfer_trajectory.add_entry(power=PowerType(10), 
                                            time=datetime.now(),
                                            requested_energy=EnergyType(10),
                                            energy=EnergyType(10))

        assert power_transfer_trajectory.time_trajectory != []
        assert power_transfer_trajectory.power_trajectory != []

    def test_get_energy_trajectory(self,
                                   power_transfer_trajectory: PowerTransferTrajectory):
        energy_trajectory=power_transfer_trajectory.get_energy_trajectory()
        assert len(energy_trajectory) == NUM_ENTRIES


    def test_get_power_trajectory(self,
                                    power_transfer_trajectory: PowerTransferTrajectory):
        power_traj=power_transfer_trajectory.get_power_trajectory()
        assert len(power_traj) == NUM_ENTRIES

    def test_get_time_trajectory(self,
                                 power_transfer_trajectory: PowerTransferTrajectory):
        time_traj=power_transfer_trajectory.get_time_trajectory()
        assert len(time_traj) == NUM_ENTRIES
    
    def test_get_last_energy_value(self,
                                   power_transfer_trajectory: PowerTransferTrajectory):
        last_energy_value=power_transfer_trajectory.get_last_energy_value()
        assert last_energy_value == EnergyType(10)

    def test_get_last_energy_value_changed(self,
                                   power_transfer_trajectory: PowerTransferTrajectory):
        power_transfer_trajectory.energy_trajectory[-1]=EnergyType(20)
        last_energy_value=power_transfer_trajectory.get_last_energy_value()
        assert last_energy_value == EnergyType(20)

    def test_get_start_energy_request(self,
                                      power_transfer_trajectory: PowerTransferTrajectory):
        power_transfer_trajectory.requested_energy_trajectory[0]=EnergyType(20)
        power_transfer_trajectory.requested_energy_trajectory[1]=EnergyType(30)
        start_energy_request=power_transfer_trajectory.get_start_energy_request()
        assert start_energy_request == EnergyType(20)

    def test_get_end_energy_request(self,
                                    power_transfer_trajectory: PowerTransferTrajectory):
        power_transfer_trajectory.requested_energy_trajectory[-1]=EnergyType(20)
    
        end_energy_request=power_transfer_trajectory.get_end_energy_request()
        assert end_energy_request == EnergyType(20)
    
