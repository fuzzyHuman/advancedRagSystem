
from pymongo.mongo_client import MongoClient # type: ignore
from pymongo.server_api import ServerApi # type: ignore
import uuid

uri = "mongodb+srv://sharmasudeepiit:KUk2sppvfdIgjLpv@insurancedetails.coenc.mongodb.net/?retryWrites=true&w=majority&appName=InsuranceDetails"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['InsuranceDetails']
collection = db['paramSummary']
