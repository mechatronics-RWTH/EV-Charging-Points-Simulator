# Mobile smart charging robot - Operating and charging strategy

## Description

This project provides an environment for simulating a mobile smart charging robot. It can be used for simulating different scenarios and comparing different operating strategies. The mobile charging robot named **GINI** consists of a battery with CCS DC charging interfaces for charging Electric vehicles and recharging itself. 

While an actual prototype is build within an research project founded by german ministry BMWK, this repository should help to 

* Evaluate the potential of mobile charging robots in different scenarios with varying user requirements
* Test different smart charging and energy management strategies for a GINI or a fleet of GINIs
* Provide a base for testing reinforcement learning algorithms 
* Offer a template for general charging management simulation and algorithm development 

## Getting Started

### Dependencies

* Python
* Latex (if you want to generate plots with Latex font - as per default)
    * For Windows follow [this](https://miktex.org/howto/install-miktex)
    * For Linux (Ubuntu): `sudo apt-get install texlive texlive-latex-extra texlive-fonts-recommended dvipng`
* Poetry for dependency management

### Installing with poetry (recommended)

* Clone the repository
* Install Poetry if you haven't already. 

```bash
pip install poetry
```

* Install the project dependencies using Poetry:
```bash
poetry install
```
* Activate poetry 
```bash
poetry shell
```
* If you encouter problems refer to the [Poetry Documentation](https://python-poetry.org/docs/)

### Installing with venv 
```bash
pip install -r requirements.txt
```

### Config Settings
| Parameter      | Default Value          | Explanation                                                                            |
|----------------|------------------------|----------------------------------------------------------------------------------------|
| `RENDER`       | `true`                 | Indicates whether the rendering/live visualitation should be executed.                            |
| `SAVE_JSON`    | `true`                 | Specifies if the output data should be saved.                         |
| `OUTPUT_GRAPHS`| `true`                 | Controls whether graphs should be generated and displayed.                             |
| `FOLDERPATH`   | `"config\\Paper"`      | The path where files, from where the config files are loaded.                      |
| `LOOP`         | `false`                | If this parameter is set, it runs multiple configs (from `FOLDERPATH`)  in a loop.  |

## Executing program
In order to execute a simulation run, the following steps need to be executed: 
* Create or modify a config file e.g. `config/env_config/env_config gini_1day.json`. For detailed information about the configuration parameters, please refer to the [Configuration Parameters](config/env_config/env_configuration_parameters.md) file.
* Open `Main.py` and change the path of the file config file `run_main`(fullfilename="config/env_config gini_1day.json"). Deactivate the Loop function `LOOP: false` in `main_config.json`.
* Ensure that you have installed and acitvated the poetry venv and execute the Main.py: `python Main.py` 

## Visualisizing results
If you have activated the options `RENDER: true`  and `OUTPUT_GRAPHS: true` in the `main_config.json` the results should be saved into the `OutputData/Plots` or `OutputData/videos` folder at the end of the simulation, respectively. The plots can be generated again by running `python helpers\Plot_json_logs.py` or executing the file via your IDE. You can change the output file format in the line containing `FILE_EXTENSION = ".svg"` for example to PDF or PNG format. In the corresponding file the name of the json logs need to be provided e.g. `run_2024-07-27_13-31-13_trace.json`.

## Comparing control strategies
Usually the environment provides some degree of stochastic behavior, especially for EV statistics (arrival and departure time, battery characteristics etc.). This might not be desired if different strategies are supposed to be compared. Therefore, a recording and replay functionality is provided. With `helpers/generate_traffic_sim_recording.py` the behavior can be saved in a json e.g. `config\traffic_sim_config\arriving_evs_record_2024-11-08_16-30-30.json` and be replayed by providing it as "recording_data_path" field within the env_config file you are using. 

NOTE: The env_config will be checked if it fits with the recording. If e.g. the start dates differ an error will be thrown. Same if the assigner_mode is not set to "fixed" in the env_config. 

### MPC based control strategy 
To use the MPC based control strategy, please see the explanation [Controller_Agent/Model_Predictive_Controller/MPC_Explanation.md](Controller_Agent/Model_Predictive_Controller/MPC_Explanation.md).

### RL based control strategy
To use the RL based control strategy, please see the explanation [Controller_Agent/Reinforcement_Learning/RL_Explanation.md](Controller_Agent/Reinforcement_Learning/RL_Explanation.md).

**Note**: As the MPC and RL strategy have been integrated with the primary purpose of performing research and investigation in the scope of thesis, the usability might not always be on point. If issues or questions come up feel free to follow the instructions in help sections or contact the author. 


## Help

If you encounter any problems or have any questions about this project, please open an issue in this repository.

## Authors

* Max Faßbender (max.fassbender@rwth-aachen.de)
* Milan Kopynske

## License

This project is licensed under the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) - see the LICENSE file for details

