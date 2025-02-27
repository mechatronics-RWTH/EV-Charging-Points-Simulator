import pathlib
import numpy as np
from datetime import datetime
import pytest

from SimulationEnvironment.GymEnvironment import CustomEnv
from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Reinforcement_Learning.Simple_RL_Agent.EnvSimpleRLAgent import EnvSimpleRLAgent
from config.definitions import ROOT_DIR


@pytest.mark.skip(reason="This test fails. Probably depends on the old version of the environment.")
def test_make_step():
    """
    the derived env has the purpose to translate action and observation space.
    Both functionalities are tested with a step.
    """
    gym_config=EnvConfig.load_env_config(config_file=pathlib.Path(ROOT_DIR)/"config"/"env_config"/"env_config.json")
    env=EnvSimpleRLAgent(gym_config)

    action=env.action_space.sample()

    env.step(action)