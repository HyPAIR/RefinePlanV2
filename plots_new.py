import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load and Prepare Data
# Note: Ensure the column name matches your file (e.g., 'Total Task time')
df = pd.read_excel('pick_place_random_results_problem_1.ods', engine='odf', sheet_name='compiled_data')
df['Data points'] = pd.to_numeric(df['Data points'], errors='coerce')
df['Goal percentage'] = pd.to_numeric(df['Goal percentage'], errors='coerce')
df['Total Task time'] = pd.to_numeric(df['Total Task time'], errors='coerce')

# Clean base data
df_clean = df.dropna(subset=['Data points', 'Goal percentage']).sort_values('Data points')

# --- THE FILTER (Equivalent to Excel Filter) ---
# We create a new dataframe that ONLY contains 100% successes for the second plot
df_100 = df_clean[df_clean['Goal percentage'] == 100].copy()

# 2. Theme and Color Configuration
sns.set_theme(style="whitegrid")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7)) # Create side-by-side plots

color_key = 'random'
if color_key == 'random':
    box_fill_color, theme_median, theme_mean = "#ff0f53", "#F70B69", "#6a0009"
else:
    box_fill_color, theme_median, theme_mean = "#D1E8FF", "#1F77B4", "#03004D"

# --- PLOT 1: Original Goal Percentage ---
sns.stripplot(data=df_clean, x='Data points', y='Goal percentage', color='grey', alpha=0.3, jitter=True, size=4, ax=ax1, zorder=1)
sns.boxplot(
    data=df_clean, x='Data points', y='Goal percentage', 
    showmeans=True, meanline=False, # Mean as marker, Median as line
    color=box_fill_color, width=0.5, linewidth=2,
    boxprops=dict(alpha=0.6, edgecolor=theme_median),
    medianprops=dict(linestyle='-', linewidth=2.5, color=theme_median),
    meanprops=dict(marker='x', markeredgecolor=theme_mean, markersize=8, markeredgewidth=2),
    showfliers=False, ax=ax1, zorder=2
)
ax1.set_title('Goal Percentage Distribution', fontsize=14, fontweight='bold')
ax1.set_ylabel('Goal Percentage (%)')

# --- PLOT 2: Total Task Time (Filtered for 100% Success) ---
sns.stripplot(data=df_100, x='Data points', y='Total Task time', color='grey', alpha=0.3, jitter=True, size=4, ax=ax2, zorder=1)
sns.boxplot(
    data=df_100, x='Data points', y='Total Task time', 
    showmeans=True, meanline=False, 
    color=box_fill_color, width=0.5, linewidth=2,
    boxprops=dict(alpha=0.6, edgecolor=theme_median),
    medianprops=dict(linestyle='-', linewidth=2.5, color=theme_median),
    meanprops=dict(marker='x', markeredgecolor=theme_mean, markersize=8, markeredgewidth=2),
    showfliers=False, ax=ax2, zorder=2
)
ax2.set_title('Total Task Time (Successful Runs Only)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Total Task Time (s)')

# Final Styling
sns.despine(left=True, bottom=True)
plt.tight_layout()
plt.savefig('performance_comparison_plots_random.png', dpi=300)
plt.show()