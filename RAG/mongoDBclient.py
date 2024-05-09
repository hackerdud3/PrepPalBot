from pymongo.server_api import ServerApi
import os
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri)
