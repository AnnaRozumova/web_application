"""This is the main file, which has a frontend of apps.
To build and run this in Docker container, use:
docker compose up --build -d
"""
from flask import Flask, render_template, redirect, request, jsonify
import requests

app = Flask(__name__)

DB_APP_URL = 'http://db_app:5001'
WEBCAMERA_APP_URL = 'http://webcamera_app:5454'
WIKI_APP_URL = 'http://wiki_app:8000'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/webcamera-app')
def get_webcamera_pic():
    return render_template('webcamera_app.html')

@app.route('/capture-photo', methods=['POST'])
def capture_photo():
    response = requests.post(f'{WEBCAMERA_APP_URL}/capture-photo')
    return jsonify(response.json()), response.status_code

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    response = requests.get(f'{WEBCAMERA_APP_URL}/download/{filename}')
    if response.status_code == 200:
        url = response.json().get('url')
        return redirect(url)
    return jsonify({'error': 'File not found or already deleted.'}), response.status_code

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    response = requests.get(f'{WEBCAMERA_APP_URL}/uploads/{filename}')
    if response.status_code == 200:
        url = response.json().get('url')
        return redirect(url)
    return jsonify({'error': 'File not found or already deleted.'}), response.status_code

@app.route('/wiki-app', methods=['GET', 'POST'])
def wiki_app():
    if request.method == 'POST':
        query = request.form['query']

        response = requests.post(f"{WIKI_APP_URL}/query", json={'query': query})

        if response.status_code == 200:
            data = response.json()
            return render_template('wiki_app.html', title=data['title'], summary=data['summary'], url=data['url'], main_image=data['main_image'])
        elif response.status_code == 404:
            error_message = response.json().get('error', 'Article nor found.')
            return render_template('wiki_app.html', error=error_message)
        else:
            return render_template('wiki_app.html', error="An error occured while fetching data.")

    return render_template('wiki_app.html')

@app.route('/db-app')
def db_app():
    return render_template('db_app.html')

@app.route('/add-client', methods=['POST'])
def add_client():
    client_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.post(f'{DB_APP_URL}/add-client', json=client_data)
    if response.status_code == 201:
        return jsonify({"success": True, "message": "Client added successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to add client."})

# Route to update a client via db_app microservice
@app.route('/update-client/<client_id>', methods=['POST'])
def update_client(client_id):
    update_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.put(f'{DB_APP_URL}/update-client/{client_id}', json=update_data)
    return jsonify(response.json()), response.status_code

# Route to delete a client via db_app microservice
@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    response = requests.delete(f'{DB_APP_URL}/delete-client/{client_id}')
    return jsonify(response.json()), response.status_code

# Route to search clients via db_app microservice
@app.route('/search-clients', methods=['GET'])
def search_clients():
    params = {
        "name": request.args.get("name"),
        "surname": request.args.get("surname"),
        "product": request.args.get("product")
    }
    response = requests.get(f'{DB_APP_URL}/search-clients', params=params)
    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)