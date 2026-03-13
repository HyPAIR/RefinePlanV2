import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load  data (standard Pandas loading)
df = pd.read_excel('manipulator_informed_data_results.ods', engine='odf', sheet_name='compiled_data')
df['Data points'] = pd.to_numeric(df['Data points'], errors='coerce')
df['Goal percentage'] = pd.to_numeric(df['Goal percentage'], errors='coerce')
df_clean = df.dropna(subset=['Data points', 'Goal percentage']).sort_values('Data points')

# 1. Theme and Color Configuration
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 7))

box_fill_color = "#D1E8FF"  # Light blue background (semi-opaque)
theme_blue = "#1F77B4"      # Dark blue for all outlines and lines
theme_red ="#EB4040"

# This shows every data point in grey with low opacity
sns.stripplot(
    data=df_clean,
    x='Data points',
    y='Goal percentage',
    color='grey',
    alpha=0.3,         # Low opacity
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
    meanline=False,            # Draw the mean as a line across the box
    color=box_fill_color,
    width=0.5,
    linewidth=2,
    # Box styling: Set transparency (alpha) and border color
    boxprops=dict(alpha=0.6, edgecolor=theme_blue),
    # Line styling: Match all lines to the theme blue
    whiskerprops=dict(color=theme_blue),
    capprops=dict(color=theme_blue),
    medianprops=dict(linestyle='--', linewidth=1.5, color=theme_red),
    # Mark the mean with an 'x'
    meanprops={
        "marker":"x", 
        "markeredgecolor":theme_blue, 
        "markersize":"8"
    },
    # Outlier styling: Open circles in theme blue
    flierprops=dict(marker='o', markeredgecolor=theme_blue, markersize=6)
)

# 3. Labeling and Aesthetics
plt.suptitle('Goal Percentage Distribution by Data Points', fontsize=14, fontweight='regular')
plt.title('MID Exploration Results', fontsize=12, fontweight='regular', pad=10)
plt.xlabel('Data Points', fontsize=12)
plt.ylabel('Goal Percentage (%)', fontsize=12)

# Remove unnecessary outer frames
sns.despine(left=True, bottom=True)

# 4. Save the Final Output
plt.savefig('manipulator_informed_data_boxplot.png', dpi=300, bbox_inches='tight')
plt.show()