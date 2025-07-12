from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]
follows_collection = db["follows"]
# mongo_service.py
try:
    follows_collection.create_index("user_id", unique=True)
except Exception as e:
    print(f"MongoDB Index Creation Failed: {e}")

