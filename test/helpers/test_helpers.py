import pathlib

import pytest
import numpy as np


from helpers.data_handling import convert_to_datetime, read_data_json, read_data_excel
from config.definitions import ROOT_DIR



@pytest.fixture()
def mock_nparray():
   array=np.random.rand(1000, 4)
   return array

def test_read_data():
    data= read_data_json()
    #logger.info(data)
    output_data=data['outputs']['hourly']

    #logger.info(output_data)

def test_convert_str_to_datetime():
    example_time='20200101:0010'
    time = convert_to_datetime(example_time)
    #logger.info(time)

def test_filter_data():
    startdate= convert_to_datetime('20200101:0010')
    endtime=convert_to_datetime('20200201:0010')
    data= read_data_json()
    output_data=data['outputs']['hourly']
    expected_result = [d for d in output_data if (convert_to_datetime(d['time'])>startdate and convert_to_datetime(d['time'])<endtime)]
    #logger.info(expectedResult)

def test_read_data_excel():

    FILEPATH = pathlib.Path(ROOT_DIR)/"SimulationModules"/"ElectricalGrid"/"data"/"Repräsentative Profile VDEW.xls"
    data=read_data_excel(FILEPATH)
    #logger.info(data)






