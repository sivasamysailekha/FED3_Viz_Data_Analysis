import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

def load_and_prepare_data(filepath):
    """
    Load data from CSV file.
    
    Expected columns:
    - group: 'ChR2' or 'YFP'
    - condition: 'off', 'Pf', or 'PPN'
    - lever_presses_stim: number of lever presses during stimulation
    - lever_presses_poststim: number of lever presses post-stimulation
    - lever_presses_reward: number of lever presses per reward
    - sequence_duration: sequence duration in seconds
    - reinforcers: number of reinforcers per minute
    - inter_press_interval: inter-press interval in seconds
    """
    df = pd.read_csv(filepath)
    return df

def calculate_statistics(group1_data, group2_data):
    """
    Perform t-test between two groups
    Returns p-value and significance markers
    """
    stat, p_value = stats.ttest_ind(group1_data, group2_data, nan_policy='omit')
    
    if p_value < 0.001:
        sig = '***'
    elif p_value < 0.01:
        sig = '**'
    elif p_value < 0.05:
        sig = '*'
    else:
        sig = 'ns'
    
    return p_value, sig

def plot_behavioral_metrics(df, save_path='behavioral_analysis.png'):
    """
    Create a 2x3 grid of bar plots showing behavioral metrics
    """
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("Set2")
    
    # Create figure with 2x3 subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Behavioral Analysis: ChR2 vs YFP', fontsize=16, fontweight='bold')
    
    # Define metrics and their labels
    metrics = [
        ('lever_presses_stim', '# Lever presses during stim', 'N'),
        ('lever_presses_poststim', '# Lever presses poststim', 'O'),
        ('lever_presses_reward', '# Lever presses per reward', 'P'),
        ('sequence_duration', 'Sequence duration (sec)', 'Q'),
        ('reinforcers', 'Reinforcers / min.', 'R'),
        ('inter_press_interval', 'Inter press interval', 'S')
    ]
    
    # Colors for conditions
    colors = {'off': '#808080', 'Pf': '#6BA3D0', 'PPN': '#5E8EBD'}
    
    # Conditions order
    conditions = ['off', 'Pf', 'PPN']
    
    # Plot each metric
    for idx, (metric, ylabel, panel_label) in enumerate(metrics):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]
        
        # Prepare data for plotting
        x_positions = []
        bar_positions = []
        current_x = 0
        
        for group_idx, group in enumerate(['ChR2', 'YFP']):
            for cond_idx, condition in enumerate(conditions):
                # Filter data
                data = df[(df['group'] == group) & (df['condition'] == condition)][metric].dropna()
                
                # Calculate position
                pos = current_x + cond_idx * 0.8
                bar_positions.append(pos)
                
                # Calculate mean and SEM
                mean_val = data.mean()
                sem_val = data.sem()
                
                # Plot bar
                bar = ax.bar(pos, mean_val, 0.7, 
                           color=colors[condition], 
                           edgecolor='black', 
                           linewidth=1.5,
                           alpha=0.8)
                
                # Plot error bars
                ax.errorbar(pos, mean_val, yerr=sem_val, 
                          fmt='none', 
                          ecolor='black', 
                          capsize=5,
                          linewidth=1.5)
                
                # Plot individual data points
                n_points = len(data)
                jitter = np.random.normal(0, 0.08, n_points)
                ax.scatter([pos + j for j in jitter], data, 
                         color='black', 
                         s=30, 
                         alpha=0.7,
                         zorder=3)
            
            current_x += 3.0
        
        # Set x-axis labels
        group_centers = [1.6, 4.6]
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(['off', 'Pf', 'PPN', 'off', 'Pf', 'PPN'])
        
        # Add group labels at bottom
        for i, (center, group) in enumerate(zip(group_centers, ['ChR2', 'YFP'])):
            color = '#4A90E2' if group == 'ChR2' else '#7CB342'
            ax.text(center, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.15, 
                   group, 
                   ha='center', 
                   va='top',
                   fontsize=11,
                   fontweight='bold',
                   color=color)
        
        # Add significance markers (example for ChR2 off vs Pf)
        chr2_off = df[(df['group'] == 'ChR2') & (df['condition'] == 'off')][metric].dropna()
        chr2_pf = df[(df['group'] == 'ChR2') & (df['condition'] == 'Pf')][metric].dropna()
        
        if len(chr2_off) > 0 and len(chr2_pf) > 0:
            p_val, sig = calculate_statistics(chr2_off, chr2_pf)
            if sig != 'ns':
                y_max = ax.get_ylim()[1]
                ax.text(0.4, y_max * 0.95, sig, 
                       ha='center', 
                       fontsize=12, 
                       fontweight='bold')
        
        # Styling
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        
        # Add panel label
        ax.text(-0.15, 1.05, panel_label, 
               transform=ax.transAxes, 
               fontsize=16, 
               fontweight='bold',
               va='top')
        
        # Set y-axis to start at 0
        ax.set_ylim(bottom=0)
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {save_path}")
    return fig

# Example usage
if __name__ == "__main__":
    # Example: Create sample data
    # Replace this with: df = load_and_prepare_data('your_data.csv')
    
    np.random.seed(42)
    n_samples = 8
    
    data_list = []
    for group in ['ChR2', 'YFP']:
        for condition in ['off', 'Pf', 'PPN']:
            for _ in range(n_samples):
                if group == 'ChR2' and condition == 'Pf':
                    # ChR2 Pf shows significant changes
                    data_list.append({
                        'group': group,
                        'condition': condition,
                        'lever_presses_stim': np.random.normal(0.2, 0.1),
                        'lever_presses_poststim': np.random.normal(8, 1),
                        'lever_presses_reward': np.random.normal(9.5, 0.5),
                        'sequence_duration': np.random.normal(37, 5),
                        'reinforcers': np.random.normal(1.8, 0.2),
                        'inter_press_interval': np.random.normal(5, 0.5)
                    })
                elif group == 'ChR2' and condition == 'off':
                    data_list.append({
                        'group': group,
                        'condition': condition,
                        'lever_presses_stim': np.random.normal(2.5, 0.3),
                        'lever_presses_poststim': np.random.normal(5.5, 0.5),
                        'lever_presses_reward': np.random.normal(9.8, 0.3),
                        'sequence_duration': np.random.normal(15, 2),
                        'reinforcers': np.random.normal(1.7, 0.2),
                        'inter_press_interval': np.random.normal(2, 0.3)
                    })
                else:
                    # Other conditions
                    data_list.append({
                        'group': group,
                        'condition': condition,
                        'lever_presses_stim': np.random.normal(3, 0.5),
                        'lever_presses_poststim': np.random.normal(5.5, 0.5),
                        'lever_presses_reward': np.random.normal(9.5, 0.5),
                        'sequence_duration': np.random.normal(18, 3),
                        'reinforcers': np.random.normal(2, 0.3),
                        'inter_press_interval': np.random.normal(2.2, 0.4)
                    })
    
    df_sample = pd.DataFrame(data_list)
    
    # Create plots
    plot_behavioral_metrics(df_sample, 'behavioral_analysis_output.png')
    
    print("\nTo use with your own data:")
    print("df = load_and_prepare_data('your_data.csv')")
    print("plot_behavioral_metrics(df, 'output_filename.png')")
