# from pymongo import MongoClient, ASCENDING
# from pymongo import MongoClient, ASCENDING

# def refresh_target_subset(uri, db_name, source_col, target_col, n):
#     client = MongoClient(uri)
#     db = client[db_name]
    
#     source = db[source_col]
#     target = db[target_col]

#     # 1. Clear the target collection first
#     print(f"Cleaning '{target_col}'...")
#     target.delete_many({})

#     # 2. Fetch the first n entries sorted by timestamp
#     print(f"Fetching first {n} entries from '{source_col}'...")
#     cursor = source.find().sort("timestamp", ASCENDING).limit(n)
#     data = list(cursor)

#     # 3. Insert if data exists
#     if data:
#         result = target.insert_many(data)
#         print(f"Done! Copied {len(result.inserted_ids)} documents.")
#     else:
#         print("Source collection is empty. Nothing to copy.")

#     client.close()



# # Usage
# if __name__ == "__main__":
#     CONNECTION_URI = "mongodb://localhost:27017/"
#     DATABASE_NAME = "refine-plan-v2"
#     SOURCE = "pick-place-random"
#     TARGET = "pick-place-informed"
#     LIMIT = 455# Change this to your desired 'n'

#     refresh_target_subset(CONNECTION_URI, DATABASE_NAME, SOURCE, TARGET, LIMIT)