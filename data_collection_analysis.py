from pymongo import MongoClient, ASCENDING
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def fetch_data_trends(uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Optimized fetch: only get the fields we need
    cursor = collection.find({}, {"duration": 1, "timestamp": 1}).sort("timestamp", ASCENDING)#.limit(1500)
    
    zero_cost_loops = 0
    total_entries = 0
    points = []
    
    for document in cursor:
        total_entries += 1
        if document.get('duration') == 0.001:
            zero_cost_loops += 1
        
        # Calculate percentages
        zero_pct = (zero_cost_loops / total_entries) * 100
        non_zero_pct = 100 - zero_pct
        
        points.append({
            "Data Points": total_entries, 
            "Zero Cost Loops": zero_cost_loops, 
            "Zero Cost %": zero_pct,
            "Non-Zero Cost %": non_zero_pct,
            "Database": collection_name
        })

    return points

if __name__ == "__main__":
    CONNECTION_URI = "mongodb://localhost:27017/"
    DATABASE_NAME = "refine-plan-v2"
    collections = ['random-exploration','informed-exploration','pick-place-random','pick-place-informed']#,'example-a-seeded','example-a-informed']#,'manipulator-informed-data']
    
    all_results = []
    for coll in collections:
        print(f"Processing {coll}...")
        all_results.extend(fetch_data_trends(CONNECTION_URI, DATABASE_NAME, coll))

    df = pd.DataFrame(all_results)
    sns.set_theme(style="whitegrid")

    # --- Plot 1: Cumulative Zero Cost Loops ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Data Points", y="Zero Cost Loops", hue="Database", linewidth=2)
    plt.suptitle('Trend 1: Cumulative Zero-Cost Loops', fontweight='bold')
    plt.title('Total count of 0.001 duration loops encountered', color='grey')
    plt.savefig('trend_cumulative_full.png')

    # --- Plot 2: Percentage of Zero Cost Loops ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Data Points", y="Zero Cost %", hue="Database", linewidth=2)
    plt.suptitle('Trend 2: Percentage of Zero-Cost Loops', fontweight='bold')
    plt.title('How often zero-cost loops occur relative to total entries', color='grey')
    plt.ylabel('Percentage (%)')
    plt.savefig('trend_zero_percentage_full.png')

    # --- Plot 3: Percentage of Non-Zero Cost Loops ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Data Points", y="Non-Zero Cost %", hue="Database", linewidth=2)
    plt.suptitle('Trend 3: Percentage of Non-Zero-Cost Loops', fontweight='bold')
    plt.title('Workload distribution: Percentage of loops requiring > 0.001 cost', color='grey')
    plt.ylabel('Percentage (%)')
    plt.savefig('trend_nonzero_percentage_full.png')

    print("All three plots have been saved to your directory.")