#import logging
import os
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.algorithms.ppo import PPOConfig
from datetime import timedelta, datetime
from ReinforcementLearning.Environment.GymEnvironment import ObservationMinMaxClassWrapper
from ReinforcementLearning.Settings.SimSettings import SimSettings
from SimulationModules.ElectricityCost.ElectricyPrice import PriceTable
from config.definitions import ROOT_DIR
from helpers.setup_logger import setup_logger


def run_rllib_training():
    # setup saving path and logger
    console_log_level=10

    folder_name = 'data_' + datetime.now().strftime('%y%m%d_%H%M')
    saving_path= os.path.join(ROOT_DIR, 'Training_Data', folder_name)
    isExist = os.path.exists(saving_path)
    if not isExist:
        os.makedirs(saving_path)

    log_file_name= os.path.join(saving_path, 'training_log.log')

    logger= setup_logger(log_file_name, console_log_level)


    # settings for checkpoint
    checkpoint_folder= 'data_230715_1649'
    checkpoint_name= 'checkpoint_002000'
    path_to_checkpoint= os.path.join(ROOT_DIR, 'Training_Data', checkpoint_folder,checkpoint_name)
    RELOAD_AGENT= False

    if RELOAD_AGENT:
        algo = Algorithm.from_checkpoint(path_to_checkpoint)
    else:
        settings = SimSettings(step_time=timedelta(seconds=60),
                               sim_duration=timedelta(days=2))
        starttime = settings.start_datetime
        price_table = PriceTable(starttime=starttime)

        gymconfig={'price_table': price_table,
                    'settings': settings,
                   "include_future_price": False,
                   'charging_incentive_weight': 0,
                   'unsatisfied_customer_weight': 30}
        # Create an RLlib Algorithm instance from a PPOConfig object.
        config = PPOConfig()
        config.environment(
                # Env class to use (here: our gym.Env sub-class from above).
                env=ObservationMinMaxClassWrapper,
                # Config dict to be passed to our custom env's constructor.
                env_config=gymconfig,
                disable_env_checking=False
            )
        config=config.rollouts(num_rollout_workers=0)
        config= config.framework('torch')
        config = config.training(entropy_coeff=0.001)
        config.training(model={'fcnet_hiddens': [20, 20]})
        algo = config.build(use_copy=False)

    logger.debug(algo.config.get_learner_hyperparameters())
    logger.debug(algo.config.model)
    #logger.debug(algo.config.get_default_rl_module_spec())
    #logger.debug()


    # initalize settings for loops
    num_iterations = 170
    log_interval = 1


    for i in range(num_iterations):
        results = algo.train()
        learner_stats= results['info']['learner']['default_policy']['learner_stats']
        line ='iteration = {0} / loss = {1:.2f}, avg return = {2:.2f},'\
              ' policy_gradient_loss = {3:.4f}, value estimation loss = {4:.2f}, entropy loss ={5:.4f}'.format(
            i + 1, learner_stats['total_loss'], results['episode_reward_mean'],
            learner_stats['policy_loss'], learner_stats['vf_loss'], learner_stats['entropy'])
        logger.debug("%s" % line)



    checkpoint_dir = algo.save(saving_path)
    logger.info(f"Checkpoint saved in directory {checkpoint_dir}")

if __name__=="__main__":
    run_rllib_training()