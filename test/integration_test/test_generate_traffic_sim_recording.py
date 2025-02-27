import pytest
from helpers.generate_traffic_sim_recording import generate_traffic_sim_recording
import os

def test_generate_traffic_sim_recording():
    config_path = "test\\env_config_test.json"
    path = "test\\integration_test\\test_generate_traffic_sim_recording.json"
    generate_traffic_sim_recording(config_path=config_path,
                                   output_file_name=path)
    assert os.path.exists(path) == True
    os.remove(path)