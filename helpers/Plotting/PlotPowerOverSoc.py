import json
import matplotlib.pyplot as plt
from matplotlib import rcParams


FILE_EXTENSION = ".pdf"
# Set the font family to Times New Roman
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 12
rcParams['text.usetex'] = True
# Convert mm to inches (1 inch = 25.4 mm)
mm_to_inches = 1 / 25.4
fig_width_mm = 90 #192
fig_width_inches = fig_width_mm * mm_to_inches

# Step 1: Import the necessary libraries

# Step 2: Load the data from the "powerOverSoc.json" file
with open('SimulationModules\\powerOverSoc.json') as file:
    data = json.load(file)
power_data = data['data']
energy_data = data['metadata']
# Step 3: Extract the x-axis values (SOC) and y-axis values (power)
soc_values = [entry['SOC']*100 for entry in power_data]

# Step 4: Create a figure with the specified width
fig, ax = plt.subplots(figsize=(fig_width_inches, 4.5),nrows=2, ncols=1, sharex=True)


# Step 7: Load the power values for all vehicles
for vehicle in power_data[0].keys():
    if vehicle == 'SOC':
        continue    
    power_values = [entry[vehicle] for entry in power_data]
    ax[0].plot(soc_values, power_values, label=vehicle)

# Step 5: Set the labels for the x-axis and y-axis
#ax[0].set_xlabel(r'SoC')
ax[0].set_ylabel(r'Power / kW')
ax[0].set_ylim(0, 500)
#ax[0].yaxis.set_major_locator(ticker.MultipleLocator(100))
ax[0].set_xlim(0, 100)
ax[0].legend(columnspacing=0.5, loc='upper right', ncol=1, fontsize=10)
ax[0].grid(True)

# Step 7: Load the power values for all vehicles
for vehicle in power_data[0].keys():
    if vehicle == 'SOC':
        continue    
    c_rate = [entry[vehicle]/energy_data[vehicle]["energyCapacity"] for entry in power_data]
    ax[1].plot(soc_values, c_rate, label=vehicle)

# Step 5: Set the labels for the x-axis and y-axis
ax[1].set_xlabel(r'SoC / \%')
ax[1].set_ylabel(r'C-Rate / 1/h')
ax[1].set_ylim(0, 3)


# Step 7: Add a grid to the plot
ax[1].grid(True)
plt.tight_layout()
# Step 8: Display the plot
plt.show()
fig.savefig('OutputData\\Plots\\PowerOverSoc.pdf', bbox_inches='tight')
