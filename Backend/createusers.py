from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Crypto     
users = db.users        

user_list = [
          { 
            "name" : "Christopher Rankin",
            "username" : "Chris",  
            "password" : b"chris_r",
            "email" : "chris.rankin90@googlemail.com",
            "admin" : True,
            "notes": [],
            "transactionfavourites": [],
            "addressfavourites": [],
            "blockfavourites": []
          },


       ]

for new_user_user in user_list:
      new_user_user["password"] = bcrypt.hashpw(new_user_user["password"], bcrypt.gensalt())
      users.insert_one(new_user_user)
