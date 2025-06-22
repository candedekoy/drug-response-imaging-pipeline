import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_nc_ratio(df, output_dir):
    """
    plots the Nuclear/Cytoplasmic signal ratio over time for different conditions.

    """
    
    # calculating N/C ratio
    df['nc_ratio'] = df['nuc_mean_intensity'] / df['cyto_mean_intensity']
    
    plt.figure(figsize=(10, 6))
    
    sns.lineplot(
        data=df,
        x='time_point',
        y='nc_ratio',
        hue='condition',
        estimator='mean',
    )
    
    plt.title('Nuclear/Cytoplasmic CTNNB1 Ratio', fontsize=18)
    plt.xlabel('Time (frames)', fontsize=12)
    plt.ylabel('N/C Ratio', fontsize=12)
    plt.legend(title='Condition')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # saving the figure
    output_path = os.path.join(output_dir, 'nuclear_cytoplasmic_ratio.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"N/C ratio plot saved to {output_path}")

def plot_membrane_signal(df, output_dir):
    """
    plots the normalized membrane signal over time for different conditions.

    """

    # normalize membrane intensity to the first time point for each cell
    df = df.sort_values(by=['condition', 'label', 'time_point'])
    df['normalized_membrane_intensity'] = df.groupby(['condition', 'label'])['mem_mean_intensity'].transform(lambda x: x / x.iloc[0])

    plt.figure(figsize=(10, 6))
    
    sns.lineplot(
        data=df,
        x='time_point',
        y='normalized_membrane_intensity',
        hue='condition',
        estimator='mean',
    )
    
    plt.title('Membrane CTNNB1 Signal', fontsize=18)
    plt.xlabel('Time (frames)', fontsize=12)
    plt.ylabel('Normalized Intensity', fontsize=12)
    plt.legend(title='Condition')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # saving the figure
    output_path = os.path.join(output_dir, 'membrane_signal.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Membrane signal plot saved to {output_path}") 