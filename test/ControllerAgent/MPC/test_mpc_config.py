from Controller_Agent.Model_Predictive_Controller.MPC_Config import MpcConfig


class TestMpcConfig:

    def test_mpc_config(self):
        mpc_config = MpcConfig.load_mpc_config(config_file="mpc_base_config.json",
                                  time_step_size=900)
        assert mpc_config.horizon_steps is not None
        assert mpc_config.solver is not None


        
