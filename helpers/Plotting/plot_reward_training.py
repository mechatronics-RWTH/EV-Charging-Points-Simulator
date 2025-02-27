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
rcParams['legend.labelspacing'] = 0.2
rcParams['legend.handlelength'] = 1
rcParams['legend.borderpad'] = 0.1
rcParams['legend.columnspacing'] = 0.3  # Reduce space between columns
rcParams['legend.handletextpad'] = 0.1  # Reduce space between handle and text
reward_log_file_name = "Controller_Agent/Reinforcement_Learning/trained_models/reward_logs/rewards_log_2025-02-10_20-33-59.txt.json"

def format_ticks(x, pos):
    # Convert any Unicode minus signs to regular hyphens
    return f'{x:.0f}'.replace('−', '-')  # Ensure using regular hyphen

class RewardPlotter:

    def __init__(self):
        self.num_subplots = 2
        self.reward_data = None
        self.has_power_agent = False
    
    def setup_fig_settings(self):
        
        # Convert mm to inches (1 inch = 25.4 mm)
        mm_to_inches = 1 / 25.4
        fig_width_mm = 150 #192
        self.fig_width_inches = fig_width_mm * mm_to_inches
        fig_height_mm = 100
        self.fig_height_inches= fig_height_mm * mm_to_inches

    def format_axes(self):
        for ax in self.axes:
            # Apply the custom formatter to both axes
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))

    def setup_saving_path(self):
        FILE_EXTENSION = ".svg"
        # Path to the reward log file
        self.reward_log_file = pathlib.Path(reward_log_file_name)

        match = re.search(r'checkpoint_(\d{8})_(\d{6})', reward_log_file_name)
        if match:
            date_str = match.group(1)  # Extracted date: '20250206'
            time_str = match.group(2)  # Extracted time: '235455'
        else:
            match = re.search(r'log_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', reward_log_file_name)
            date_str = match.group(1).replace('-', '')  # "20250210"
            time_str = match.group(2).replace('-', '')  # "114328"

        checkpoint_name = self.reward_log_file.parent.name
        output_plot_file_name = PLOTS_DIR
        file_base_name = f"reward_training_plot_{date_str}_{time_str}"
        # Construct the output file name with checkpoint info
        self.output_plot_file_name = PLOTS_DIR / f"{file_base_name}_{checkpoint_name}{FILE_EXTENSION}"
        # Load the reward data from the JSON file

    def load_data(self):
        # Read the data from the log file
        with open(self.reward_log_file, 'r') as f:
            self.reward_data = json.load(f)

        # Extract the episode numbers
        self.episodes = list(range(len(self.reward_data)))

        # Extract rewards for specific agents
        self.gini_agent_0_rewards = [entry['agent_rewards'].get('gini_agent_0', {}).get('reward', 0) for entry in self.reward_data]
        self.gini_agent_1_rewards = [entry['agent_rewards'].get('gini_agent_1', {}).get('reward', 0) for entry in self.reward_data]
        self.gini_agent_2_rewards = [entry['agent_rewards'].get('gini_agent_2', {}).get('reward', 0) for entry in self.reward_data]

        # Compute the average reward for all central agents
        self.central_rewards = []
        for entry in self.reward_data:
            central_agents = [reward['reward'] for agent, reward in entry['agent_rewards'].items() if "central_agent" in agent]
            central_avg = np.mean(central_agents) if central_agents else 0
            self.central_rewards.append(central_avg)
        episode_reward = zip(self.episodes, self.central_rewards)
        print(list(episode_reward))

    def check_for_power_agent(self,):
        if 'gini_power_agent_0' in self.reward_data[0]['agent_rewards']:
            self.has_power_agent = True

        if self.has_power_agent:
            self.num_subplots += 1
            count =0
            self.power_agent_rewards=[]
            while f"gini_power_agent_{count}" in self.reward_data[0]['agent_rewards']:                
                self.power_agent_rewards.append([entry['agent_rewards'].get(f'gini_power_agent_{count}', {}).get('reward', 0) for entry in self.reward_data])
                count+=1



    def plot_rewards(self):
        # Create subplots
        fig, self.axes = plt.subplots(self.num_subplots, 1, figsize=(self.fig_width_inches, self.fig_height_inches), sharex=True, )
        self.format_axes()

        colors= [cm.RWTHBlau(100),  cm.RWTHSchwarz(75), cm.RWTHGruen(75)]

        # Plot each agent's rewards
        self.axes[0].plot(self.episodes, self.central_rewards, marker='o',markersize=3, linestyle='-', label=r"\$\mathcal I_{RH} average\$")
        self.axes[1].plot(self.episodes, self.gini_agent_0_rewards, marker='o',markersize=3, linestyle='-', label=r"\$I_{MCR,1}\$")
        self.axes[1].plot(self.episodes, self.gini_agent_1_rewards, marker='o',markersize=3, linestyle='-',color=colors[1],  label=r"\$I_{MCR,2}\$")
        self.axes[1].plot(self.episodes, self.gini_agent_2_rewards, marker='o',markersize=3, linestyle='-',color=colors[2],  label=r"\$I_{MCR,3}\$")
        if self.has_power_agent:
            for i,power_agent_rewards in enumerate(self.power_agent_rewards) :
                index_text = f"Rechrg, {i+1}"
                self.axes[2].plot(self.episodes, power_agent_rewards, marker='o',markersize=3, linestyle='-',color=colors[i], label=f"\$I_{{ {index_text} }}\$")

        # Add labels and legends
        for ax in self.axes:
            ax.set_ylabel(r"Total Reward / \euro")
            ax.grid(True)
            ax.legend(loc='upper left', ncols=3)

        self.axes[-1].set_xlabel(r"Episode")  # Only the last subplot gets the x-label
        for ax in self.axes:
            ax.set_xlim(left=0)  # Start x-axis at 
            ymin, ymax = ax.get_ylim()
            fac = 1.3
            if ymax < 0:
                fac = 1/fac
            ax.set_ylim(ymin, ymax * fac)
        # Set overall title
        #fig.suptitle("Agent Rewards over Episodes")

        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Show the plot
        plt.savefig(self.output_plot_file_name, format="svg")

if __name__ == "__main__":
    plotter = RewardPlotter()
    plotter.setup_fig_settings()
    plotter.setup_saving_path()
    plotter.load_data()
    plotter.check_for_power_agent()
    plotter.plot_rewards()
    print(f"Plot saved to {plotter.output_plot_file_name}")
