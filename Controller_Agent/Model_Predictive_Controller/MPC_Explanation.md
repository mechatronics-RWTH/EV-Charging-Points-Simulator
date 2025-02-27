## Description

Within the scope of work an MPC based charging management considering mobile charging robots (MCRs) has been developed. The MPC framework contains three main aspects: 
* **Prediction/Forecast**: For effective charging management the controller needs a forecast about the EVs that will arrive at the parking area in the future. Currently perfect prediction and prediction with long short-term memory (LSTM) network has been investigated. The relevant files can be found here: `Controller_Agent/Model_Predictive_Controller/Prediction`

* **Mapping**: A translation between optimization formualtion and the interface to the simulation environment is needed. The realization is found here:      `Controller_Agent/Model_Predictive_Controller/EnvMpcMapping`

* **Optimization Model**: The formulation of the model can be found here: `Controller_Agent\Model_Predictive_Controller\Pyomo_Optimization_Model.py`

### Dependencies
Depending on which solver you want to use the following depencies to non-python toolboxes exist:
* Gurobi
* GLPK

### Config Settings  
| Parameter                         | Explanation                                                                                         | Default Value |
|-----------------------------------|-----------------------------------------------------------------------------------------------------|--------------|
| `N_pred`                          | Prediction horizon in time steps, defining how many future steps are considered in the optimization. | `24` |
| `solver`                          | The optimization solver used for solving the mathematical program. <br> Gurobi is a high-performance solver for linear and mixed-integer programming problems. | `"gurobi"` |
| `solver_time_limit`                | Only valid for GLPK sovler: The maximum time (in seconds) that the solver is allowed to run before terminating, <br> even if an optimal solution has not been found. | `60` |
| `solver_mip_gap`                   | Only valid for GLPK sovler: The solver's relative MIP gap tolerance, which determines how close the solution needs to be to the optimal objective before stopping. <br> A smaller value ensures better solutions but increases computation time. | `0.05` |
| `show_solver_output`               | If set to `true`, the solver's detailed logs and outputs will be displayed during execution, <br> which can be useful for debugging or analysis. | `false` |
| `selling_cost_in_euro_per_kwh`     | The price per kilowatt-hour (kWh) at which energy is sold. <br> This parameter directly affects revenue calculations in energy transactions. | `0.5` |
| `use_slack_weight_end_of_horizon`  | If enabled, slack weighting is applied at the end of the prediction horizon <br> to reduce constraint violations or improve feasibility in long-term planning. | `false` |
| `use_linearized_model`             | If set to `true`, a simplified linear model is used instead of a MILP model, <br> which can speed up computation but may reduce accuracy. In most cases this is not a good choice for given problem. | `false` |
| `prediction_mode`                  | The prediction method used for forecasting energy demand, availability, or system behavior. <br> In this case, an LSTM (Long Short-Term Memory) neural network is used for time-series prediction. Other choices would be "perfect" or "noprediction" | `"lstm"` |
| `moving_penalty`                   | A penalty cost applied for movement, <br> used to discourage unnecessary repositioning of mobile units (e.g., charging robots) in the optimization process. | `0.01` |
| `prediction_data_path`             | The file path where the prediction input data is stored. <br> If left empty, no external prediction data will be loaded. This is only used in case of perfect prediction. It will only lead to useful perfect prediction if same file as in simulation environment (see env config file) is used. | `""` |
| `lstm_model_path`                  | The file path to the trained LSTM model and scaler, <br> which are used for generating predictive inputs in the optimization model. | `"Controller_Agent/.../lstm_model_and_scaler_augmented_simple_comp.joblib"` |



### Tools and Limitations 
The general approach is developed using [Pyomo](https://www.pyomo.org/) for formulation of the optimization problem and either [glpk](https://www.gnu.org/software/glpk/) or [gurobi](https://www.gurobi.com/academia/academic-program-and-licenses/?gad_source=1&gclid=CjwKCAiAlPu9BhAjEiwA5NDSA8wYQMLKh-lLkdR3saTPPW7mkP4DYFIatRw_pUsZ_pdu-4KEu1PUnxoCXZoQAvD_BwE) solver. While the glpk solver is open source and works well for problems with smaller problems (meaning small prediction horizons, few parking spots, only one MCR) no settings have been found to use it effectively with larger problems. In contrast, gurobi requires a (academic) license, but was also capable of solving larger problems. However, it also required modification of the settings. Otherwise the gurobi solver gets "stuck" as well. 


## How to use
The main file for testing the MPC is `Controller_Agent\Model_Predictive_Controller\test_MPC.py`. **Note**: Ideally, in future the MPC is migrated into the `Main.py` by adding it to the agent factory `Controller_Agent\AgentFactory.py`. In order to run the simulation a couple of steps need to be followed:



### Configure your environment
* Select and or modify a config file (e.g. `config\env_config\Benchmark\comparison_spring.json`)
* Add the config file to the MPC test file by changing the respective parameter in `Controller_Agent\Model_Predictive_Controller\test_MPC.py` 
    ```
    ENVIRONMENT_CONFIG = "config/env_config/env_config_MPC_test.json" 
    ```

### Configure the MPC 
* Selcting your MPC configuration e.g. `Controller_Agent/Model_Predictive_Controller/config/mpc_lstm_24_no_slack_move_penalty.json`
* Add the MPC config to `Controller_Agent\Model_Predictive_Controller\test_MPC.py`
    ```
    MPC_CONFIG="Controller_Agent/Model_Predictive_Controller/config/mpc_lstm_24_no_slack_move_penalty.json"
    ```

#### Train LSTM
In case you want to use LSTM prediction, you need to train the LSTM beforehand or use one of the once available. The available LSTM are found here, named based on the dataset they used: `Controller_Agent\Model_Predictive_Controller\Prediction\LSTM\models`
If you want to train a new LSTM, use `Controller_Agent\Model_Predictive_Controller\Prediction\LSTM\LSTMTrainer.py`. 
If you have your LSTM, you can add it via the "lstm_model" parameter in the mpc config. Please ensure that it is trained with same prediction horizon as used in the MPC.

#### Perfect prediction
In case you want to test MPC with perfect prediction for EV arrivals, departues and energy requests, you can add the corresponding recording e.g.: `config\traffic_sim_config\arriving_evs_record_2024-11-14_14-42-04.json`.  
**IMPORTANT**:To have an actual perfect prediction it needs to be the same as the once used in the Env Config.

### Running and see results
Once configured you can run `Controller_Agent\Model_Predictive_Controller\test_MPC.py` and the results will be saved as json or even plotted depending on the options you have set ("SAVE_JSON" and "OUTPUT_GRAPHS" in the test_MPC.py).