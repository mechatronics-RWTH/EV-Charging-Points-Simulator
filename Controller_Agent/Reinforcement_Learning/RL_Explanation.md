## Description

Within the scope of work a RL based charging management considering mobile charging robots (MCRs) has been developed. The RL controller combines multi-agent RL and hierarchical RL to a HMARL framework. The HMARL framework requires a wrapper around the Simulation environment, because the multi-agent framework does provide a dictionary of observations, actions and rewards. Therefore, in `Controller_Agent\Reinforcement_Learning\RLModules\Environments\HMARLEnvironment.py` this wrapper is provided. It basically conducts many MARL steps and gathers the actions of the individual agents before applying those to the real environment. 


### Config Settings  
The RL algorithm including architecture can be configured here: `Controller_Agent\Reinforcement_Learning\config\algo_configs`
Configurations for training can be found here: `Controller_Agent\Reinforcement_Learning\config\trainer_configs`. The parameters are described within the comments of the respective .yaml file.


### Tools and Limitations 
The general approach is developed [RLLib](https://docs.ray.io/en/latest/rllib/index.html) and [gymnasium](https://gymnasium.farama.org/index.html).


## How to use
Trainings can be started with `Controller_Agent\Reinforcement_Learning\Training\RLTraining_main.py`. The configuration for training are set in `Controller_Agent\Reinforcement_Learning\config\trainer_configs\trainer_config_base.yaml` and for the algorithm and architecture used in `Controller_Agent\Reinforcement_Learning\config\algo_configs\algo_config_base.yaml`. 

### Running and see results
During training checkpoints are saved in `Controller_Agent\Reinforcement_Learning\trained_models`. Within `Controller_Agent\Reinforcement_Learning\TestRlAlgorithm\RLTest_main.py` these can be loaded and the strategy can be applied to the simulation environment.