import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load  data (standard Pandas loading)
df = pd.read_excel('pick_place_random_results.ods', engine='odf', sheet_name='compiled_data')
df['Data points'] = pd.to_numeric(df['Data points'], errors='coerce')
df['Goal percentage'] = pd.to_numeric(df['Goal percentage'], errors='coerce')
df_clean = df.dropna(subset=['Data points', 'Goal percentage']).sort_values('Data points')

# 1. Theme and Color Configuration
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 7))
color_key = 'random'
if color_key == 'random':
    box_fill_color ="#ff0f53"   # semi-opaque)
    theme_median ="#F70B69"#       
    theme_mean ="#6a0009"
else:
    box_fill_color ="#D1E8FF"
    theme_median ="#1F77B4"
    theme_mean ="#03004D"
# This shows every data point in grey with low opacity
sns.stripplot(
    data=df_clean,
    x='Data points',
    y='Goal percentage',
    color='grey',
    alpha=0.5,         # Low opacity
    jitter=True,       # Spread points out to show density
    size=5,            # Point size
    zorder=1           # Ensures points are behind the box lines
)

#2. Create the Vertical Box Plot
ax = sns.boxplot(
    data=df_clean,
    x='Data points',          # Categories on x-axis
    y='Goal percentage',      # Values on y-axis
    showmeans=True,           # Enable mean display
    meanline=True,            # Draw the mean as a line across the box
    color=box_fill_color,
    width=0.5,
    linewidth=2,
    # Box styling: Set transparency (alpha) and border color
    boxprops=dict(alpha=0.6, edgecolor=theme_median),
    # Line styling: Match all lines to the theme blue
    whiskerprops=dict(color=theme_median),
    capprops=dict(color=theme_median),
    medianprops=dict(linestyle='-', linewidth=1.5, color=theme_median),
    meanprops=dict(linestyle='-', linewidth=1.5, color=theme_mean),
    # Mark the mean with an 'x'
    # meanprops={
    #     "marker":"x", 
    #     "markeredgecolor":theme_blue, 
    #     "markersize":"8"
    # },
    # Outlier styling: Open circles in theme blue
    showfliers=True,
    flierprops=dict(marker='o', markeredgecolor=theme_median, markersize=6)
)

# 3. Labeling and Aesthetics
plt.suptitle('Goal Percentage Distribution by Data Points', fontsize=14, fontweight='regular')
plt.title('random Exploration Results', fontsize=12, fontweight='regular', pad=10)
plt.xlabel('Data Points', fontsize=12)
plt.ylabel('Goal Percentage (%)', fontsize=12)

# Remove unnecessary outer frames
sns.despine(left=True, bottom=True)

# 4. Save the Final Output
plt.savefig('pick_place_random_data_boxplot.png', dpi=300, bbox_inches='tight')
plt.show()