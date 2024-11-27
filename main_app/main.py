"""This is the main file, which run home page and has routs to other apps
To build and run this in Docker container, use:
docker build -t app_image .
docker run -d --name app --network my_network -p 5000:5000 app_image
"""
import os
from flask import Flask, render_template, redirect, request, jsonify
import requests

app = Flask(__name__)

DB_APP_URL = 'http://db_app:5001'
app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/webcamera-picture')
def get_webcamera_pic():
    return redirect('http://localhost:5454')

@app.route('/db_app')
def db_app():
    return render_template('db_app.html')

@app.route('/wiki_app')
def wiki_app():
    return redirect('http://localhost:8000')

@app.route('/add_client', methods=['POST'])
def add_client():
    client_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.post(f'{DB_APP_URL}/add_client', json=client_data)
    if response.status_code == 201:
        return jsonify({"success": True, "message": "Client added successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to add client."})

# Route to update a client via db_app microservice
@app.route('/update_client/<client_id>', methods=['POST'])
def update_client(client_id):
    update_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.put(f'{DB_APP_URL}/update_client/{client_id}', json=update_data)
    return jsonify(response.json()), response.status_code

# Route to delete a client via db_app microservice
@app.route('/delete_client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    response = requests.delete(f'{DB_APP_URL}/delete_client/{client_id}')
    return jsonify(response.json()), response.status_code

# Route to search clients via db_app microservice
@app.route('/search_clients', methods=['GET'])
def search_clients():
    params = {
        "name": request.args.get("name"),
        "surname": request.args.get("surname"),
        "product": request.args.get("product")
    }
    response = requests.get(f'{DB_APP_URL}/search_clients', params=params)
    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)