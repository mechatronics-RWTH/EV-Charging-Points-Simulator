# Python program to read
# json file
import pathlib
import json
from datetime import datetime
# import pandas lib as pd
import pandas as pd
from config.definitions import ROOT_DIR


FILEPATH = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ElectricalGrid"/"data"/"Timeseries_50.763_6.074_SA2_20kWp_crystSi_14_42deg_-3deg_2020_2020.json"

def read_data_excel(filepath: pathlib.Path,
                    usedcols = None):
    if usedcols is None:
        df_sheet_name = pd.read_excel(filepath, sheet_name='G3', header=2)
    else:
        df_sheet_name = pd.read_excel(filepath, sheet_name='G3', header=2, usecols=usedcols)
    return df_sheet_name


def read_data_json(filepath: pathlib.Path =FILEPATH):
    # Opening JSON file
    f = open(filepath)
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Closing file
    f.close()
    return data


def convert_to_datetime(datetime_str,format='%Y%m%d:%H%M') -> datetime:
    datetime_object = datetime.strptime(datetime_str, format)
    return datetime_object

