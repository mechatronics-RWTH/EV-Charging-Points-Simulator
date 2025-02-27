import os
from config.definitions import ROOT_DIR
from SimulationModules.ElectricityCost.ElectricyPrice import PriceTable
from SimulationEnvironment.Settings import SimSettings
from datetime import timedelta
from ray.rllib.algorithms.algorithm import Algorithm
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)


#tf.compat.v1.enable_eager_execution()
from helpers.plotting import plot_trajectory

def run_rllib_policy():

    loggers = [logger]
    # for logger in loggers:
    #     logger.setLevel(logging.WARN)

    settings = SimSettings(step_time=timedelta(seconds=60),
                           sim_duration=timedelta(days=2))
    starttime = settings.start_datetime
    price_table = PriceTable(starttime=starttime)
    # train_env = register_Gym_Env(price_table=price_table,
    #                                    settings=settings,
    #                                    environment_space=standard_environment_space) # get the gym environment
    gymconfig = {'price_table': price_table,
                 'settings': settings,
                 "include_future_price": False}

    #checkpoint_path = 'D:\\021_Git\\08_Gini_V2X_Strategy\\gini_smart_charging_strategy\\Training_Data\\data_230520_0023\\checkpoint_000150'
    checkpoint_folder= 'data_230716_1100'
    checkpoint_name= 'checkpoint_001000'
    checkpoint_path= os.path.join(ROOT_DIR, 'Training_Data', checkpoint_folder,checkpoint_name)
    algo = Algorithm.from_checkpoint(checkpoint_path)

    env = algo.env_creator(algo.config.env_config)

    obs, info = env.reset()
    terminated = truncated = False
    total_reward = 0.0


    # Play one episode.
    observations_list=[obs]
    info_list_dictionary= [info]
    while not terminated and not truncated:
        # Compute a single action, given the current observation
        # from the environment.
        action = algo.compute_single_action(obs)
        # Apply the computed action in the environment.
        obs, reward, terminated, truncated, info = env.step(action)
        observations_list.append(obs)
        info_list_dictionary.append(info)

    #
        # Sum up rewards for reporting purposes.
        total_reward += reward
    # Report results.
    logger.info(f"Played 1 episode; total-reward={total_reward}")
    test=info_list_dictionary[0]
    info_dictonary_list = {k: [dic[k] for dic in info_list_dictionary] for k in info_list_dictionary[0]}


    plot_trajectory(info_dictonary_list,enable_saving=True)


if __name__ == "__main__":
    run_rllib_policy()
