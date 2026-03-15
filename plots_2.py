import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# Load  data (standard Pandas loading)
df = pd.read_excel('pick_place_informed_results_perm_1.ods', engine='odf', sheet_name='compiled_data')
df['Data points'] = pd.to_numeric(df['Data points'], errors='coerce')
df['Goal percentage'] = pd.to_numeric(df['Goal percentage'], errors='coerce')
df_clean = df.dropna(subset=['Data points', 'Goal percentage']).sort_values('Data points')

# 1. Setup Theme
sns.set_theme(style="whitegrid")

# --- VERSION A: GROUPED BOXPLOT (Multiple colors, one graph) ---
plt.figure(figsize=(12, 8))

# Background Scatter: Dodged to align with grouped boxes
sns.stripplot(
    data=df_clean,
    x='Data points',
    y='Goal percentage',
    hue='Initial Permutation',
    dodge=True,            # Crucial: aligns points with specific boxes
    palette='dark:grey',
    alpha=0.3,
    jitter=True,
    size=3,
    zorder=1,
    legend=False
)

# Grouped Boxplot
sns.boxplot(
    data=df_clean,
    x='Data points',
    y='Goal percentage',
    hue='Initial Permutation',
    showmeans=True,
    meanline=True,
    palette="pastel",       # Distinct colors for each permutation
    width=0.8,
    linewidth=1.5,
    boxprops=dict(alpha=0.7, zorder=2),
    medianprops=dict(color="black", linewidth=2, zorder=3), # Black median
    meanprops=dict(linestyle='-', linewidth=2, color="red", zorder=3), # Red mean
    showfliers=False
)

plt.title('Performance by Data Points & Permutation (Grouped)', fontsize=16, fontweight='bold')
plt.legend(title='Permutation', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.savefig('grouped_permutation_boxplot.png', dpi=300, bbox_inches='tight')


# --- VERSION B: FACETED BOXPLOTS (Separate graphs for each permutation) ---
# This maintains your original blue signature style
g = sns.FacetGrid(df_clean, col="Initial Permutation", col_wrap=3, height=4, aspect=1.2)

# Add the grey scatter to each subplot
g.map_dataframe(
    sns.stripplot, 
    x='Data points', y='Goal percentage', 
    color='grey', alpha=0.3, jitter=True, size=3, zorder=1
)

# Add the signature blue boxes to each subplot
g.map_dataframe(
    sns.boxplot, 
    x='Data points', y='Goal percentage', 
    showmeans=True, meanline=True,
    color="#D1E8FF", 
    width=0.5, linewidth=1.5,
    boxprops=dict(alpha=0.6, edgecolor="#1F77B4"),
    medianprops=dict(color="#1F77B4", linewidth=2),
    meanprops=dict(linestyle='-', linewidth=2, color="#1F77B4"),
    showfliers=False
)

g.set_titles("{col_name}", fontweight='bold')
g.set_axis_labels("Data Points", "Goal Percentage (%)")
plt.tight_layout()
plt.savefig('faceted_permutation_boxplots_informed.png', dpi=300, bbox_inches='tight')