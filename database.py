import datetime
import re
import uuid

import certifi
from pymongo import DESCENDING, MongoClient

import config

DATABASE_NAME = "MongoDBCluster"
COLLECTION_NAME = "AIAppRequests"
SEARCH_LIMIT = 50

_collection = None


def get_collection():
    # Connect lazily, so importing this module does not need a database
    global _collection
    if _collection is None:
        if not config.MONGO_URI:
            raise RuntimeError("MONGO_URI is not set, see .env.example")
        client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
        # MongoDB creates the collection on the first insert if it does not exist
        collection = client[DATABASE_NAME][COLLECTION_NAME]
        _ensure_indexes(collection)
        _collection = collection
    return _collection


def _ensure_indexes(collection):
    # create_index does nothing if the index already exists
    collection.create_index("request")
    collection.create_index([("date", DESCENDING)])


def insert_one_item(request, response):
    item = {
        "_id": str(uuid.uuid4()),
        "request": request,
        "date": datetime.datetime.now(datetime.timezone.utc),
        "response": response,
    }
    get_collection().insert_one(item)
    return item["_id"]


def find_cached_answer(question):
    """Return the newest stored answer for exactly this question, or None."""
    item = get_collection().find_one({"request": question}, sort=[("date", DESCENDING)])
    return item["response"] if item else None


def find_all_which(param, limit=SEARCH_LIMIT):
    # Escape the user input so it is matched as plain text, not as a regex
    pattern = {"$regex": re.escape(param), "$options": "i"}
    query = {"$or": [{"request": pattern}, {"response": pattern}]}
    return list(get_collection().find(query).sort("date", DESCENDING).limit(limit))
