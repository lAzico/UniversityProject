# Update field name


# from pymongo import MongoClient
# from bson import ObjectId
# import uuid
# client = MongoClient("mongodb://127.0.0.1:27017")
# db = client.crypto
# businesses = db.assets
# for business in businesses.find():
#  businesses.update_many({}, {'$rename': {'Market Capitalization': 'marketCapitalization'}})
    
 
# Add fields

# from pymongo import MongoClient
# from bson import ObjectId
# import uuid

# client = MongoClient("mongodb://127.0.0.1:27017")
# db = client.crypto
# businesses = db.users
# for business in businesses.find():
#  businesses.update_one({'Available suppy': 'Available suppy'}, {'$set': {'Available suppy': 'availableSupply'}})

from pymongo import MongoClient
from bson import ObjectId
import uuid

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Crypto
businesses = db.users
for business in businesses.find():
 businesses.update_one(
    { "_id" : business['_id'] },
    {
        "$set" : {
            "notes" : [

            ]
        }
            
        }
    
 )



 #Delete fields       
            
# from pymongo import MongoClient
# from bson import ObjectId
# import uuid

# client = MongoClient("mongodb+srv://lazico:SimbaCat14!@cluster0.7xduv2k.mongodb.net/test")
# db = client.crypto
# businesses = db.users
# for business in businesses.update_one({'Network': 'Network'}, {'$unset': {'Network': 1}})       
    
 
