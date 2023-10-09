import pymongo
import json
from pymongo import MongoClient

# connect to local mongoDB
client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db["ulyssesChap1"]

collection_name = "ulyssesChap1"

# check if collection exists
if collection_name in db.list_collection_names():
    db[collection_name].drop()
    print(f"Collection '{collection_name}' has been dropped.")
else:
    print(f"Collection '{collection_name}' does not exist.")



# close client
client.close()