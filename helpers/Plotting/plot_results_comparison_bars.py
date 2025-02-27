import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from RWTHColors import ColorManager
import re
import scienceplots
import matplotlib.ticker as ticker
from config.definitions import PLOTS_DIR
from matplotlib.ticker import MaxNLocator, MultipleLocator
import json 

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])


# Add 'inputenc' package to handle UTF-8 encoding
rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 12
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"
rcParams['legend.labelspacing'] = 0.0
rcParams['legend.handlelength'] = 1
rcParams['legend.borderpad'] = 0.4
rcParams['legend.columnspacing'] = 0.7  # Reduce space between columns
rcParams['legend.handletextpad'] = 0.2  # Reduce space between handle and text

JSON_FILE =  r"OutputData\diss_results\Final_Profit_Comparison.json"#"OutputData/diss_results/kWh_charged_comparison.json"#r"OutputData\diss_results\User_satisfaction_comparison.json"##"OutputData/diss_results/kWh_charged_comparison.json"

def format_ticks(x, pos):
    # Convert any Unicode minus signs to regular hyphens
    return f'{x:.0f}'.replace('−', '-')  # Ensure using regular hyphen

class ComparisonBarPlot:

    def load_data(self,
                  json_file: str = JSON_FILE):
        with open(json_file) as f:
            plots_config = json.load(f)
        self.algorithms = plots_config['data']['algorithms']
        self.seasons = plots_config['data']['seasons']
        self.results = plots_config['data']['results']
        self.y_label = plots_config['y_axis_title']
        self.file_name = plots_config['file_name']

        # Number of algorithms and seasons
        self.n_algorithms = len(self.algorithms)
        self.n_seasons = len(self.seasons)

    def define_figure(self):
        # Setup the figure size and style for better aesthetic        
        # Convert mm to inches (1 inch = 25.4 mm)
        mm_to_inches = 1 / 25.4
        fig_width_mm = 150 #192
        self.fig_width_inches = fig_width_mm * mm_to_inches
        fig_height_mm = 70
        self.fig_height_inches= fig_height_mm * mm_to_inches
        self.fig, self.ax = plt.subplots(nrows=1,ncols=1,figsize=(self.fig_width_inches, self.fig_height_inches))

    def format_axes(self):
        #self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
        self.ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))

    def plot_bars(self):
        # Define positions for groups on x-axis (one position per season)
        index = np.arange(self.n_seasons)

        # Width of bars (adjust if needed for spacing)
        bar_width = 0.15

        # Increase space between groups by adjusting initial position
        group_offset = 0.15

        # Colors for different algorithms (customize as needed)
        colors = [cm.RWTHOrange(100), cm.RWTHGruen(100), cm.RWTHBlau(100), cm.RWTHBlau(50) ]

        print(f"Algorithms: {self.algorithms}")
        print(f"Seasons: {self.seasons}")
        # Plotting bars for each algorithm within the same group position
        for i in range(self.n_algorithms):
            self.ax.bar(index + i * bar_width + group_offset,
                        [self.results[season][i] for season in self.seasons],
                        width=bar_width,
                        color=colors[i],
                        edgecolor='black',  # Add edge color
                        label=self.algorithms[i],
                        alpha=0.9,  # Transparency level
                        zorder=3)  # Draw above grid lines

        
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins='auto', integer=True, prune=None))
        # Adding labels and title
        self.ax.set_xlabel('Season')
        self.ax.set_ylabel(self.y_label)
        if "Profit" in self.y_label :
            self.ax.yaxis.set_minor_locator(MultipleLocator(20))
            self.ax.set_ylim(-120, 400)
        elif "Satisfaction" in self.y_label:
            self.ax.set_ylim(-23, -10)
        elif "kWh" in self.y_label:
            self.ax.set_ylim(500, 2000)

        self.ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.3)
        
        
        # Set x-ticks with appropriate labels centered between groups
        middle_of_group_positions = index + bar_width * (self.n_algorithms / 2) + group_offset / 2
        self.ax.set_xticks(middle_of_group_positions)
        self.ax.set_xticklabels(self.seasons)

        # Add legend to distinguish between algorithms
        plt.legend(ncols=4, loc='upper left', bbox_to_anchor=(0.0, 1.02), frameon=True)

        # Improve layout and show grid lines with customization
        plt.tight_layout()
        
        # Customize grid lines and ticks 
        self.ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.6)
        self.ax.tick_params(axis='x', which='both', length=5)
        self.format_axes()

        self.output_plot_file_name = PLOTS_DIR / self.file_name
        # Show the plot
        plt.savefig(self.output_plot_file_name, format="svg")


if __name__ == '__main__':
    json_file = JSON_FILE
    plotter = ComparisonBarPlot()
    plotter.load_data(json_file=JSON_FILE)
    plotter.define_figure()
    plotter.plot_bars()
    