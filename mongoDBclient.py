from pymongo.server_api import ServerApi
import getpass
import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri)
