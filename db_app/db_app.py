from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Set up MongoDB client (pointing to MongoDB Docker container)
client = MongoClient('mongodb://mongo:27017/')
db = client['e_shop']
collection = db['clients']

@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.json
    client_data = {
        "name": data.get("name"),
        "surname": data.get("surname"),
        "email": data.get("email"),
        "shipping_address": data.get("shipping_address"),
        "products": data.get("products", [])
    }
    result = collection.insert_one(client_data)
    return jsonify({"message": "Client added successfully", "id": str(result.inserted_id)}), 201

@app.route('/update_client/<client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.json
    update_fields = {
        "name": data.get("name"),
        "surname": data.get("surname"),
        "email": data.get("email"),
        "shipping_address": data.get("shipping_address"),
        "products": data.get("products", [])
    }
    result = collection.update_one({"_id": client_id}, {"$set": update_fields})
    if result.matched_count > 0:
        return jsonify({"message": "Client updated successfully"}), 200
    else:
        return jsonify({"error": "Client not found"}), 404

@app.route('/delete_client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    result = collection.delete_one({"_id": client_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Client deleted successfully"}), 200
    else:
        return jsonify({"error": "Client not found"}), 404

@app.route('/search_clients', methods=['GET'])
def search_clients():
    name = request.args.get('name')
    surname = request.args.get('surname')
    product = request.args.get('product')

    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if surname:
        query["surname"] = {"$regex": surname, "$options": "i"}
    if product:
        query["products"] = {"$regex": product, "$options": "i"}

    results = list(collection.find(query))
    clients = [{
        "_id": str(client["_id"]),
        "name": client["name"],
        "surname": client["surname"],
        "email": client["email"],
        "shipping_address": client["shipping_address"],
        "products": client["products"]
    } for client in results]

    return jsonify(clients), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Runs on a separate port within the network
