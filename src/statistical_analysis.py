import pandas as pd
import statsmodels.formula.api as smf

# Load the data
df = pd.read_csv("results/master_results.csv")

# Preprocess: compute new features
df['nuc_cyto_ratio'] = df['nuc_mean_intensity'] / df['cyto_mean_intensity']
df['mem_mean_norm'] = (df['mem_mean_intensity'] - df['mem_mean_intensity'].mean()) / df['mem_mean_intensity'].std()
df['condition'] = df['condition'].astype('category')

# Fit OLS model for normalized membrane intensity
mem_model = smf.ols("mem_mean_norm ~ condition * time_point", data=df).fit()
mem_summary = mem_model.summary2().tables[1].reset_index()
mem_summary.columns = ['Term', 'Coefficient', 'Standard Error', 't', 'P>|t|', 'Lower 95% CI', 'Upper 95% CI']

# Fit OLS model for nuclear/cytoplasmic ratio
ratio_model = smf.ols("nuc_cyto_ratio ~ condition * time_point", data=df).fit()
ratio_summary = ratio_model.summary2().tables[1].reset_index()
ratio_summary.columns = ['Term', 'Coefficient', 'Standard Error', 't', 'P>|t|', 'Lower 95% CI', 'Upper 95% CI']

# Save results to CSV
mem_summary.to_csv("results/membrane_stats_model_results.csv", index=False, float_format='%.2f')
ratio_summary.to_csv("results/nuc_cyto_ratio_stats_model_results.csv", index=False, float_format='%.2f')

print("Analysis complete. Results saved to:")
print("results/membrane_stats_model_results.csv")
print("results/nuc_cyto_ratio_stats_model_results.csv")
