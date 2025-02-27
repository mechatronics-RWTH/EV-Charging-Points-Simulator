from dataclasses import dataclass
from ray.rllib.env import BaseEnv


@dataclass
class HMARLSubEnvs:
    """HMARLSubEnvs: Dataclass for storing
    the sub-environments for the HMARL environment.
    """
    central_agent_env: BaseEnv
    termination_agent_env: BaseEnv
    gini_agent_env: BaseEnv
    gini_power_agent_env: BaseEnv

