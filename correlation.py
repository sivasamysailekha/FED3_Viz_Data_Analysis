import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch

# Simulated data
np.random.seed(42)
time = np.linspace(0, 100, 200)
early_data = np.cumsum(np.random.randn(200)) + 50
late_data = np.cumsum(np.random.randn(200)) + 70

# Lever press times (randomly selected)
early_presses = np.random.choice(time, size=20, replace=False)
late_presses = np.random.choice(time, size=30, replace=False)

# Points of interest (random red dots)
early_interest = np.random.choice(range(200), size=5, replace=False)
late_interest = np.random.choice(range(200), size=5, replace=False)

# Create figure
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
titles = ['Wild Mice', 'Autism Mice']
datasets = [(early_data, early_presses, early_interest),
            (late_data, late_presses, late_interest)]

for i, ax in enumerate(axs):
    data, presses, interest = datasets[i]

    # Main plot
    ax.plot(time, data, color='black', linewidth=1)
    ax.scatter(time, data, color='blue', s=10)
    ax.scatter(time[interest], data[interest], color='red', s=30, zorder=5)
    ax.vlines(presses, ymin=min(data)-5,
              ymax=min(data)-2, color='red', linewidth=2)

    ax.set_title(titles[i])
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Number of pokes')

    # Inset zoom
    inset_start = 40
    inset_end = 60
    inset_ax = ax.inset_axes([0.6, 0.5, 0.35, 0.4])
    mask = (time >= inset_start) & (time <= inset_end)
    inset_ax.plot(time[mask], data[mask], color='black', linewidth=1)
    inset_ax.scatter(time[mask], data[mask], color='blue', s=10)
    inset_ax.vlines([t for t in presses if inset_start <= t <= inset_end],
                    ymin=min(data)-5, ymax=min(data)-2, color='red', linewidth=2)
    inset_ax.set_title('Zoom')

    # Connect inset to main plot
    con = ConnectionPatch(xyA=(inset_start, data[mask][0]), coordsA=ax.transData,
                          xyB=(inset_start, data[mask][0]
                               ), coordsB=inset_ax.transData,
                          color='gray', linewidth=1)
    ax.add_artist(con)

plt.savefig("corr_raster.png", dpi=300)
plt.savefig("corr_raster.pdf")
print("Plot saved as corr_raster.png and corr_raster.pdf")
