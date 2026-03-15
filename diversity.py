from pymongo import MongoClient, ASCENDING
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def fetch_data_trends(uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fields to track for diversity
    div_fields = [
        "column00", "column10", "column20", 
        "option", "motion", 
        "column0t", "column1t", "column2t"
    ]
    
    # Optimized fetch
    projection = {f: 1 for f in div_fields}
    projection.update({"duration": 1, "timestamp": 1})
    
    cursor = collection.find({}, projection).sort("timestamp", ASCENDING)
    
    zero_cost_loops = 0
    total_entries = 0
    seen_states = set() # To track unique combinations
    points = []
    
    for document in cursor:
        total_entries += 1
        
        # 1. Track Zero Cost Loops
        if document.get('duration') == 0.001:
            zero_cost_loops += 1
        else:
        
            # 2. Track Diversity
            # We create a tuple of the 8 fields to represent a "unique experience"
            state_signature = tuple(str(document.get(f, "")) for f in div_fields)
            seen_states.add(state_signature)
        
        # Calculate metrics
        zero_pct = (zero_cost_loops / total_entries) * 100
        diversity_count = len(seen_states)
        
        points.append({
            "Entries": total_entries, 
            "Zero Cost Loops": zero_cost_loops, 
            "Zero Cost %": zero_pct,
            "Non-Zero Cost %": 100 - zero_pct,
            "Unique Experiences": diversity_count,
            "Database": collection_name
        })

    return points

if __name__ == "__main__":
    CONNECTION_URI = "mongodb://localhost:27017/"
    DATABASE_NAME = "refine-plan-v2"
    collections =['example-a-random', 'example-a-informed','pick-place-random','pick-place-informed']#,'manipulator-informed-data']
    
    all_results = []
    for coll in collections:
        print(f"Processing diversity and trends for {coll}...")
        all_results.extend(fetch_data_trends(CONNECTION_URI, DATABASE_NAME, coll))

    df = pd.DataFrame(all_results)
    sns.set_theme(style="whitegrid")

    # --- Plot 4: Diversity (Cumulative Unique States) ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Entries", y="Unique Experiences", hue="Database", linewidth=2.5)
    
    plt.suptitle('Data Diversity: Unique Experiences Over Time', fontsize=16, fontweight='bold')
    plt.title('How many unique combinations of transitions have been seen', color='grey')
    plt.xlabel('Total Entries')
    plt.ylabel('Count of Unique Combinations')
    
    # Adding a "perfect diversity" reference line (Optional)
    # plt.plot([0, df['Entries'].max()], [0, df['Entries'].max()], 'k--', alpha=0.2, label='Perfect Diversity')
    
    sns.despine()
    plt.savefig('trend_diversity.png', dpi=300, bbox_inches='tight')
    
    # (The previous 3 plotting blocks would go here as well)
    print("Diversity plot saved as 'trend_diversity.png'.")