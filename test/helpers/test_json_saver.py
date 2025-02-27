import pytest
import os
import json
from helpers.JSONSaver import JSONSaver, object_to_dict, comp_data, JsonReader
from SimulationEnvironment.GymEnvironment import CustomEnv
from SimulationEnvironment.EnvConfig import EnvConfig

from Controller_Agent.Rule_based.RuleBasedAgent import RuleBasedAgent_One
import time
from config.logger_config import get_module_logger


logger = get_module_logger(__name__)

@pytest.fixture
def json_saver() -> JSONSaver:
    return JSONSaver()
    # with JSONSaver() as saver:
    #     yield saver # provide the fixture value


@pytest.fixture
def json_reader() -> JsonReader:
    return JsonReader()
    # with JSONSaver() as saver:
    #     yield saver # provide the fixture value


@pytest.fixture(scope="function")
def gym_environment():
    gym_config = EnvConfig.load_env_config(config_file="test/env_config_test.json")
    #endregion

    env=CustomEnv(config=gym_config)
    return env

@pytest.fixture
def json_data():
    return [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]

def test_read_data(json_saver, tmp_path, json_data, json_reader):
    # Create a temporary json file
    p = tmp_path / "data.json"
    p.write_text(json.dumps(json_data))

    # Call the read_data method
    result = json_reader.read_data(str(p))

    # Check that the result matches the original data
    assert result == json_data

def test_to_dict(gym_environment):

    observations = {key: object_to_dict(value) for key, value in gym_environment.observation_raw.items()}

    actions = {key: object_to_dict(value) for key, value in gym_environment.action_raw_base.items()}
    assert observations.keys() == gym_environment.observation_raw.keys()
    assert actions.keys() == gym_environment.action_raw_base.keys()
    assert observations['grid_power'][0] !=0
    
@pytest.fixture
def random_dict(gym_environment):
    observations = {key: object_to_dict(comp_data(value)) for key, value in gym_environment.observation_raw.items() if key not in ["distances", "field_kinds"]}

    actions = {key: object_to_dict(comp_data(value)) for key, value in gym_environment.action_raw_base.items()}
    data = {
            'observations': observations,
            'actions': actions
        }
    return data 


    

def test_save_gym_environment(json_saver, gym_environment):
    # Save the gym environment as JSON

    json_saver.add_data(gym_environment.observation_raw, gym_environment.action_raw_base)
    json_saver.save_to_json()
    #print(gym_environment.observation_raw)
    # Check if the JSON file exists
    assert os.path.exists(json_saver.file_name)

    # Load the saved JSON file
    with open(json_saver.file_name, "r") as f:
        saved_data = json.load(f)
    print(f'Loaded data: {saved_data}')
    # Check if the loaded data matches the original gym environment
    #assert saved_data == gym_environment.to_dict()

    # Clean up the JSON file
    os.remove(json_saver.file_name)


def test_read_saved_gym_data(json_saver, gym_environment,json_reader):
    counter=0
    json_saver.add_data(gym_environment.observation_raw, gym_environment.action_raw_base)
    agent=RuleBasedAgent_One()
    while counter <5:
        counter=counter+1
        action=agent.calculate_action(gym_environment.observation_raw, gym_environment.action_raw_base)
        gym_environment.step(action)
        json_saver.add_data(gym_environment.observation_raw, gym_environment.action_raw_base)
        #gym_environment.render()
        time.sleep(0.1)
    json_saver.save_to_json()

    data = json_reader.read_data(json_saver.file_name)
    print(data)
    # Clean up the JSON file
    os.remove(json_saver.file_name)

#now we make the tests for the compressed version of the saved data
def test_to_dict_comp(json_saver, gym_environment):

    observations = {key: object_to_dict(comp_data(value)) for key, value in gym_environment.observation_raw.items() if key not in ["distances", "field_kinds"]}

    actions = {key: object_to_dict(comp_data(value)) for key, value in gym_environment.action_raw_base.items()}
    assert observations['grid_power'][0] !=0
    
def test_save_json_array(json_saver, random_dict,json_reader):
    expected_length= 4
    expected_data = [random_dict for _ in range(expected_length)]
    for _ in range(expected_length):
        json_saver.add_data_comp(observations=random_dict['observations'], actions=random_dict['actions'])
    json_saver.save_to_json()
    
    data = json_reader.read_data(json_saver.file_name)
    logger.info(f'Loaded data: {data}')
    assert data is not None
    assert len(data) == expected_length
    assert data == expected_data

def test_save_gym_environment_comp(json_saver, gym_environment):
    # Save the gym environment as JSON
    json_saver.add_data_comp(gym_environment.observation_raw, gym_environment.action_raw_base)
    json_saver.save_to_json()

    # Check if the JSON file exists
    assert os.path.exists(json_saver.file_name)

    # Load the saved JSON file
    with open(json_saver.file_name, "r") as f:
        saved_data = json.load(f)
    print(f'Loaded data: {saved_data}')
    # Check if the loaded data matches the original gym environment
    #assert saved_data == gym_environment.to_dict()

    # Clean up the JSON file
    os.remove(json_saver.file_name)


def test_read_saved_gym_data_comp(json_saver, gym_environment,json_reader):
    counter=0
    agent=RuleBasedAgent_One()
    json_saver.add_data_comp(gym_environment.observation_raw, gym_environment.action_raw_base)
    while counter <5:
        counter=counter+1
        action=agent.calculate_action(gym_environment.observation_raw, gym_environment.action_raw_base)
        gym_environment.step(action)
        json_saver.add_data_comp(gym_environment.observation_raw, gym_environment.action_raw_base)
        #gym_environment.render()
        time.sleep(0.01)
    json_saver.save_to_json()

    
    data = json_reader.read_data(json_saver.file_name)
    logger.info(f'Loaded data: {data}')
    assert data is not None
    assert data[1] is not None    
    assert data[1]['observations'] is not None
    #logger.info(f"Loaded data: {data[1]['observations']}")
    # Clean up the JSON file
    os.remove(json_saver.file_name)

def test_save_config_in_output_folder(json_saver:JSONSaver):
    json_saver.config_file_name = "test/helpers/env_config_test.json"
    json_saver.save_config_in_output_folder("test/env_config_test.json",
                                            copy_file_name="mpc_config.json")
    assert os.path.exists("test/helpers/mpc_config.json")
    os.remove("test/helpers/mpc_config.json")
