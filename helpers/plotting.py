import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from config.definitions import ROOT_DIR

plt.rcParams['text.usetex'] = True
plt.rcParams["font.family"] = "Arial"
plt.rcParams.update({'font.size': 11})
def plot_trajectory(data,enable_saving = False, saving_path= None, figwidth=9, figheight=6):
    if saving_path is None:
        file_name= 'plot_' + datetime.now().strftime('%y%m%d_%H%M') + '.png'
        saving_path = os.path.join(ROOT_DIR, 'plots')
        fullfile_name= os.path.join(saving_path, file_name)
    else:
        saving_path = saving_path


    fig, axs = plt.subplots(figsize=(figwidth, figheight), nrows=4,
                            ncols=1
                            )

    plt.yscale('linear')
    k=0

    axs[k].plot(data['requested_energy_kWh'],linewidth=1.5)
    axs[k].set_ylabel('$E_{requested} /kWh $')
    axs[k].set_ylim(0, 40)
    k+=1

    axs[k].plot(data['charging_power'],linewidth=1.5)
    axs[k].set_ylabel('$P_{charging} / kW$')
    axs[k].set_ylim(0, 13)
    k += 1

    axs[k].plot(data['current_price_in_cent_kWh'],linewidth=1.5)
    axs[k].set_ylabel('$c_{Energy}$')
    axs[k].set_ylim(-10, 250)
    k += 1

    axs[k].plot(np.array(data['time_to_departure_in_s']) / 60 / 60)
    axs[k].set_ylabel('$\Delta t_{departure}$')
    axs[k].set_xlabel('Step')
    axs[k].set_ylim(0, 8)

    for ax in axs:
        ax.grid(True)

    for ax in axs.flatten():  # flatten in case you have a second row at some point
        #img = ax.imshow(data, interpolation='nearest')
        ax.set_aspect('auto')

    if enable_saving:
        plt.savefig(fullfile_name)
    plt.show()

