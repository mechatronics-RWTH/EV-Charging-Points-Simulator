import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

def plot_stacked(time,
                 data,
                 labels= None,
                 ax = None,):
    if not isinstance(data, np.ndarray):
        ValueError('Data is not of type np.array')
    # split data into negative and positive values
    data_positive = np.copy(data)
    data_positive[data_positive<=0]=0
    data_negative = np.copy(data)
    data_negative[data_negative>=0]=0

    keys=list(mcolors.BASE_COLORS.keys())
    colors= [mcolors.BASE_COLORS[keys[x]] for x in range(data.shape[0])]
    if labels is None:
        label= colors
    else:
        label= labels

    if ax is None:
        # initialize stackplot
        fig, ax = plt.subplots(nrows=1, ncols=1, facecolor="#F0F0F0")
        # create and format stackplot
    else: ax = ax
    ax.stackplot(time, data_positive, colors= colors)
    ax.stackplot(time,data_negative, colors= colors, labels = label)

    ax.legend(loc='upper left')
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_ylim(bottom=np.min(data)*1.5, top=np.max(data)*1.5)
    ax.grid(which="major", color="grey", linestyle="--", linewidth=0.5)


if __name__ == "__main__":
    example_data= np.random.randn(4,100)*100 -50
    time = np.linspace(0, 7 * 60 * 60, 100)
    labels = ["House", "PV", "Grid", "Charger"]

    plot_stacked(time, example_data, labels=labels)