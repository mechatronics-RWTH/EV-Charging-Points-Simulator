from ray.rllib.algorithms.algorithm_config import AlgorithmConfig

"""
This file implements the RL Algorithm Selector.

The RL Algorithm Selector determines and configures the reinforcement learning algorithm
based on a provided index, enabling flexible and modular multi-algorithm setups.

"""


def import_algorithm_config(rl_algorithm) -> AlgorithmConfig:
    if rl_algorithm == 0:
        from ray.rllib.algorithms.ppo import PPOConfig
        return PPOConfig()
    elif rl_algorithm == 1:
        from ray.rllib.algorithms.appo import APPOConfig
        return APPOConfig()
    elif rl_algorithm == 2:
        from ray.rllib.algorithms.pg import PGConfig
        return PGConfig()
    elif rl_algorithm == 3:
        from ray.rllib.algorithms.sac import SACConfig
        return SACConfig()
    elif rl_algorithm == 4:
        from ray.rllib.algorithms.dqn import DQNConfig
        return DQNConfig()
    elif rl_algorithm == 5:
        from ray.rllib.algorithms.a2c import A2CConfig
        return A2CConfig()
    elif rl_algorithm == 6:
        from ray.rllib.algorithms.a3c import A3CConfig
        return A3CConfig()
    elif rl_algorithm == 7:
        from ray.rllib.algorithms.impala import ImpalaConfig
        return ImpalaConfig()
    elif rl_algorithm == 9:
        from ray.rllib.algorithms.r2d2 import R2D2Config
        return R2D2Config()
    else:
        raise ValueError(f"Invalid rl_algorithm value: {rl_algorithm}. Must be between 0 and 7 or 9.")


