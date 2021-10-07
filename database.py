from pymongo import MongoClient
import pymongo
import certifi
import uuid
import datetime

def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://mongoUser:PWD12345@mongodbcluster.5kxf3.mongodb.net/MongoDBCluster?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING,ssl_ca_certs=certifi.where())

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['MongoDBCluster']

def insertOneItem(request,response):
    id = str(uuid.uuid4())

    today = datetime.date.today()
    date = str(today.year)+'-'+str(today.month)+'-'+str(today.day)

    request = {
    "_id" : id,
    "request" : request,
    "date" : date,
    "response" : response
    }
    
    collection_name.insert_one(request)


dbname = get_database()

collection_name = dbname["AIAppRequests"] #if not exist create one DATABASE WITH THIS NAME

item_details = collection_name.find()

#insertedRow = insertOneItem('asd','asd')