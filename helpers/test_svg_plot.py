import matplotlib.pyplot as plt
from matplotlib import rcParams

# Ensure text is saved as text, not paths
rcParams['svg.fonttype'] = 'none'

# Example plot
plt.plot([1, 2, 3], [4, 5, 6], label="Example Line")
plt.title("Plot Title")
plt.xlabel("X-Axis Label")
plt.ylabel("Y-Axis Label")
plt.legend()
plt.savefig("plot.svg", format="svg")