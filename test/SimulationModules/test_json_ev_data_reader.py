from SimulationModules.EvBuilder.JsonEvDataReader import JsonEvDataReader
from datetime import datetime
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricVehicle.EV import EV

class TestJsonEvDataReader:

    def test_init_reader(self):
        reader = JsonEvDataReader()
        assert isinstance(reader, JsonEvDataReader)

    def test_get_arriving_evs_from_json(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")
        assert len(reader.Evs_from_json) == 40

    def test_get_arriving_evs_from_json_is_EV(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")
        assert isinstance(reader.Evs_from_json[0], EV) 

    def test_get_arriving_evs_from_json_arrival_time(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")
        assert isinstance(reader.Evs_from_json[0].arrival_time, datetime) 

    def test_get_arriving_evs_from_json_present_energy(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")
        assert isinstance(reader.Evs_from_json[0].energy_demand_at_arrival, EnergyType) 

    def test_get_arriving_evs_from_json_parking_spot_index(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")
        for ev in reader.Evs_from_json:
            assert ev.parking_spot_index is not None  

    def test_get_arriving_evs_from_json_battery_including_power_map(self):
        reader = JsonEvDataReader()
        reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test_with_power_map.json")
        for index,ev in enumerate(reader.Evs_from_json):
            assert ev.battery.charging_power_map is not None
            assert ev.battery.charging_power_map.get_map_type() == reader.ev_data[index]['battery']['power_map_type']


        

