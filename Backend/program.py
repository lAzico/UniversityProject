from json import JSONDecodeError, JSONDecoder
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
import datetime
from functools import wraps
import bcrypt
import requests
from functools import lru_cache
import datetime
import json
import jwt
from decimal import Decimal
import uuid
from flask_limiter import Limiter

app = Flask(__name__)
CORS(app)

limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
app.config['SECRET_KEY'] = 'mysecret'

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Crypto
users = db.users

# ---------------------------------------------


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1]
            print(token)

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = data['username']
            current_user = db.users.find_one({'username': username})
        except:
            
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
# ---------------------------------------------


# ---------------------------------------------
def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            print("Token:", token)
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                print("Decoded data:", data)
                if data["admin"] == True:
                    return func(*args, **kwargs)
                else:
                    return make_response(jsonify({'message': 'Admin access required'}), 401)
            except Exception as e:
                print(f"Exception: {e}")
                return make_response(jsonify({'message': 'Invalid token'}), 400)
        else:
            return make_response(jsonify({'message': 'Token header not found'}), 400)
    return admin_required_wrapper



# ---------------------------------------------


@app.route("/api/v1.0/signup", methods=["POST"])
def add_user():
    data = request.get_json()
    password = data["password"]
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    new_user = {
        "name": data["name"],
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
        "admin": False,
        "notes": [],
        "transactionfavourites": [],
        "addressfavourites": [],
        "blockfavourites": []
    }

    new_user_id = users.insert_one(new_user)
    new_user_link = \
        "http://localhost:5000/api/v1.0/userprofile/" \
        + str(new_user_id.inserted_id)
    return make_response(jsonify(
        {"url": new_user_link}), 201)
# ---------------------------------------------

# ---------------------------------------------
@app.route('/api/v1.0/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users.find_one({'email': username})
    if user is not None:
        if bcrypt.checkpw(bytes(str(password), 'UTF-8'), user["password"]):
            token = jwt.encode(
                {'username': username,
                 '_id': str(user["_id"]),
                 'admin': user["admin"],
                 'name': user["name"],
                 'exp': datetime.datetime.utcnow() +
                 datetime.timedelta(minutes=30)
                 }, app.config['SECRET_KEY'])
            return make_response(jsonify(
                {'token': token.encode('UTF-8').decode('UTF-8')}), 200)
        else:
            return make_response(jsonify(
                {'message': 'Bad username or password'}), 401)
    else:
        return make_response(jsonify(
            {'message': 'No user found'}), 401)

# ---------------------------------------------


# ---------------------------------------------
@app.route("/api/v1.0/userprofile/<string:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    user = users.find_one({"_id": ObjectId(id)})

    if data['admin']:
        admin = bool(json.loads(data['admin']))
        edited_user = {
            "name": data["name"],
            "password": data[b"password"],
            "username": data["username"],
            "email": data["email"],
            "admin": admin,
            "transactionfavourites": user["transactionfavourites"],
            "notes": user["notes"],
            "addressfavourites": user["addressfavourites"],
            "blockfavourites": user["blockfavourites"]
            
        }

    edited_user_without_admin = {
        "name": data["name"],
        "username": data["username"],
        "email": data["email"],
        "password": data[b"password"],
        "notes": user["notes"],
        "transactionfavourites": user["transactionfavourites"],
        "addressfavourites": user["addressfavourites"],
        "blockfavourites": user["blockfavourites"]

    }

    if data['admin']:

        users.update_one({'_id': ObjectId(id)}, {'$set': edited_user})
    else:
        users.update_one({'_id': ObjectId(id)}, {
                         '$set': edited_user_without_admin})
    return jsonify({"message": "User updated successfully"})


# ---------------------------------------------


# ---------------------------------------------
@app.route('/api/v1.0/userprofile', methods=['POST'])
def userprofile():

    token = request.get_json()
    if not token:
        return jsonify({'message': 'No token present, please sign in'}), 400
    try:
        decodedtoken = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = decodedtoken['username']

        user = users.find_one({'email': username})
        if user is not None:
            result = {"_id": str(user["_id"]), "email": user["email"],
                      "name": user["name"], "admin": user["admin"]}
            return jsonify(result)
        else:
            return jsonify({'message': 'Bad user details'}), 401
    except jwt.exceptions.InvalidTokenError:
        return jsonify({'message': 'Invalid token format'}), 401
# ---------------------------------------------


# ---------------------------------------------


@app.route("/api/v1.0/user-manager",
           methods=["GET"])
@admin_required
@jwt_required
def fetch_all_users(*args):

    datatoReturn = []
    for user in users.find():
        user["_id"] = str(user["_id"])
        user['password'] = str(user['password'])

        for favourite in user["transactionfavourites"]:
            favourite["favourite_id"] = str(favourite["favourite_id"])
        for favourite in user["addressfavourites"]:
            favourite["favourite_id"] = str(favourite["favourite_id"])
        for favourite in user["blockfavourites"]:
            favourite["favourite_id"] = str(favourite["favourite_id"])
        for note in user["notes"]:
            note["_id"] = str(note["_id"])
        datatoReturn.append(user)
        # print(datatoReturn)

    return make_response(jsonify(
        datatoReturn), 200)


# ---------------------------------------------

@app.route("/api/v1.0/user-manager/<string:id>", methods=["DELETE"])
def delete_user(id):
    result = users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)

# ---------------------------------------------





# ---------------------------------------------


@app.route("/api/v1.0/userprofile/<string:id>",
           methods=["GET"])
def show_one_userprofile(id):

    id = str(ObjectId(id))
    user = users.find_one({'_id': id})
    if user is not None:
        user['_id'] = str(user['_id'])
        user['password'] = str(user['password'])
        for favourite in user['favourites']:
            favourite['_id'] = str(favourite['_id'])
        for note in user["notes"]:
            note["_id"] = str(note["_id"])
        return make_response(jsonify([user]), 200)
    else:
        return make_response(jsonify(
            {"error": "Invalid asset ID"}), 404)
# ---------------------------------------------


# ---------------------------------------------
@app.route("/api/v1.0/userprofile/<string:id>/favourites/all",
           methods=["GET"])
def fetch_all_favourites_user(id):
    data_to_return = []
    user = users.find_one(
        {"_id": ObjectId(id)},
        {"transactionfavourites": 1, "_id": 0} 
        or {"addressfavourites": 1, "_id": 0} 
        or {"blockfavourites": 1, "_id": 0})
    if user is not None:
        transaction_favourites = user.get("transactionfavourites", [])
        address_favourites = user.get("addressfavourites", [])
        block_favourites = user.get("blockfavourites", [])

        for favourite in transaction_favourites:
            favourite["favourite_id"] = str(favourite["favourite_id"])
            favourite["favouriteType"] = favourite.get("favouriteType", "")  # Add the favouriteType property
            data_to_return.append(favourite)

        for favourite in address_favourites:
            favourite["favourite_id"] = str(favourite["favourite_id"])
            favourite["favouriteType"] = favourite.get("favouriteType", "")
            data_to_return.append(favourite)

        for favourite in block_favourites:
            favourite["favourite_id"] = str(favourite["favourite_id"])
            favourite["favouriteType"] = favourite.get("favouriteType", "")
            data_to_return.append(favourite)

        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error": "User was not found"}), 404)
# ---------------------------------------------

# ---------------------------------------------

@app.route("/api/v1.0/userprofile/<string:id>/favourites", methods=["POST"])
@limiter.limit("1 per 3 seconds")
def add_favourite(id):
    data = request.get_json()
    user = users.find_one({"_id": ObjectId(id)})
    if user is not None:
        if data.get("favouriteType") == "transaction":
            data["favourite_id"] = str(uuid.uuid4())
            for favourite in user["transactionfavourites"]:
                if data["Transaction Hash"] == favourite["Transaction Hash"]:
                    return make_response(jsonify({"message": "Transaction already added to favourites"}), 400)
            users.update_one({"_id": ObjectId(id)}, {
                             "$push": {"transactionfavourites": data}})
            return make_response(jsonify({"message": "Favourite added", "favourite_id": data["favourite_id"]}), 200)
        elif data.get("favouriteType") == "address":
            data["favourite_id"] = str(uuid.uuid4())
            if ((data["Address"] or data["address"]) == user["addressfavourites"]["Address"] or user["addressfavourites"]["address"]):
                return make_response(jsonify({"message": "Address already added to favourites"}), 400)
            users.update_one({"_id": ObjectId(id)}, {
                             "$push": {"addressfavourites": data}})
            return make_response(jsonify({"message": "Favourite added", "favourite_id": data["favourite_id"]}), 200)
        elif data.get("favouriteType") == "block":
            if((data["Block Number"] or data["blockNumber"]) == user["blockfavourites"]["Block Number"] or user["blockfavourites"]["blockNumber"]):
                data["favourite_id"] = str(uuid.uuid4())
                return make_response(jsonify({"message": "Block already added to favourites"}), 400)
            users.update_one({"_id": ObjectId(id)}, {
                             "$push": {"blockfavourites": data}})
            return make_response(jsonify({"message": "Favourite added", "favourite_id": data["favourite_id"]}), 200)
    else:
        return make_response(jsonify({"error": "Invalid favourite ID"}), 404)

# ---------------------------------------------


@app.route("/api/v1.0/user-manager/<string:id>",
           methods=["GET"])
def show_one_user(id):
    user = users.find_one({'_id': ObjectId(id)})
    if user is not None:
        user['_id'] = str(user['_id'])
        user['password'] = str(user['password'])
        for note in user['notes']:
            note['_id'] = str(note['_id'])
            for favourite in user['favourites']:
                favourite['favourite_id'] = str(favourite['favourite_id'])

        return make_response(jsonify([user]), 200)
    else:
        return make_response(jsonify(
            {"error": "Invalid asset ID"}), 404)
# ---------------------------------------------

# ---------------------------------------------


@app.route("/api/v1.0/userprofile/<bid>/favourites/<rid>/<favourite_type>",
           methods=["GET"])
def fetch_one_favourite_user(bid, rid, favourite_type):

    if favourite_type == "transaction":
        favourite_key = "transactionfavourites"
    elif favourite_type == "address":
        favourite_key = "addressfavourites"
    elif favourite_type == "block":
        favourite_key = "blockfavourites"
    else:
        return make_response(jsonify({"error": "Invalid favourite type"}), 400)
    user = users.find_one(
        {f"{favourite_key}._id": ObjectId(bid)},
        {"_id": 0, f"{favourite_key}.$": 1})
    
    if user is None:
        return make_response(
            jsonify(
                {"error": "Invalid asset ID or favourite ID"}), 404)
    user = users.find_one(
        {f"{favourite_key}._id": ObjectId(rid)},
        {"_id": 0, f"{favourite_key}.$": 1})

    return make_response(jsonify(
        user['favourites'][0]), 200)
# ---------------------------------------------


# ---------------------------------------------
@app.route("/api/v1.0/userprofile/<bid>/favourites/<rid>/<favourite_type>",
           methods=["DELETE"])
def delete_user_favourite(bid, rid, favourite_type):
    if favourite_type == "transaction":
        favourite_key = "transactionfavourites"
    elif favourite_type == "address":
        favourite_key = "addressfavourites"
    elif favourite_type == "block":
        favourite_key = "blockfavourites"
    else:
        return make_response(jsonify({"error": "Invalid favourite type"}), 400)
    users.update_one(
        {"_id": ObjectId(bid)},
        {"$pull": {favourite_key: {"favourite_id": rid}}})

    return make_response(jsonify({}), 204)
# ---------------------------------------------




# ---------------------------------------------
@app.route('/api/v1.0/userprofile', methods=['GET'])
def get_user_profile():

    headers = {'authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il9jVzR0blVsZEE3bktGUGt5RjUzZSJ9.eyJpc3MiOiJodHRwczovL2Rldi1qZzNpcHRsN2ptY2dwbXVsLnVrLmF1dGgwLmNvbS8iLCJzdWIiOiJvejl0a0FFS1IybEtDcjdRdmhHUkFxUWZuckxkOVVObEBjbGllbnRzIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo0MjAwL2FwaS92MS4wL3VzZXJwcm9maWxlIiwiaWF0IjoxNjczMDY2NjI4LCJleHAiOjE2NzMxNTMwMjgsImF6cCI6Im96OXRrQUVLUjJsS0NyN1F2aEdSQXFRZm5yTGQ5VU5sIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.Z12PdkwwvbLjg2YZkJmE4UjMhJqwcLv8Bye4JJ7G3zSebm3Afb58HAMFZrpyMyNF5WO86IFqjDQK3F1_MyDFEuSbbA67ELmIusZBkj9c-zDT5SDGleKywjZ9DIlpt0Wkm4aHUhY1j2ebLRhxR9G7KkzX2rgTn98896BcDtcKd5VYgKpcDg-JHgxcTYy9AOZnjdA2YEXBtxxNmXiVWlGIt1w6dOt8OBr-wQFK0zLtmCI0JhHYF_Kci0HxPnLrHCidUBcxFAWfNWUhsPyuvvmS1qJV1pTnmlV40155kWU5zQxchEvkVtypT67N4_i5P36ISyculs-fTgMr6y42cSdU2w"}

    response = requests.get(
        "http://localhost:4200/api/v1.0/userprofile", headers=headers)

    return response
# ---------------------------------------------


# # ---------------------------------------------


@app.route('/api/v1.0/Search', methods=['POST'])
@limiter.limit("10 per minute")
def get_api_url():

    requestdata = request.get_json()
    network = requestdata['network']
    query_type = requestdata['querytype']
    query = requestdata['query']
    field = requestdata.get('field')
    offset = requestdata.get('offset', 10)
    api_key_bc = 'G___zsQPYZjPGyTGmNcUlmR1BHFSI7K8'
    base_url_bc = "https://api.blockchair.com"
    page = requestdata.get('page', 1)
    if network == 'ethereum':
        api_key_eth = 'SKSU9DYC77XECN63MWKW3FRZA6YMWAD4M6'

        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_eth)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})

        elif query_type == "address":
            address_data = get_address_data(network, query, api_key_eth, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify(network, query, api_key_eth, page, field, offset)
                # return jsonify({"error": "Error fetching address data or address not found."})

        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_eth)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})
            
    elif network == "avalanche":
        api_key_avax = '5A5TI2XZ9BCVBU2114BAMG1DTKFW9STT33'
        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_avax)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})

        elif query_type == "address":
            address_data = get_address_data(network, query, api_key_avax, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})

        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_avax)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})

    elif network == "polygon":
        api_key_polygon = 'SCM96EWYC438DUC7KMJRG4DFETR4315RID'
        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_polygon)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})

        elif query_type == "address":
            address_data = get_address_data(
                network, query, api_key_polygon, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})

        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_polygon)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})

    elif network == "binance":
        api_key_binance = 'EZF8BXBD1PHNT7SB64V7SV82XHK6INZSQB'
        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_binance)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})

        elif query_type == "address":
            address_data = get_address_data(
            network, query, api_key_binance, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})

        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_binance)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})


    elif network == "fantom":
        api_key_ftm = 'W864NVTNJUD2N5W7H7CM84JQ4U6DYWR21C'
        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_ftm)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})

        elif query_type == "address":
            address_data = get_address_data(network, query, api_key_ftm, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})

        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_ftm)

            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})

    elif network == "ripple":
        api_key_ripple = api_key_bc
        if query_type == "transaction":
            transaction_data = get_transaction_data(
                network, query, api_key_ripple)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})
        
        elif query_type == "address":
            address_data = get_address_data(network, query, api_key_ripple, page, field, offset)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})
        
        elif query_type == "block":
            block_data = get_block_data(network, query, api_key_ripple)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching ledger data or ledger not found, also Ledgers up to #79223976 are unavailable."})
            
    

    # Any blockchair API call
    else:
        if query_type == "transaction":
            transaction_data = get_transaction_data_bc(network, query, api_key_bc)
            if transaction_data:
                return jsonify(transaction_data)
            else:
                return jsonify({"error": "Error fetching transaction data or transaction not found."})
            
        elif query_type == "address":
            address_data = get_address_data_bc(network, query, api_key_bc)
            if address_data:
                return jsonify(address_data)
            else:
                return jsonify({"error": "Error fetching address data or address not found."})
        
        elif query_type == "block":
            block_data = get_block_data_bc(network, query, api_key_bc)
            if block_data:
                return jsonify(block_data)
            else:
                return jsonify({"error": "Error fetching block data or block not found."})
        
            
        
def get_transaction_data_bc(network, query, api_key):
    base_url = "https://api.blockchair.com"
    url = f"{base_url}/{network}/dashboards/transaction/{query}?key={api_key}"
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        json_data = response.json()
        transaction_data = json_data["data"]

        if transaction_data:
            transaction = transaction_data[query]["transaction"]
            inputs = json_data["data"][query]["inputs"]
            outputs = json_data["data"][query]["outputs"]
            transaction_fee = transaction["fee"] / 100000000
            

            recipients = []
            for output in outputs:
                recipients.append({
                        "Recipient": output["recipient"],
                        "value": output["value"] / 100000000,
                        "value_usd": output["value_usd"],
                        "Coinbase transaction": output["is_from_coinbase"],
                        "Block Number": output["block_id"],
                        "Timestamp": output["time"],
                        "Transaction Hash": output["transaction_hash"]
                    })

            senders = []
            for input in inputs:
                senders.append({
                        "Sender": input["recipient"],
                        "value": input["value"] / 100000000,
                        "value_usd": input["value_usd"],
                        "Coinbase transaction": input["is_from_coinbase"],
                        "Block Number": input["block_id"],
                        "Timestamp": input["time"],
                        "Transaction Hash": input["transaction_hash"]
                    })
            


            if not inputs:
                inputs = [{"recipient": "No inputs"}]
            if not outputs:
                outputs = [{"recipient": "No outputs"}]
            if recipients == []:
                recipients = "No recipients"
            if senders == []:
                senders = "No senders"
            
            result = {
                "Transaction Hash": transaction["hash"],
                "Block Number": transaction["block_id"],
                "Value sent": transaction["output_total"] / 100000000,
                "Value sent (USD)": transaction["output_total_usd"],
                "Transaction Fee": transaction_fee,
                "Transaction Fee (USD)": transaction["fee_usd"],
                "address_from": inputs[0]["recipient"],
                "Current market price USD": json_data["context"]["market_price_usd"],
                "Timestamp": transaction["time"],
                "Recipients": recipients,
                "Output Count": transaction["output_count"],
                "Input Count": transaction["input_count"],
                "Senders": senders,

                
            }
            return result
    
    return {"error": "Error fetching transaction data or transaction not found."}

    

def get_address_data_bc(network, query, api_key):
    base_url = "https://api.blockchair.com"
    url = f"{base_url}/{network}/dashboards/address/{query}?transaction_details=true&limit=500&key={api_key}"
    print(url)
    result = {}
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        data = json_data["data"]
        transactions_data = []
        address_info = {
            "address": data[query],
            "Balance": data[query]["address"]["balance"] / 100000000,
            "Balance USD": data[query]["address"]["balance_usd"],
            "Received": data[query]["address"]["received"],
            "Spent": data[query]["address"]["spent"],
            "Transaction Count": data[query]["address"]["transaction_count"],
            "First Seen Receiving": data[query]["address"]["first_seen_receiving"],
            "Last Seen Receiving": data[query]["address"]["last_seen_receiving"],
            "First Seen Spending": data[query]["address"]["first_seen_spending"],
            "Last Seen Spending": data[query]["address"]["last_seen_spending"],
        }

        for tx in data[query]["transactions"]:
            balance_change = tx["balance_change"] / 100000000
            balance_status = "received" if balance_change > 0 else "sent"
            tx_data = {
                "Block Number": tx["block_id"],
                "Timestamp": tx["time"],
                "Transaction hash": tx["hash"],
                "Value": balance_change,
                "Value USD": balance_change * json_data["context"]["market_price_usd"],
                "Balance status": balance_status,
                
            }

            transactions_data.append(tx_data)


            

        context_data = json_data["context"]
        market_price_usd = context_data["market_price_usd"]
        result['Address'] = address_info
        result['Transactions'] = transactions_data
        result['Market Price USD'] = market_price_usd

    return result

def get_block_data_bc(network, query, api_key):
    base_url = "https://api.blockchair.com"
    url = f"{base_url}/{network}/dashboards/block/{query}?limit=10000&key={api_key}"
    response = requests.get(url)
    print(url)

    if response.status_code == 200:
        data = response.json().get("data", {}).get(query)
        transactions = data["transactions"]
        block_data = data['block']
        if block_data:
            block_data = {
                "Block Number": block_data["id"],
                "Timestamp": block_data["time"],
                "Transaction Count": block_data["transaction_count"],
                "Difficulty": block_data["difficulty"],
                "Input Count": block_data["input_count"],
                "Input Total": block_data["input_total"] / 100000000,
                "Input Total (USD)": block_data["input_total_usd"],
                "Output Count": block_data["output_count"],
                "Output Total": block_data["output_total"] / 100000000,
                "Output Total (USD)": block_data["output_total_usd"],
                "Fee": block_data["fee_total"] / 100000000,
                "Fee (USD)": block_data["fee_total_usd"],
                "Reward": block_data["reward"] / 100000000,
                "Reward (USD)": block_data["reward_usd"],
                "Guessed Miner": block_data["guessed_miner"],
            }
            transactions_data = []
            for tx in transactions:
                transactions_data.append({
                    "Transaction Hash": tx,
                })
            block_data["Transactions"] = transactions_data
            
        
        
        return block_data
    return None
     


# Block data for non-bitcoin chains (apart from ripple)
def get_block_data(network, query, api_key):
    if network == "ethereum":
        api_url = 'https://api.etherscan.io/api?module=block&action=getblockreward&blockno='
        api_url_2 = 'https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber&tag='
    elif network == "avalanche":
        api_url = 'https://api.snowtrace.io/api?module=block&action=getblockreward&blockno='
        api_url_2 = 'https://api.snowtrace.io/api?module=proxy&action=eth_getBlockByNumber&tag='
    elif network == "binance":
        api_url = 'https://api.bscscan.com/api?module=block&action=getblockreward&blockno='
        api_url_2 = 'https://api.bscscan.com/api?module=proxy&action=eth_getBlockByNumber&tag='
    elif network == "polygon":
        api_url = 'https://api.polygonscan.com/api?module=block&action=getblockreward&blockno='
        api_url_2 = 'https://api.polygonscan.com/api?module=proxy&action=eth_getBlockByNumber&tag='
    elif network == "fantom":
        api_url = 'https://api.ftmscan.com/api?module=block&action=getblockreward&blockno='
        api_url_2 = 'https://api.ftmscan.com/api?module=proxy&action=eth_getBlockByNumber&tag='
    elif network == "ripple":
        api_url = 'https://api.blockchair.com/ripple/raw/ledger/'
        api_url_request = api_url + query + '?transactions=true&key=' + api_key
        print(api_url_request)
        response = requests.get(api_url_request)
        if response.status_code == 200:
            data = response.json()['data'][query]
            result = {}
            context = response.json()['context']
            market_price_usd = context['market_price_usd']
            ledger_data = response.json()['data'][query]['ledger']
            transactions = ledger_data['transactions']
            for tx in transactions:
                tx['Fee'] = int(tx['Fee']) / 1000000
            ledger_data['total_coins'] = int(ledger_data['total_coins']) / 100000000
            
            result['Transactions'] = transactions
            result['Market Price USD'] = market_price_usd
            result['Ledger Data'] = ledger_data
            
            if result:
                return result
            return None
        else:
            return None
    api_url_request = api_url + query + '&apikey=' + api_key
    api_url_request_2 = api_url_2 + \
        hex(int(query)) + '&boolean=true&apikey=' + api_key
    response = requests.get(api_url_request)
    response2 = requests.get(api_url_request_2)
    block_data_result = None
    transactions_result = None

    if response.status_code == 200:
        data = response.json()
        block_data = data.get("result")
        if block_data:
            if block_data["blockNumber"] is None or block_data["timeStamp"] is None:
                block_data_result = None
            else:
                uncles = block_data.get("uncles", [])

                uncle_data = []
                for uncle in uncles:
                    uncle_data.append({
                        "Uncle miner": uncle["miner"],
                        "Uncle position": uncle["unclePosition"],
                        "Uncle reward": int(uncle["blockreward"]) / 1e18,
                    })
                block_data_result = {
                    "Block number": block_data["blockNumber"],
                    "Timestamp": datetime.datetime.fromtimestamp(int(block_data['timeStamp'])),
                    "Block miner":  block_data["blockMiner"],
                    "Block reward": int(block_data["blockReward"]) / 1e18,
                    "Uncles": uncle_data,
                    "Uncle inclusion reward": int(block_data["uncleInclusionReward"]) / 1e18,
                }
        else:
            return None
    if response2.status_code == 200:
        data2 = response2.json()
        transactions_data = data2.get("result")
        if transactions_data:
            transactions = transactions_data.get("transactions", [])

            processed_transactions = []
            for tx in transactions:
                tx_hash = tx["hash"]
                block_number = int(tx["blockNumber"], 16)
                from_address = tx["from"]
                to_address = tx["to"]
                value = int(tx["value"], 16) / 1e18
                gas_fee = int(tx["gas"], 16) * int(tx["gasPrice"], 16) / 1e18

                processed_transactions.append({
                    "tx_hash": tx_hash,
                    "block_number": block_number,
                    "from_address": from_address,
                    "to_address": to_address,
                    "value": value,
                    "gas_fee": gas_fee,
                })

            transactions_result = processed_transactions
        else:
            return None

    if block_data_result is None and transactions_result is None:
        return None
    elif block_data_result is None:
        return transactions_result
    elif transactions_result is None:
        return block_data_result
    else:
        return (block_data_result, transactions_result)


def is_contract_address(network: str, address: str, apikey: str) -> bool:
    if network == 'ethereum':
        api_url = f'https://api.etherscan.io/api?module=proxy&action=eth_getCode&address={address}&apikey={apikey}'
    elif network == 'avalanche':
        api_url = f'https://api.snowtrace.io/api?module=proxy&action=eth_getCode&address={address}&apikey={apikey}'
    elif network == 'binance':
        api_url = f'https://api.bscscan.com/api?module=proxy&action=eth_getCode&address={address}&apikey={apikey}'
    elif network == 'polygon':
        api_url = f'https://api.polygonscan.com/api?module=proxy&action=eth_getCode&address={address}&apikey={apikey}'
    elif network == 'fantom':
        api_url = f'https://api.ftmscan.com/api?module=proxy&action=eth_getCode&address={address}&apikey={apikey}'
    else:
        raise ValueError(f'Invalid network "{network}"')
    response = requests.get(api_url).json()
    if response['result'] != '0x':
        return True
    else:
        return False
        

def get_transaction_data(network, query, api_key):
    if network == 'ethereum':
        api_url = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt&txhash='
        api_url2 = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash='
    elif network == 'avalanche':
        api_url = 'https://api.snowtrace.io/api?module=proxy&action=eth_getTransactionReceipt&txhash='
        api_url2 = 'https://api.snowtrace.io/api?module=proxy&action=eth_getTransactionByHash&txhash='
    elif network == 'binance':
        api_url = 'https://api.bscscan.com/api?module=proxy&action=eth_getTransactionReceipt&txhash='
        api_url2 = 'https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash='
    elif network == 'polygon':
        api_url = 'https://api.polygonscan.com/api?module=proxy&action=eth_getTransactionReceipt&txhash='
        api_url2 = 'https://api.polygonscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash='
    elif network == 'fantom':
        api_url = 'https://api.ftmscan.com/api?module=proxy&action=eth_getTransactionReceipt&txhash='
        api_url2 = 'https://api.ftmscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash='
    elif network == 'ripple':
        api_url = 'https://api.blockchair.com/ripple/raw/transaction/'
        api_url_request = api_url + query + '?key=' + api_key
        response = requests.get(api_url_request)

        if response.status_code == 200:
            data = response.json()
            transaction = data.get("data").get(query)
            context = data.get("context")
            AffectedNodes = []
            if 'TakerGets' not in transaction:
                transaction["TakerGets"] = ''
            if 'TakerPays' not in transaction:
                transaction["TakerPays"] = ''
                
            if transaction:
                result={
                    "Transaction Hash": query,
                    "Account": transaction["Account"],
                    "Timestamp": (datetime.datetime.fromtimestamp(transaction["date"]) + datetime.timedelta(days=365*30, hours=-1) + datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    "Fee": int(transaction["Fee"]) / 1e6,
                    "Sequence": transaction["Sequence"],
                    "Transaction Type": transaction["TransactionType"],
                    "TxnSignature": transaction["TxnSignature"],
                    "Flags": transaction["Flags"],
                    "In Ledger": transaction["inLedger"],
                    "Ledger": transaction["ledger_index"],
                    "Affected Nodes": AffectedNodes,
                    "Market Price (USD)": context["market_price_usd"],
                    "Status": transaction["status"],
                    "Validated": transaction["validated"],
                    "TakerGets": transaction["TakerGets"],
                    "TakerPays": transaction["TakerPays"],

                }


                for i in transaction["meta"]["AffectedNodes"]:

                    result["Affected Nodes"].append(i)


                return result
            
        else:
            return None


    else:
        raise ValueError(f'Invalid network "{network}"')
    
    api_url_request = api_url + query + '&apikey=' + api_key    
    api_url_request2 = api_url2 + query + '&apikey=' + api_key
    response = requests.get(api_url_request)
    response2 = requests.get(api_url_request2)
    if response.status_code == 200:
        data = response.json()
        data2= response2.json()
        transaction = data.get("result")
        transaction_more_information = data2.get("result")
        logs = []
        
        if transaction:  # Check if transaction is not None
            result = {
                "Transaction Hash": transaction["transactionHash"],
                "Block Number": int(transaction["blockNumber"], 16),
                "Transaction Index": int(transaction["transactionIndex"], 16),
                "Block Hash": transaction["blockHash"],
                "Cumulative Gas Used": int(transaction["cumulativeGasUsed"], 16) / 1e9,
                "Gas Used": int(transaction["gasUsed"], 16 ),
                "Status": "Success" if transaction.get("status") == "0x1" else "Failed",
                "Effective Gas Price (Gwei)": (int(transaction["effectiveGasPrice"], 16) / 1e9),
                "Type": transaction.get("type"),
                "Value sent": int(transaction_more_information["value"], 16) / 1e18,
                "Nonce": int(transaction_more_information["nonce"], 16),
                           }
            if is_contract_address(network, transaction["to"], api_key) == True:
                address_to_field = "contract_to"
            else:
                address_to_field = "address_to"
            result[address_to_field] = transaction["to"]
            if is_contract_address(network, transaction["from"], api_key) == True:
                address_from_field = "contract_from"
            else:
                address_from_field = "address_from"
            result[address_from_field] = transaction["from"]
            if transaction["logs"]:
                for log in transaction["logs"]:
                    if len(log["topics"]) >= 3:
                        from_address = (log["topics"][1])
                        to_address = (log["topics"][2])
                    else:
                        from_address = None
                        to_address = None
                    if (log["data"] != "0x"):
                        transfer_amount = Decimal(int(log["data"], 16)) / Decimal(10**18)
                    else:
                        transfer_amount = 0
                    logs.append({
                    "ERC-20 Address": log["address"],
                    "ERC-20 Transfer amount": transfer_amount,
                    "From": from_address,
                    "To": to_address,
                    })
            result[address_from_field] = transaction["from"]
            transaction["logs"] = logs
            result["ERC-20 Transfers"] = logs
            return result
        else:
            return None

# Address data for non-bitcoin chains and ripple
def normal_transactions(api_key, page, query, api_url, offset):
    if offset == 10:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page='+ str(page) + '&offset=10&apikey=' + api_key
    else:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page=' + str(page) + '&offset=' + str(offset) +'&apikey=' + api_key
    
    response = requests.get(api_url_request)
    print(api_url_request)
    data = response.json()
    transactions_info = []
    if data['result']:
        for tx in data['result']:
            tx_info = {
                    "Transaction hash": (tx['hash']),
                    "From": tx['from'],
                    "To": tx['to'],
                    "Value": (int(tx["value"])/ 1000000000000000000),
                    "Timestamp": datetime.datetime.fromtimestamp(int(tx['timeStamp'])),
                    "Block Number": tx['blockNumber'],
                    "Gas used": (int(tx["gasUsed"])),
                    "Gas price": (int(tx["gasPrice"])),
                    "function name": tx["functionName"],
                }
            transactions_info.append(tx_info)
    else:
        print("No transactions found")
    return transactions_info

def internal_transactions(api_key, page, query, api_url, offset):
    if offset == 10:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page='+ str(page) + '&offset=10&apikey=' + api_key
    else:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page=' + str(page) + '&offset=' + str(offset) +'&apikey=' + api_key
    
    response = requests.get(api_url_request)
    print(api_url_request)
    data = response.json()
    internal_transactions_info = []
    data = response.json()
    for tx in data['result']:
        tx_info = {
            "Transaction hash": str(tx['hash']),
            "From": tx['from'],
            "To": tx['to'],
            "Timestamp": datetime.datetime.fromtimestamp(int(tx['timeStamp'])),
            "Block Number": tx['blockNumber'],
            "Gas": int(tx["gas"]) / 1e9,
            "Value": '{:.18f}'.format(int(tx["value"])/ 10**18),
            "Type": tx["type"],
            }
        # Append transaction information to the list
        internal_transactions_info.append(tx_info)
    return internal_transactions_info

def erc20_transactions(api_key, page, query, api_url, offset):
    if offset == 10:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page='+ str(page) + '&offset=10&apikey=' + api_key
    else:
        api_url_request = api_url + query + '&startblock=0&endblock=99999999&page=' + str(page) + '&offset=' + str(offset) +'&apikey=' + api_key
    
    response = requests.get(api_url_request)
    print(api_url_request)
    data = response.json()
    transactions_info_tokens = []
    token_balances = {}
    for tx in data['result']:
        tx_tokens_info = {
            "Transaction hash": str(tx['hash']),
            "From": tx['from'],
            "To": tx['to'],
            "Value": int(tx["value"], 16) / 1e18,
            "Timestamp": datetime.datetime.fromtimestamp(int(tx['timeStamp'])),
            "Block Number": tx['blockNumber'],
            "Gas": int(tx["gas"], 16) / 1e9,
            "ERC-20 Address": tx["contractAddress"],
            "ERC-20 Transfer amount": Decimal(int(tx["value"], 16)) / Decimal(10**18),
            "From": tx["from"],
            "To": tx["to"],
            }
            # Extract token information
        token_symbol = tx['tokenSymbol']
        token_decimals = int(tx['tokenDecimal'])
        token_amount = int(tx["value"]) / (10 ** token_decimals)

            # Update token balances
        if token_symbol not in token_balances:
            token_balances[token_symbol] = 0

        if tx['to'].lower() == query.lower():
            token_balances[token_symbol] += token_amount
        elif tx['from'].lower() == query.lower():
            token_balances[token_symbol] -= token_amount
                # Append transaction information to the list
            
        # Append transaction information to the list
        transactions_info_tokens.append(tx_tokens_info)
    return transactions_info_tokens, token_balances
def get_address_data(network, query, api_key, page, field, offset):
    result = {}
    
    if field == "transactions":
        if network == "ethereum":
            api_url = 'https://api.etherscan.io/api?module=account&action=txlist&address='
        elif network == "avalanche":
            api_url = 'https://api.snowtrace.io/api?module=account&action=txlist&address='
        elif network == "binance":
            api_url = 'https://api.bscscan.com/api?module=account&action=txlist&address='
        elif network == "polygon":
            api_url = 'https://api.polygonscan.com/api?module=account&action=txlist&address='
        elif network == "fantom":
            api_url = 'https://api.ftmscan.com/api?module=account&action=txlist&address='
        else:
            raise ValueError(f'Invalid network "{network}"')
        return normal_transactions(api_key, page, query, api_url, offset), field

    elif field == "internal_transactions":
        if network == "ethereum":
            api_url = 'https://api.etherscan.io/api?module=account&action=txlistinternal&address='
        elif network == "avalanche":
            api_url = 'https://api.snowtrace.io/api?module=account&action=txlistinternal&address='
        elif network == "binance":
            api_url = 'https://api.bscscan.com/api?module=account&action=txlistinternal&address='
        elif network == "polygon":
            api_url = 'https://api.polygonscan.com/api?module=account&action=txlistinternal&address='
        elif network == "fantom":
            api_url = 'https://api.ftmscan.com/api?module=account&action=txlistinternal&address='
        else:
            raise ValueError(f'Invalid network "{network}"')
        return internal_transactions(api_key, page, query, api_url, offset), field
    
    elif field == "erc20_transactions":
        if network == "ethereum":
            api_url = 'https://api.etherscan.io/api?module=account&action=tokentx&address='
        elif network == "avalanche":
            api_url = 'https://api.snowtrace.io/api?module=account&action=tokentx&address='
        elif network == "binance":
            api_url = 'https://api.bscscan.com/api?module=account&action=tokentx&address='
        elif network == "polygon":
            api_url = 'https://api.polygonscan.com/api?module=account&action=tokentx&address='
        elif network == "fantom":
            api_url = 'https://api.ftmscan.com/api?module=account&action=tokentx&address='
        else:
            raise ValueError(f'Invalid network "{network}"')
        return erc20_transactions(api_key, page, query, api_url, offset), field
    else:
        

        if network == "ethereum":
            api_url = 'https://api.etherscan.io/api?module=account&action=balance&address='
            api_url_2 = 'https://api.etherscan.io/api?module=account&action=txlist&address='
            api_url_3 = 'https://api.etherscan.io/api?module=account&action=txlistinternal&address='
            api_url_4 = 'https://api.etherscan.io/api?module=account&action=tokentx&address='
        elif network == "avalanche":
            api_url = 'https://api.snowtrace.io/api?module=account&action=balance&address='
            api_url_2 = 'https://api.snowtrace.io/api?module=account&action=txlist&address='
            api_url_3 = 'https://api.snowtrace.io/api?module=account&action=txlistinternal&address='
            api_url_4 = 'https://api.snowtrace.io/api?module=account&action=tokentx&address='
        elif network == "binance":
            api_url = 'https://api.bscscan.com/api?module=account&action=balance&address='
            api_url_2 = 'https://api.bscscan.com/api?module=account&action=txlist&address='
            api_url_3 = 'https://api.bscscan.com/api?module=account&action=txlistinternal&address='
            api_url_4 = 'https://api.bscscan.com/api?module=account&action=tokentx&address='
        elif network == "polygon":
            api_url = 'https://api.polygonscan.com/api?module=account&action=balance&address='
            api_url_2 = 'https://api.polygonscan.com/api?module=account&action=txlist&address='
            api_url_3 = 'https://api.polygonscan.com/api?module=account&action=txlistinternal&address='
            api_url_4 = 'https://api.polygonscan.com/api?module=account&action=tokentx&address='
        elif network == "fantom":
            api_url = 'https://api.ftmscan.com/api?module=account&action=balance&address='
            api_url_2 = 'https://api.ftmscan.com/api?module=account&action=txlist&address='
            api_url_3 = 'https://api.ftmscan.com/api?module=account&action=txlistinternal&address='
            api_url_4 = 'https://api.ftmscan.com/api?module=account&action=tokentx&address='
        elif network == "ripple":
            api_url = 'https://api.blockchair.com/ripple/raw/account/'
            api_url_request = api_url + query + '?transactions=true&assets=true&key=' + api_key
            print(api_url_request)
            response = requests.get(api_url_request)
            response_json = response.json()
            account_data = response_json['data'][query]['account']['account_data']
            assets = response_json['data'][query]['assets']
            
            transactions_data = []
            if response.status_code == 200:
                account_data['Balance'] = int(account_data['Balance']) / 1000000
                for transaction in response_json['data'][query]['transactions']['transactions']:
                    transactions_data.append(transaction['tx']) 
                    transaction['tx']['date'] = (datetime.datetime.fromtimestamp(transaction['tx']["date"]) + datetime.timedelta(days=365*30, hours=-1) + datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    transaction['tx']['Fee'] = float(transaction['tx']['Fee']) / 1000000
                    if 'TakerPays' in transaction['tx']:
                        transaction['tx']['TakerPays'] = float(transaction['tx']['TakerPays']['value']) / 1000000
                    else:
                        transaction['tx']['TakerPays'] = 0

                result = {
                    "Account Data": account_data,
                    "Transactions": transactions_data,
                    "Assets": assets,
                }
                return result
            else:
                return None
            

        api_url_request = api_url + query + '&apikey=' + api_key
        if network == "ethereum":
            api_url_request2 = "https://api.blockchair.com/ethereum/dashboards/address/" + query + '?erc_20=true&key=G___zsQPYZjPGyTGmNcUlmR1BHFSI7K8'
            print(api_url_request2)
            response2 = requests.get(api_url_request2)

            if response2.status_code == 200:
                response_json2 = response2.json()
                portfolio_data = []

                layer_2_data = response_json2.get('data', {}).get(query, {}).get('layer_2', None)

                if layer_2_data is not None:
                    tokens = layer_2_data.get('erc_20', [])

                    for token in tokens:
                        portfolio_data.append(token)

                    result["Portfolio"] = portfolio_data



        

        normaltransactions = normal_transactions(api_key, page, query, api_url_2, offset)
        internaltransactions = internal_transactions(api_key, page, query, api_url_3, offset)
        erc20transactions = erc20_transactions(api_key, page, query, api_url_4, offset)


        response = requests.get(api_url_request)
        response_json = response.json()
        balance = response_json['result']
        balance = int(balance) / 1000000000000000000
        balance = round(balance, 4)
        

        result["Balance"] = balance
        result["Transactions"] = normaltransactions
        result["Internal Transactions"] = internaltransactions
        result["ERC-20 Transactions"] = erc20transactions
        return result

def get_transactions_internal(transaction_hash, network, api_key):
    if network == 'ethereum':
        api_url = 'https://api.etherscan.io/api?module=account&action=txlistinternal&address='
    elif network == 'avalanche':
        api_url = 'https://api.snowtrace.io/api?module=account&action=txlistinternal&address='
    elif network == 'binance':
        api_url = 'https://api.bscscan.com/api?module=account&action=txlistinternal&address='
    elif network == 'polygon':
        api_url = 'https://api.polygonscan.com/api?module=account&action=txlistinternal&address='
    elif network == 'fantom':
        api_url = 'https://api.ftmscan.com/api?module=account&action=txlistinternal&address='

        api_url_request = api_url + transaction_hash + \
            '&startblock=0&endblock=999999999&' + 'page=1' + '&apikey=' + api_key
        response = requests.get(api_url_request)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                transactions = data['result']
                # Create an empty list to store transactions information
                for tx in transactions:
                    tx_info = {
                        "Transaction hash": str(tx['hash']),
                        "From": tx['from'],
                        "To": tx['to'],
                        "Value": int(tx["value"], 16) / 1e18,
                        "Timestamp": datetime.datetime.fromtimestamp(int(tx['timeStamp'])),
                        "Type": tx['type'],
                        "Block Number": tx['blockNumber'],
                        "Gas": int(tx["gasPrice"], 16) / 1e9,
                    }

                    return tx_info


def get_price(network, api_key):

    if network == 'ethereum':
        api_url = 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey='
    elif network == 'avalanche':
        api_url = 'https://api.snowtrace.io/api?module=stats&action=ethprice&apikey='
    elif network == 'binance':
        api_url = 'https://api.bscscan.com/api?module=stats&action=ethprice&apikey='
    elif network == 'polygon':
        api_url = 'https://api.polygonscan.com/api?module=stats&action=ethprice&apikey='
    elif network == 'fantom':
        api_url = 'https://api.ftmscan.com/api?module=stats&action=ethprice&apikey='
    api_url_request = api_url + api_key
    response = requests.get(api_url_request)
    if response.status_code == 200:
        data = response.json()
        if data['result']:
            price = data['result']['ethusd']
            return price
    else:
        return None


# # ---------------------------------------------

# ---------------------------------------------
@app.route('/api/v1.0/HomePage', methods=['GET'])
def get_homepage_details():
    API_KEY_ETH = 'SKSU9DYC77XECN63MWKW3FRZA6YMWAD4M6'
    API_KEY_AVAX = '5A5TI2XZ9BCVBU2114BAMG1DTKFW9STT33'
    API_KEY_FTM = 'W864NVTNJUD2N5W7H7CM84JQ4U6DYWR21C'
    API_KEY_BINANCE = 'EZF8BXBD1PHNT7SB64V7SV82XHK6INZSQB'
    API_KEY_BC = 'G___zsQPYZjPGyTGmNcUlmR1BHFSI7K8'

    # Get latest block number Ethereum
    latest_block_url = "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=" + API_KEY_ETH

    # Get latest block number Avalanche
    latest_block_url2 = "https://api.snowtrace.io/api?module=proxy&action=eth_blockNumber&apikey=" + API_KEY_AVAX

    # Get latest block number for Fantom
    latest_block_url3 = "https://api.ftmscan.com/api?module=proxy&action=eth_blockNumber&apikey=" + API_KEY_FTM

    # Get latest block number for Binance Smart Chain
    latest_block_url4 = "https://api.bscscan.com/api?module=proxy&action=eth_blockNumber&apikey=" + API_KEY_BINANCE

    latest_block_url5 = f"https://api.blockchair.com/bitcoin/stats?key={API_KEY_BC}"

    #Ethereum API
    EtherResponse = requests.get(latest_block_url)
    #Avalanche API
    AvaxResponse = requests.get(latest_block_url2)
    #Fantom API
    FtmResponse = requests.get(latest_block_url3)
    #Binance Smart Chain API
    BscResponse = requests.get(latest_block_url4)

    

    latest_block_number = int(EtherResponse.json()["result"], 16)
    latest_block_number2 = int(AvaxResponse.json()["result"], 16)
    latest_block_number3 = int(FtmResponse.json()["result"], 16)
    latest_block_number4 = int(BscResponse.json()["result"], 16)



    transactions_eth = []
    transactions_avax = []
    transactions_ftm = []
    transactions_bsc = []


    # Get price of blockchain's native token in USD

    # Get price of Ethereum
    price_eth = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={API_KEY_ETH}"
    price_eth_response = requests.get(price_eth)
    price_eth_json = price_eth_response.json()
    price_eth_usd = price_eth_json["result"]["ethusd"]

    # Get price of Avalanche
    price_avax = f"https://api.snowtrace.io/api?module=stats&action=ethprice&apikey={API_KEY_AVAX}"
    price_avax_response = requests.get(price_avax)
    price_avax_json = price_avax_response.json()
    price_avax_usd = price_avax_json["result"]["ethusd"]

    # Get price of Fantom
    price_ftm = f"https://api.ftmscan.com/api?module=stats&action=ftmprice&apikey={API_KEY_FTM}"
    price_ftm_response = requests.get(price_ftm)
    price_ftm_json = price_ftm_response.json()
    price_ftm_usd = price_ftm_json["result"]["ethusd"]

    # Get price of Binance Smart Chain
    price_bsc = f"https://api.bscscan.com/api?module=stats&action=bnbprice&apikey={API_KEY_BINANCE}"
    price_bsc_response = requests.get(price_bsc)
    price_bsc_json = price_bsc_response.json()
    price_bsc_usd = price_bsc_json["result"]["ethusd"]
    

    # Get gas price in Gwei of Ethereum blockchains and Binance Smart Chain

    # Get gas price of Ethereum
    gas_price_eth = f"https://api.etherscan.io/api?module=proxy&action=eth_gasPrice&apikey={API_KEY_ETH}"
    gas_price_eth_response = requests.get(gas_price_eth)
    gas_price_eth_json = gas_price_eth_response.json()
    gas_price_eth_gwei = int(gas_price_eth_json["result"], 16) / 1e9

    # Get gas price of Avalanche
    gas_price_avax = f"https://api.snowtrace.io/api?module=proxy&action=eth_gasPrice&apikey={API_KEY_AVAX}"
    gas_price_avax_response = requests.get(gas_price_avax)
    gas_price_avax_json = gas_price_avax_response.json()
    gas_price_avax_gwei = int(gas_price_avax_json["result"], 16) / 1e9
    
    # Get gas price of Fantom
    gas_price_ftm = f"https://api.ftmscan.com/api?module=proxy&action=eth_gasPrice&apikey={API_KEY_FTM}"
    gas_price_ftm_response = requests.get(gas_price_ftm)
    gas_price_ftm_json = gas_price_ftm_response.json()
    gas_price_ftm_gwei = int(gas_price_ftm_json["result"], 16) / 1e9

    # Get gas price of Binance Smart Chain
    gas_price_bsc = f"https://api.bscscan.com/api?module=proxy&action=eth_gasPrice&apikey={API_KEY_BINANCE}"
    gas_price_bsc_response = requests.get(gas_price_bsc)
    gas_price_bsc_json = gas_price_bsc_response.json()
    gas_price_bsc_gwei = int(gas_price_bsc_json["result"], 16) / 1e9


    # Get transactions from latest 5 blocks for Ethereum-based blockchains and Binance Smart Chain
    while len(transactions_eth) < 5 or len(transactions_avax) < 5 or len(transactions_ftm) < 5 or len(transactions_bsc) < 5:
        block_number_hex = hex(latest_block_number)
        block_number_hex2 = hex(latest_block_number2)
        block_number_hex3 = hex(latest_block_number3)
        block_number_hex4 = hex(latest_block_number4)
        block_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber&tag={block_number_hex}&boolean=true&apikey={API_KEY_ETH}"
        block_url2 = f"https://api.snowtrace.io/api?module=proxy&action=eth_getBlockByNumber&tag={block_number_hex2}&boolean=true&apikey={API_KEY_AVAX}"
        block_url3 = f"https://api.ftmscan.com/api?module=proxy&action=eth_getBlockByNumber&tag={block_number_hex3}&boolean=true&apikey={API_KEY_FTM}"
        block_url4 = f"https://api.bscscan.com/api?module=proxy&action=eth_getBlockByNumber&tag={block_number_hex4}&boolean=true&apikey={API_KEY_BINANCE}"
        

        #Ethereum API
        EtherResponse = requests.get(block_url)
        #Avalanche API
        AvaxResponse = requests.get(block_url2)
        #Fantom API
        FtmResponse = requests.get(block_url3)
        #Binance Smart Chain API
        BscResponse = requests.get(block_url4)

        block_data = EtherResponse.json()["result"]
        block_data2 = AvaxResponse.json()["result"]
        block_data3 = FtmResponse.json()["result"]
        block_data4 = BscResponse.json()["result"]

        for tx in block_data["transactions"]:
            if len(transactions_eth) <5:
                filtered_tx = {
                    "blockNumber": int(tx["blockNumber"], 16),
                    "from": tx["from"],
                    "to": tx["to"],
                    "gas": int(tx["gas"], 16),
                    "gasPrice": int(tx["gasPrice"], 16) / 1e9,  # Convert to Gwei
                    "hash": tx["hash"],
                    "value": int(tx["value"], 16) / 1e18,  # Convert to Ether
                }
                transactions_eth.append(filtered_tx)
            
            else:
                break
        
        if len(transactions_eth) < 5:
            latest_block_number -= 1
        
        for tx in block_data2["transactions"]:
            if len(transactions_avax) <5:
                filtered_tx = {
                    "blockNumber": int(tx["blockNumber"], 16),
                    "from": tx["from"],
                    "to": tx["to"],
                    "gas": int(tx["gas"], 16),
                    "gasPrice": int(tx["gasPrice"], 16) / 1e9,  # Convert to Gwei
                    "hash": tx["hash"],
                    "value": int(tx["value"], 16) / 1e18,  # Convert to Ether
                }
                transactions_avax.append(filtered_tx)
            
            else:
                break
        
        if len(transactions_avax) < 5:
            latest_block_number2 -= 1

        
        for tx in block_data3["transactions"]:
            if len(transactions_ftm) <5:
                filtered_tx = {
                    "blockNumber": int(tx["blockNumber"], 16),
                    "from": tx["from"],
                    "to": tx["to"],
                    "gas": int(tx["gas"], 16),
                    "gasPrice": int(tx["gasPrice"], 16) / 1e9,  # Convert to Gwei
                    "hash": tx["hash"],
                    "value": int(tx["value"], 16) / 1e18,  # Convert to Ether
                }
                transactions_ftm.append(filtered_tx)
            
            else:
                break

        if len(transactions_ftm) < 5:
            latest_block_number3 -= 1
        
        for tx in block_data4["transactions"]:
            if len(transactions_bsc) <5:
                filtered_tx = {
                    "blockNumber": int(tx["blockNumber"], 16),
                    "from": tx["from"],
                    "to": tx["to"],
                    "gas": int(tx["gas"], 16),
                    "gasPrice": int(tx["gasPrice"], 16) / 1e9,  # Convert to Gwei
                    "hash": tx["hash"],
                    "value": int(tx["value"], 16) / 1e18,  # Convert to Ether
                }
                transactions_bsc.append(filtered_tx)
            
            else:
                break
        
        if len(transactions_bsc) < 5:
            latest_block_number4 -= 1

    return jsonify([{"Token name": "ETH", "network": "Ethereum", "Transactions": transactions_eth, "Latest block number": latest_block_number, "Price": price_eth_usd, "Gas price": gas_price_eth_gwei},
                {"Token name": "AVAX","network": "Avalanche", "Transactions": transactions_avax, "Latest block number": latest_block_number2, "Price": price_avax_usd, "Gas price": gas_price_avax_gwei},
                {"Token name": "FTM","network": "Fantom", "Transactions": transactions_ftm, "Latest block number": latest_block_number3, "Price": price_ftm_usd, "Gas price": gas_price_ftm_gwei},
                {"Token name": "BSC","network": "Binance", "Transactions": transactions_bsc, "Latest block number": latest_block_number4, "Price": price_bsc_usd, "Gas price": gas_price_bsc_gwei}])
# ---------------------------------------------

# ---------------------------------------------
@app.route("/api/v1.0/Stats" , methods=["GET"])
def get_stats():
    url = "https://api.blockchair.com/internal/markets?limit=1000"
    url2 = "https://api.blockchair.com/stats"
    url3 = "https://api.blockchair.com/tools/halvening"

    response = requests.get(url)
    data1 = response.json()["data"]
    response2 = requests.get(url2)
    data2 = response2.json()["data"]
    response3 = requests.get(url3)
    data3 = response3.json()["data"]
    result = {}
  


    for blockchain in data3:
        current_reward = data3[blockchain]["current_reward"] / 1e8
        next_reward = data3[blockchain]["halvening_reward"] / 1e8

        data3[blockchain]['current_reward'] = current_reward
        data3[blockchain]['halvening_reward'] = next_reward

    result["Top 1000"] = data1
    result["Stats"] = data2
    result["Halvening"] = data3

    return jsonify(result)


# ---------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
