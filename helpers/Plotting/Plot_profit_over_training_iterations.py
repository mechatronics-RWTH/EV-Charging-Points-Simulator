import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from config.definitions import PLOTS_DIR
import pathlib
import matplotlib.ticker as ticker
from RWTHColors import ColorManager
import re
import scienceplots

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])

#plt.style.use('rwth')

#matplotlib.use("SVG")
# Add 'inputenc' package to handle UTF-8 encoding
rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 11
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"
summary_log_file_name = "OutputData/summary_data/summary_data_checkpoint_20250209_152944.json"
#checkpoint_profit_training_plot_20250212_223601_summary_data
def format_ticks(x, pos):
    # Convert any Unicode minus signs to regular hyphens
    return f'{x:.0f}'.replace('−', '-')  # Ensure using regular hyphen

class ProfitPlotter:

    def __init__(self):
        self.num_subplots = 1
        self.reward_data = None
        self.has_power_agent = False
    
    def setup_fig_settings(self):
        
        # Convert mm to inches (1 inch = 25.4 mm)
        mm_to_inches = 1 / 25.4
        fig_width_mm = 150 #192
        self.fig_width_inches = fig_width_mm * mm_to_inches
        fig_height_mm = 80
        self.fig_height_inches= fig_height_mm * mm_to_inches

    def format_axes(self):
            # Apply the custom formatter to both axes
        self.axes.xaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
        self.axes.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))

    def setup_saving_path(self):
        FILE_EXTENSION = ".svg"
        # Path to the reward log file
        self.reward_log_file = pathlib.Path(summary_log_file_name)

        match = re.search(r'checkpoint_(\d{8})_(\d{6})', summary_log_file_name)
        if match:
            date_str = match.group(1)  # Extracted date: '20250206'
            time_str = match.group(2)  # Extracted time: '235455'

        checkpoint_name = self.reward_log_file.parent.name
        output_plot_file_name = PLOTS_DIR
        file_base_name = f"checkpoint_profit_training_plot_{date_str}_{time_str}"
        # Construct the output file name with checkpoint info
        self.output_plot_file_name = PLOTS_DIR / f"{file_base_name}_{checkpoint_name}{FILE_EXTENSION}"
        # Load the reward data from the JSON file

    def load_data(self):
        # Read the data from the log file
        with open(self.reward_log_file, 'r') as f:
            self.reward_data = json.load(f)

        self.iterations = [entry['iteration'] for entry in self.reward_data]
        self.profits = [entry['profit'] for entry in self.reward_data]


    def plot_profit_over_checkpoints(self):
        # Create subplots
        fig, self.axes = plt.subplots(self.num_subplots, 1, figsize=(self.fig_width_inches, self.fig_height_inches), sharex=True, )
        self.format_axes()

        # Plot each agent's rewards
        self.axes.plot(self.iterations, self.profits, marker='o',markersize=3, linestyle='-')


        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Show the plot
        plt.savefig(self.output_plot_file_name, format="svg")

if __name__ == "__main__":
    plotter = ProfitPlotter()
    plotter.setup_fig_settings()
    plotter.setup_saving_path()
    plotter.load_data()
    plotter.plot_profit_over_checkpoints()
    print(f"Plot saved to {plotter.output_plot_file_name}")
