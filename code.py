import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
 
# -------------------------------
# File path
# -------------------------------
file_path = "D:\\Nemo_MHomo_FR1-1.CSV" 
 
# -------------------------------
# Load CSV
# -------------------------------
df = pd.read_csv(file_path)
 
# -------------------------------
# Parse timestamps
# -------------------------------
df['Datetime'] = pd.to_datetime(df['MM:DD:YYYY hh:mm:ss'], errors='coerce')
df = df.dropna(subset=['Datetime'])  # remove bad timestamps
 
# -------------------------------
# Ensure Left_Poke_Count is numeric
# -------------------------------
df['Left_Poke_Count'] = pd.to_numeric(df['Left_Poke_Count'], errors='coerce').fillna(0)
 
# -------------------------------
# Sort by datetime
# -------------------------------
df = df.sort_values('Datetime')
 
# -------------------------------
# Plot Left Poke Counts
# -------------------------------
plt.figure(figsize=(12, 6))
plt.plot(df['Datetime'], df['Left_Poke_Count'], marker='o', linestyle='-', color='green', linewidth=2)
 
plt.xlabel("Date and Time")
plt.ylabel("Left Poke Count")
plt.title("Left Poke Sequence Over Time")
 
# -------------------------------
# Format x-axis nicely
# -------------------------------
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))  # shows 09/08 20:24
ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # automatic ticks
plt.xticks(rotation=45)
 
plt.grid(True)
plt.tight_layout()
plt.show()

