import pathlib
from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from config.definitions import ROOT_DIR

def test_load_env_config():

    gym_config=EnvConfig.load_env_config(config_file=pathlib.Path(ROOT_DIR)/ "test" / "env_config_test.json")
    assert gym_config["customers_per_hour"]==2
    assert gym_config["max_charging_power"].value==11
    assert gym_config["max_grid_power"].value==1000
    assert gym_config["max_building_power"].value==500
    assert len(gym_config["pred_building_power"])==96
    assert gym_config["max_pv_power"].value==250
    assert gym_config["pv_area_in_m2"]==75
    assert len(gym_config["pred_pv_power"])==96
    assert gym_config["max_parking_time"].seconds==7200
    assert gym_config["max_energy_request"].value==100
    assert gym_config["max_ev_energy"].value==100
    assert gym_config["max_gini_energy"].value==100
    assert gym_config["assigner_mode"]=="charging_station"
    assert gym_config["Gini_starting_fields"]== [13,7,9]


def test_load_env_config_stationary_storage():
    gym_config=EnvConfig.load_env_config(config_file=pathlib.Path(ROOT_DIR)/"test"/"env_config_stationary_storage_one.json")
    print(gym_config["stationary_batteries"])
    stat_battery = gym_config["stationary_batteries"]
    assert isinstance(stat_battery, StationaryBatteryStorage)
    assert stat_battery.battery_energy.value==100
    assert stat_battery.present_energy.value==50

