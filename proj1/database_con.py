import pymongo
from pymongo import MongoClient

def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    #CONNECTION_STRING = "mongodb://172.16.3.26:27017/"
    CONNECTION_STRING = "mongodb://127.0.0.1:27017/"
    # CONNECTION_STRING = "14.98.66.46/32"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example
    db = client['hotwordDetection']

    # Creating a collection
    # collection = db["hotwordDetection"]
    return db     
