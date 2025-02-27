from SimulationModules.TrafficSimulator.DataImport import read_standard_load_data
import pathlib
from config.definitions import ROOT_DIR

def test_read_standard_load_data():
    FILEPATH_starts = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ParkingArea"/"data"/"Weekly_EV_Prob_from_STAWAG_DATA.xlsx"
    time_axis_start, probability_arrival_per_time_unit_data = read_standard_load_data(FILEPATH_starts)
    assert time_axis_start is not None
    assert probability_arrival_per_time_unit_data is not None