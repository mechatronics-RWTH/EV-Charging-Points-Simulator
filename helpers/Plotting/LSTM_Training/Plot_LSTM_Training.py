import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import pathlib
import matplotlib.ticker as ticker
from RWTHColors import ColorManager
from config.definitions import PLOTS_DIR
import re
import scienceplots

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])

rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 11
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"
history_json_path = "Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/training/training_history_jpl.json" #os.path.join(relative_path, 'models', f'training_history_{dataset}.json')

def plot_lstm_training(history_json_path):
    file_based_name = re.search(r"training_history_(.*).json", history_json_path).group(1)
    output_plot_file_name = PLOTS_DIR / f"{file_based_name}_training_loss.svg"
    # Convert mm to inches (1 inch = 25.4 mm)
    mm_to_inches = 1 / 25.4
    fig_width_mm = 150 #192
    fig_width_inches = fig_width_mm * mm_to_inches
    fig_height_mm = 70
    fig_height_inches= fig_height_mm * mm_to_inches

    # Load training history from JSON
    with open(history_json_path, 'r') as f:
        history = json.load(f)

    # Plot training and validation loss
    fig = plt.figure(figsize=(fig_width_inches, fig_height_inches))
    plt.plot(history['loss'], label='Training Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    #plt.show()
    plt.savefig(output_plot_file_name, format="svg")

if __name__ == "__main__":
    plot_lstm_training(history_json_path)
