import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='plot success rate for a database')
parser.add_argument('-d','--training-data-collection-name', type=str, required=True, help='Name of the training data collection')
args = parser.parse_args()

DATABASE = args.training_data_collection_name 
OUTPUT_NAME = f'{DATABASE}_balanced_analysis'
DATA_DIR = 'results'
POINTS_RANGE = range(1000, 16001, 1000)

# 1. THEME SELECTION
is_informed = 'informed' in DATABASE.lower()
main_color = "#1F77B4" if is_informed else "#ff0f0f"
palette_style = "Blues_d" if is_informed else "Reds_d"

# 2. DATA COMPILATION
all_data = []
for limit in POINTS_RANGE:
    file_path = os.path.join(DATA_DIR, f'{DATABASE}_{limit}_points.csv')
    if os.path.isfile(file_path):
        all_data.append(pd.read_csv(file_path))

if not all_data:
    print(f"Error: No files found in {DATA_DIR}.")
    exit()

df_raw = pd.concat(all_data, ignore_index=True)

# 3. DATA CLEANING & BALANCING
df_raw['is_success'] = (df_raw['goal_percentage'] >= 99.9).astype(int)
if df_raw['initial_permutation'].dtype == object:
    df_raw['initial_permutation'] = df_raw['initial_permutation'].str.replace('permutation_', '')

def balance_groups(group):
    # Find the smallest number of runs among all permutations in this specific data limit
    counts = group.groupby('initial_permutation').size()
    if counts.empty: return group
    min_samples = counts.min()
    return group.groupby('initial_permutation').sample(n=min_samples, random_state=42)

# Apply balancing (using a lambda to avoid the DeprecationWarning)
df = df_raw.groupby('data limit', group_keys=False).apply(lambda x: balance_groups(x))

# --- PRINT SAMPLE REPORT ---
print("\n" + "="*40)
print(f"BALANCING REPORT: {DATABASE}")
print("="*40)
counts_table = df.groupby(['data limit', 'initial_permutation']).size().unstack(fill_value=0)
print("Samples per Permutation (Balanced):")
print(counts_table)
print("="*40 + "\n")

# 4. PREPARE METRICS
df_100 = df[df['is_success'] == 1].copy()

# Calculate unique permutations solved per data limit
perms_solved = df.groupby('data limit').apply(
    lambda x: x[x['is_success'] == 1]['initial_permutation'].nunique()
).reset_index(name='unique_perms_solved')

# 5. PLOTTING (2x2 Grid)
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(20, 14))
((ax1, ax2), (ax3, ax4)) = axes

# Plot 1: Overall Success Rate
sns.barplot(data=df, x='data limit', y='is_success', 
            estimator=lambda x: sum(x)/len(x)*100, 
            color=main_color, ax=ax1, edgecolor="black", alpha=0.8, errorbar=None)
ax1.set_title('Overall Success Rate (%)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Success %')

# Plot 2: Success per Permutation
sns.barplot(data=df, x='data limit', y='is_success', hue='initial_permutation',
            estimator=lambda x: sum(x)/len(x)*100, 
            palette=palette_style, ax=ax2, edgecolor="black", errorbar=None)
ax2.set_title('Success Rate by Permutation', fontsize=14, fontweight='bold')
ax2.legend(title='Perm', bbox_to_anchor=(1.05, 1), loc='upper left')

# Plot 3: Avg Task Time
sns.barplot(data=df_100, x='data limit', y='total_task_time', 
            color=main_color, ax=ax3, edgecolor="black", alpha=0.8, capsize=.1)
ax3.set_title('Avg Task Time (Successful Runs)', fontsize=14, fontweight='bold')
ax3.set_ylabel('Time (s)')

# Plot 4: Number of Unique Permutations Solved
sns.barplot(data=perms_solved, x='data limit', y='unique_perms_solved', 
            color=main_color, ax=ax4, edgecolor="black", alpha=0.8)
ax4.set_title('Count of Unique Permutations Solved', fontsize=14, fontweight='bold')
ax4.set_ylabel('Count of Permutations')

# Standardize Labels
for ax in axes.flat:
    ax.set_xlabel('Data Points')

# Annotate Plot 1
for p in ax1.patches:
    ax1.annotate(f'{p.get_height():.1f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=10, fontweight='bold')

plt.suptitle(f'Balanced Performance Metrics: {DATABASE.replace("-", " ").title()}', 
             fontsize=20, fontweight='bold', y=0.98)
sns.despine()
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# 6. SAVE
df.to_csv(f'{OUTPUT_NAME}.csv', index=False)
plt.savefig(f'{OUTPUT_NAME}.png', dpi=300, bbox_inches='tight')
print(f"Graphs saved: {OUTPUT_NAME}.png")
plt.show()