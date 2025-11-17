import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

# Read the data
df = pd.read_csv('/mnt/user-data/uploads/Nemo_MHomo_PR-1.CSV')

print("=== DATA OVERVIEW ===")
print(f"Total rows: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")

# Parse datetime
df['DateTime'] = pd.to_datetime(df['MM:DD:YYYY hh:mm:ss'], format='%m/%d/%Y %H:%M:%S', errors='coerce')
df = df.dropna(subset=['DateTime']).sort_values('DateTime').reset_index(drop=True)

# Time from session start
df['Time_Min'] = (df['DateTime'] - df['DateTime'].iloc[0]).dt.total_seconds() / 60

# Filter to pellet delivery events
pellets = df[df['Event'].str.contains('Pellet', na=False)].copy()
pellets = pellets.reset_index(drop=True)
pellets['Reward_Number'] = range(1, len(pellets) + 1)

print(f"\nTotal pellets delivered: {len(pellets)}")
print(f"FR (ratio) range: {pellets['FR'].min()} to {pellets['FR'].max()}")
print(f"Session duration: {df['Time_Min'].max():.1f} minutes")

# Calculate metrics by FR ratio
print("\n=== CALCULATING METRICS BY PROGRESSIVE RATIO ===")

# Get all pokes (not just pellets)
all_pokes = df[df['Event'].str.contains('Left|Right', na=False)].copy()

# For each reward, find the FR requirement and pokes made
metrics_by_ratio = []

for idx, pellet_row in pellets.iterrows():
    fr_value = pellet_row['FR']
    reward_num = pellet_row['Reward_Number']
    pellet_time = pellet_row['Time_Min']
    
    # Find previous pellet time (or session start)
    if reward_num == 1:
        prev_time = 0
    else:
        prev_time = pellets.iloc[reward_num-2]['Time_Min']
    
    # Get pokes in this interval
    interval_pokes = all_pokes[(all_pokes['Time_Min'] > prev_time) & 
                               (all_pokes['Time_Min'] <= pellet_time)]
    
    n_pokes = len(interval_pokes)
    time_for_ratio = pellet_time - prev_time
    
    # Calculate metrics
    metrics_by_ratio.append({
        'Reward_Number': reward_num,
        'FR_Ratio': fr_value,
        'Pokes_Made': n_pokes,
        'Time_Minutes': time_for_ratio,
        'Poke_Rate': n_pokes / time_for_ratio if time_for_ratio > 0 else 0,
        'Cumulative_Time': pellet_time
    })

metrics_df = pd.DataFrame(metrics_by_ratio)

print("\nMetrics by ratio (first 15 rewards):")
print(metrics_df.head(15))

# Aggregate by FR ratio
ratio_summary = metrics_df.groupby('FR_Ratio').agg({
    'Pokes_Made': ['mean', 'sem', 'count'],
    'Time_Minutes': ['mean', 'sem'],
    'Poke_Rate': ['mean', 'sem']
}).reset_index()

ratio_summary.columns = ['FR_Ratio', 'Pokes_Mean', 'Pokes_SEM', 'N_Completions',
                         'Time_Mean', 'Time_SEM', 'Rate_Mean', 'Rate_SEM']

print("\n=== SUMMARY BY FR RATIO ===")
print(ratio_summary)

# Create the figure
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

fig.suptitle(f'Progressive Ratio Analysis - Nemo_MHomo_PR-1\nBreakpoint: FR {pellets["FR"].max()} | Total Rewards: {len(pellets)}', 
             fontsize=14, fontweight='bold')

# Plot 1: Pokes per ratio over time
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(metrics_df['Reward_Number'], metrics_df['Pokes_Made'], 'o-', color='steelblue', linewidth=2, markersize=6)
ax1.set_xlabel('Reward Number')
ax1.set_ylabel('Pokes Made')
ax1.set_title('A. Pokes Required per Reward', fontweight='bold')
ax1.grid(True, alpha=0.3)

# Plot 2: Time per ratio over session
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(metrics_df['Reward_Number'], metrics_df['Time_Minutes'], 'o-', color='coral', linewidth=2, markersize=6)
ax2.set_xlabel('Reward Number')
ax2.set_ylabel('Time (minutes)')
ax2.set_title('B. Time per Reward', fontweight='bold')
ax2.grid(True, alpha=0.3)

# Plot 3: Response rate over session
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(metrics_df['Reward_Number'], metrics_df['Poke_Rate'], 'o-', color='mediumseagreen', linewidth=2, markersize=6)
ax3.set_xlabel('Reward Number')
ax3.set_ylabel('Pokes per Minute')
ax3.set_title('C. Response Rate', fontweight='bold')
ax3.grid(True, alpha=0.3)

# Plot 4: Average pokes by FR ratio
ax4 = fig.add_subplot(gs[1, 0])
ax4.bar(ratio_summary['FR_Ratio'], ratio_summary['Pokes_Mean'], 
        yerr=ratio_summary['Pokes_SEM'], capsize=5, color='steelblue', alpha=0.7)
ax4.set_xlabel('FR Ratio Requirement')
ax4.set_ylabel('Average Pokes')
ax4.set_title('D. Average Pokes by FR Ratio', fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

# Plot 5: Average time by FR ratio
ax5 = fig.add_subplot(gs[1, 1])
ax5.bar(ratio_summary['FR_Ratio'], ratio_summary['Time_Mean'], 
        yerr=ratio_summary['Time_SEM'], capsize=5, color='coral', alpha=0.7)
ax5.set_xlabel('FR Ratio Requirement')
ax5.set_ylabel('Average Time (min)')
ax5.set_title('E. Average Time by FR Ratio', fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# Plot 6: Average rate by FR ratio
ax6 = fig.add_subplot(gs[1, 2])
ax6.bar(ratio_summary['FR_Ratio'], ratio_summary['Rate_Mean'], 
        yerr=ratio_summary['Rate_SEM'], capsize=5, color='mediumseagreen', alpha=0.7)
ax6.set_xlabel('FR Ratio Requirement')
ax6.set_ylabel('Pokes per Minute')
ax6.set_title('F. Average Response Rate by FR Ratio', fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')

# Plot 7: Cumulative rewards over time
ax7 = fig.add_subplot(gs[2, :2])
ax7.plot(metrics_df['Cumulative_Time'], metrics_df['Reward_Number'], 
         linewidth=3, color='darkblue', marker='o', markersize=4)
ax7.set_xlabel('Time (minutes)')
ax7.set_ylabel('Cumulative Rewards')
ax7.set_title('G. Cumulative Reward Function', fontweight='bold')
ax7.grid(True, alpha=0.3)

# Plot 8: FR progression
ax8 = fig.add_subplot(gs[2, 2])
ax8.plot(metrics_df['Reward_Number'], metrics_df['FR_Ratio'], 
         linewidth=3, color='darkred', marker='s', markersize=5)
ax8.set_xlabel('Reward Number')
ax8.set_ylabel('FR Ratio Requirement')
ax8.set_title('H. Progressive Ratio Schedule', fontweight='bold')
ax8.grid(True, alpha=0.3)

plt.savefig('/mnt/user-data/outputs/progressive_ratio_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Plot saved as 'progressive_ratio_analysis.png'")

# Print key findings
print("\n=== KEY FINDINGS ===")
print(f"Breakpoint (highest FR completed): FR {pellets['FR'].max()}")
print(f"Total rewards earned: {len(pellets)}")
print(f"Session duration: {df['Time_Min'].max():.1f} minutes")
print(f"Average reward rate: {len(pellets) / df['Time_Min'].max():.2f} rewards/min")
print(f"\nFR ratios completed:")
for _, row in ratio_summary.iterrows():
    print(f"  FR {int(row['FR_Ratio'])}: {int(row['N_Completions'])} times, "
          f"avg {row['Pokes_Mean']:.1f} pokes, "
          f"avg {row['Time_Mean']:.2f} min")
