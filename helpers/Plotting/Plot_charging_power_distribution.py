import json
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from helpers.DataAnalyzer.DataAnalyzer import DataAnalyzer
from RWTHColors import ColorManager
from SimulationModules.Enums import GiniModes
import pathlib
import scienceplots
import RWTHColors
import numpy as np
from config.definitions import PLOTS_DIR

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])

# Path to your JSON file
file_path = 'OutputData/logs/save_as_json_logs/run_2025-02-07_12-18-03/run_2025-02-07_12-18-03_trace.json'
FILE_EXTENSION = ".svg"
# Set the font family to Times New Roman
rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 11
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"

# Set default legend parameters globally
rcParams['legend.labelspacing'] = 0.2
rcParams['legend.handlelength'] = 1
rcParams['legend.borderpad'] = 0.1
rcParams['legend.columnspacing'] = 0.3  # Reduce space between columns
rcParams['legend.handletextpad'] = 0.1  # Reduce space between handle and text
# Convert mm to inches (1 inch = 25.4 mm)
mm_to_inches = 1 / 25.4
fig_width_mm = 150 #192
fig_width_inches = fig_width_mm * mm_to_inches
fig_height_mm = 70
fig_height_inches= fig_height_mm * mm_to_inches
class ChargingPowerPlotter:
    def __init__(self):
        self.fig = None
        self.ax = None
        self.filtered_ginis = None
        self.output_filename = 'charging_power_distribution.svg'
        self.output_folder = PLOTS_DIR
        self.num_plot =1

    def save_plot(self):
        output_folder_path = pathlib.Path(self.output_folder)
        output_folder_path.mkdir(parents=True, exist_ok=True)
        output_file = output_folder_path / self.output_filename
        self.fig.savefig(output_file)
        plt.close()

    def create_figure(self):
        # Create a new figure with a specific size
        self.fig, self.ax = plt.subplots(figsize=(fig_width_inches, fig_height_inches))
        self.ax.set_xlabel(r'\$P_{\text{MCR}}\$ /kW')
        self.ax.set_ylabel('Frequency')
    
        # Add legend outside the box (optional).
           
        plt.tight_layout()

    def collect_data(self, file_path= file_path):
        data_analyzer = DataAnalyzer(filename=file_path)

        # Assuming data_analyzer is defined and provides necessary methods
        gini_charging_power = data_analyzer.get_observation_by_name(name='gini_charging_power')
        gini_state = data_analyzer.get_observation_by_name(name='gini_states')
        accepted_modes = [GiniModes.CHARGING]
        # Define a function to filter based on gini states being 3 or 4
        def filter_ginis(power_data, state_data,i):
            power_data = [power[i] for power in power_data]
            state_data = [state[i] for state in state_data]
            return [
                power[1]/1000 for power,state in zip(power_data, state_data)
                if state[1] in accepted_modes and power[1] > 0
            ]

        self.filtered_ginis = {
            # Add additional ginis here if applicable
        }
        for i in range(1):
            self.filtered_ginis[f'MCR {i}'] = filter_ginis(gini_charging_power, gini_state, i)
        # Check if there is any valid data to plot
        # Check if there is any valid data to plot
            
    def add_plot(self):
        if not any(self.filtered_ginis.values()):
            print("No valid data available after filtering.")
        else:
            # Plotting using Seaborn for better aesthetics
            # Plot each dataset's distribution with distinct style/color
            for label, values in self.filtered_ginis.items():
                print(f"Plotting {label} with {len(values)} data points.")
                if values:  # Only plot non-empty datasets
                    sns.histplot(values, bins=20, kde=False, label=f"Configuration {self.num_plot}", alpha=0.7, ax=self.ax)
                    self.num_plot+=1

        self.ax.legend(loc='upper left',)#bbox_to_anchor=(0,0)) 
if __name__ == "__main__":
    plotter = ChargingPowerPlotter()
    plotter.create_figure()
    data_paths = ['OutputData/logs/save_as_json_logs/run_2025-02-11_23-59-47/run_with_checkpoint_20250210_203111_000064_trace.json',
                 'OutputData/logs/save_as_json_logs/run_2025-02-13_11-38-54/run_with_checkpoint_20250212_223601_000084_trace.json',
                 ]
    for data_path in data_paths:
        plotter.collect_data(data_path)
        plotter.add_plot()

    plotter.save_plot()

