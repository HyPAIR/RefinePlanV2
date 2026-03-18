import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data from CSV
# Assigning the names as the file does not have a header line
column_names = [
    'Data points', 'Run Number', 'Initial Permutation', 'Goal percentage', 
    'Success', 'Number of actions', 'Total Task time', 'Goal region config'
]
df = pd.read_csv('pick-place-random_compiled_results_perm_4.csv', header=None, names=column_names)

# Numeric conversions to handle raw string data
df['Data points'] = pd.to_numeric(df['Data points'], errors='coerce')
df['Goal percentage'] = pd.to_numeric(df['Goal percentage'], errors='coerce')
df['Total Task time'] = pd.to_numeric(df['Total Task time'], errors='coerce')

# Filter 1: General cleaning for the Goal Percentage plot
df_clean = df.dropna(subset=['Data points', 'Goal percentage']).sort_values('Data points')

# Filter 2: Only 100% Goal percentage for the Task Time plot
df_100 = df_clean[df_clean['Goal percentage'] == 100].copy()

# 2. Theme and Color Configuration
sns.set_theme(style="whitegrid")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

color_key = 'random' # Auto-set for random results
if color_key == 'random':
    box_fill_color, theme_median, theme_mean = "#ff0f53", "#F70B69", "#6a0009"
else:
    box_fill_color, theme_median, theme_mean = "#D1E8FF", "#1F77B4", "#03004D"

# --- PLOT 1: Goal Percentage Distribution ---
sns.stripplot(data=df_clean, x='Data points', y='Goal percentage', color='grey', 
              alpha=0.5, jitter=True, size=5, zorder=1, ax=ax1)

sns.boxplot(
    data=df_clean, x='Data points', y='Goal percentage',
    showmeans=True, meanline=True, color=box_fill_color, width=0.5, linewidth=2,
    boxprops=dict(alpha=0.6, edgecolor=theme_median),
    whiskerprops=dict(color=theme_median),
    capprops=dict(color=theme_median),
    medianprops=dict(linestyle='-', linewidth=1.5, color=theme_median),
    meanprops=dict(linestyle='-', linewidth=1.5, color=theme_mean),
    showfliers=True, flierprops=dict(marker='o', markeredgecolor=theme_median, markersize=6),
    ax=ax1
)
ax1.set_title('Goal Percentage Distribution', fontsize=14, fontweight='bold')
ax1.set_ylabel('Goal Percentage (%)')

# --- PLOT 2: Total Task Time (Successful Runs Only) ---
sns.stripplot(data=df_100, x='Data points', y='Total Task time', color='grey', 
              alpha=0.5, jitter=True, size=5, zorder=1, ax=ax2)

sns.boxplot(
    data=df_100, x='Data points', y='Total Task time',
    showmeans=True, meanline=True, color=box_fill_color, width=0.5, linewidth=2,
    boxprops=dict(alpha=0.6, edgecolor=theme_median),
    whiskerprops=dict(color=theme_median),
    capprops=dict(color=theme_median),
    medianprops=dict(linestyle='-', linewidth=1.5, color=theme_median),
    meanprops=dict(linestyle='-', linewidth=1.5, color=theme_mean),
    showfliers=True, flierprops=dict(marker='o', markeredgecolor=theme_median, markersize=6),
    ax=ax2
)
ax2.set_title('Total Task Time (100% Success Only)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Total Task Time (s)')

# 3. Labeling and Aesthetics
plt.suptitle('Performance Metrics: Informed Results', fontsize=16, fontweight='bold', y=1.02)
sns.despine(left=True, bottom=True)
plt.tight_layout()

# 4. Save Output
plt.savefig('performance_metrics_from_csv_random.png', dpi=300, bbox_inches='tight')
plt.show()