#!/usr/bin/env python3
"""
Left-poke -> pellet raster (zoom 0-2s)
- Trial increments only after a pellet retrieval.
- 'X' plotted for every Left_Poke_Count increment (also falls back to Event text).
- '^' plotted for pellet retrievals (Event or Pellet_Count increment).
- Zoomed x-axis between 0 and 2 seconds.
- Saves figure using the variable name `fig`.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ---- USER SETTINGS ----
csv_file = "Nemo_MHomo_FR1-2.CSV"   # <-- update path if needed
time_col = "MM:DD:YYYY hh:mm:ss"
event_col = "Event"
left_poke_col = "Left_Poke_Count"
pellet_count_col = "Pellet_Count"
poke_time_col = "Poke_Time"
retrieval_time_col = "Retrieval_Time"
x_min, x_max = 0.0, 2.0              # zoom window (seconds)
outfile_png = "left_poke_pellet_raster_2.png"
outfile_pdf = "left_poke_pellet_raster_2.pdf"
# -----------------------


def to_float_safe(x):
    try:
        return float(x)
    except Exception:
        return np.nan


# Load CSV
df = pd.read_csv(csv_file, parse_dates=[
                 time_col], dayfirst=False, keep_default_na=True).reset_index(drop=True)

# Clean numeric time columns
df[poke_time_col] = df[poke_time_col].apply(to_float_safe)
df[retrieval_time_col] = df[retrieval_time_col].apply(
    lambda v: np.nan if (isinstance(
        v, str) and "Timed_out" in v) else to_float_safe(v)
)

# Coerce counts if present
if left_poke_col in df.columns:
    df[left_poke_col] = pd.to_numeric(df[left_poke_col], errors='coerce')
if pellet_count_col in df.columns:
    df[pellet_count_col] = pd.to_numeric(df[pellet_count_col], errors='coerce')

# Build events: trial increments only after pellet
trial = 1
poke_events = []    # list of (trial, time)
pellet_events = []  # list of (trial, time)
prev_left_count = None
prev_pellet_count = None

for _, row in df.iterrows():
    ev = row.get(event_col, "")
    poke_t = row.get(poke_time_col, np.nan)
    retr_t = row.get(retrieval_time_col, np.nan)

    # Detect left pokes:
    #  - prefer numeric Left_Poke_Count increments (one marker per increment)
    #  - fallback to Event text containing "Left" (excluding LeftWithPellet)
    if left_poke_col in df.columns:
        cur_left = row[left_poke_col]
        if prev_left_count is None:
            prev_left_count = cur_left
        else:
            if (not np.isnan(cur_left)) and (not np.isnan(prev_left_count)) and (cur_left > prev_left_count):
                increments = int(cur_left - prev_left_count)
                if not np.isnan(poke_t):
                    # Add one marker per increment with tiny negative jitter so they don't overlap exactly
                    for k in range(increments):
                        jitter = -0.01 * (increments - 1 - k)
                        poke_events.append((trial, float(poke_t) + jitter))
        prev_left_count = cur_left

    # If numeric counts missing or did not indicate a change, use Event string
    if (left_poke_col not in df.columns or np.isnan(row.get(left_poke_col, np.nan))):
        if isinstance(ev, str) and ("Left" in ev) and ("LeftWithPellet" not in ev):
            if not np.isnan(poke_t):
                poke_events.append((trial, float(poke_t)))

    # Detect pellets: Event == 'Pellet' or contains 'WithPellet' OR Pellet_Count increments
    pellet_flag = False
    if isinstance(ev, str) and (ev == "Pellet" or "WithPellet" in ev):
        pellet_flag = True

    if pellet_count_col in df.columns:
        cur_pel = row[pellet_count_col]
        if prev_pellet_count is None:
            prev_pellet_count = cur_pel
        else:
            if (not np.isnan(cur_pel)) and (not np.isnan(prev_pellet_count)) and (cur_pel > prev_pellet_count):
                pellet_flag = True
        prev_pellet_count = cur_pel

    if pellet_flag:
        if not np.isnan(retr_t):
            pellet_events.append((trial, float(retr_t)))
        elif not np.isnan(poke_t):
            pellet_events.append((trial, float(poke_t)))
        # increment trial after pellet
        trial += 1

# Aggregate pokes per trial for linking latencies
pokes_by_trial = defaultdict(list)
for tr, t in poke_events:
    pokes_by_trial[tr].append(t)

# Prepare plotting lists limited to zoom window
poke_x = [t for tr, t in poke_events if x_min <= t <= x_max]
poke_y = [tr for tr, t in poke_events if x_min <= t <= x_max]
pellet_x = [t for tr, t in pellet_events if x_min <= t <= x_max]
pellet_y = [tr for tr, t in pellet_events if x_min <= t <= x_max]

# ---- Plotting ----
# create fig variable so we can save via fig.savefig()
fig, ax = plt.subplots(figsize=(10, 8))

# Scatter pokes and pellets inside zoom window
ax.scatter(poke_x, poke_y, marker='x', color='tab:blue',
           s=50, label='Left poke (X)')
ax.scatter(pellet_x, pellet_y, marker='^',
           color='tab:green', s=80, label='Pellet (^)')

# For each pellet inside the zoom window, draw a line from last left poke before pellet to pellet and annotate latency
for tr, pellet_t in pellet_events:
    if not (x_min <= pellet_t <= x_max):
        continue
    tr_pokes = sorted(pokes_by_trial.get(tr, []))
    if len(tr_pokes) == 0:
        continue
    # choose last poke <= pellet_t if possible
    last_poke = None
    for pt in tr_pokes:
        if pt <= pellet_t:
            last_poke = pt
    if last_poke is None:
        last_poke = tr_pokes[-1]
    if not (x_min <= last_poke <= x_max):
        continue
    ax.plot([last_poke, pellet_t], [tr, tr],
            color='gray', linewidth=0.9, alpha=0.9)
    latency = pellet_t - last_poke
    ax.text(pellet_t + 0.02*(x_max - x_min), tr,
            f"{latency:.2f}s", fontsize=7, color='gray', va='center')

# Axis formatting
ax.set_xlim(x_min, x_max)
all_y = poke_y + pellet_y
if all_y:
    ax.set_ylim(min(all_y) - 0.5, max(all_y) + 0.5)
else:
    ax.set_ylim(0.5, 5.5)

ax.set_xlabel("Time (sec)")
ax.set_ylabel("Trial #")
ax.set_title(
    f"Left pokes (X) and pellet retrievals (^) — zoom {x_min:.1f}-{x_max:.1f}s")
ax.legend(loc='upper right')
plt.tight_layout()

# Save figure using the fig variable
fig.savefig(outfile_png, dpi=300)
fig.savefig(outfile_pdf)
print(f"Saved {outfile_png} and {outfile_pdf}")
