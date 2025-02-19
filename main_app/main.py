"""This is the main file, which has a frontend of apps.
To build and run this in Docker container, use:
docker compose up --build -d
"""
import os
import smtplib
from flask import Flask, render_template, redirect, request, jsonify, Response
from dotenv import load_dotenv
import requests
from flask_mail import Mail, Message
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_APP_URL = os.getenv('DB_APP_URL', 'http://db_app:5001')
WEBCAMERA_APP_URL = os.getenv('WEBCAMERA_APP_URL', 'http://webcamera_app:5454')
WIKI_APP_URL = os.getenv('WIKI_APP_URL', 'http://wiki_app:8000')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

@app.route('/')
def home() -> str:
    '''Route which render home page'''
    app.logger.info("Rendering home page")
    return render_template('home.html')

@app.route('/send-email', methods=['POST'])
def send_email() -> tuple[Response, int]:
    '''Function handle sending message on email through form'''
    try:
        name = request.form.get('name')
        sender_email = request.form.get('email')
        message_text = request.form.get('message')

        if not name or not sender_email or not message_text:
            app.logger.warning("Missing form fields in email request")
            return jsonify({'error': 'Missing form fields'}), 400
        recipient_email: str = os.getenv('MAIL_USERNAME') or ""
        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=sender_email,
            recipients=[recipient_email] if recipient_email else [],
            body=f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_text}"
        )

        mail.send(msg)
        app.logger.info("Email sent successfully from %s", sender_email)
        return jsonify({'success': 'Email sent successfully!'}), 200
    except (ValueError, requests.exceptions.RequestException, smtplib.SMTPException) as e:
        app.logger.error("Failed to send email: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/webcamera-app')
def get_webcamera_pic() -> str:
    '''Route which render webcamera application'''
    app.logger.info("Rendering WebCamera application")
    return render_template('webcamera_app.html', WEBCAMERA_APP_URL=WEBCAMERA_APP_URL)

@app.route('/upload', methods=['POST'])
def upload_photo() -> tuple[Response, int]:
    '''Receives an image from the frontend and forwards it to the webcamera service'''
    try:
        app.logger.info("Received request to upload an image")
        if 'image' not in request.files:
            app.logger.warning("No image file provided in request")
            return jsonify({'error': 'No image file provided'}), 400
        files = {'image': (request.files['image'].filename, request.files['image'].read(), 'image/jpeg')}
        response = requests.post(f'{WEBCAMERA_APP_URL}/upload', files=files, timeout=30)
        app.logger.info("Forwarding image to WebCamera service at %s", WEBCAMERA_APP_URL)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        app.logger.error("WebCamera service unavailable: %s", str(e), exc_info=True)
        return jsonify({'error': 'Webcamera service unavailable', 'details': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename: str) -> Response:
    '''Download image from server by URL'''
    app.logger.info("Attempting to download image: %s", filename)
    response = requests.get(f'{WEBCAMERA_APP_URL}/download/{filename}', timeout=20)
    if response.status_code == 200:
        url = response.json().get('url')
        app.logger.info("Redirecting to image URL: %s", url)
        return redirect(url)
    app.logger.warning("File not found or already deleted: %s", filename)
    return jsonify({'error': 'File not found or already deleted.'})

@app.route('/wiki-app', methods=['GET', 'POST'])
def wiki_app() -> str:
    '''Handle request to wikipedia from user'''
    if request.method == 'POST':
        query = request.form['query']
        app.logger.info("Searching Wikipedia for query: %s", query)
        response = requests.post(f"{WIKI_APP_URL}/query", json={'query': query}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            app.logger.info("Wikipedia search successful for query: %s", query)
            return render_template('wiki_app.html', title=data['title'], summary=data['summary'], url=data['url'], main_image=data['main_image'])
        if response.status_code == 404:
            error_message = response.json().get('error', 'Article nor found.')
            app.logger.warning("Wikipedia article not found: %s", query)
            return render_template('wiki_app.html', error=error_message)

        app.logger.error("Wikipedia service error for query: %s", query)
        return render_template('wiki_app.html', error="An error occured while fetching data.")

    return render_template('wiki_app.html')

@app.route('/db-app')
def db_app() -> str:
    '''Route which render DataBase manager template'''
    app.logger.info("Rendering database management page")
    return render_template('db_app.html')

@app.route('/add-client', methods=['POST'])
def add_client() -> Response:
    '''Collect data from the form and send request to DataBase handler to add client'''
    client_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    app.logger.info("Sending request to add new client: %s", client_data)
    response = requests.post(f'{DB_APP_URL}/add-client', json=client_data, timeout=30)
    if response.status_code == 201:
        app.logger.info("Client added successfully: %s", client_data)
        return jsonify({"success": True, "message": "Client added successfully!"})
    
    app.logger.warning("Failed to add client: %s", response.json())
    return jsonify({"success": False, "message": "Failed to add client."})

@app.route('/update-client/<client_id>', methods=['POST'])
def update_client(client_id: str) -> tuple[Response, int]:
    '''Send request to DataBase handler to update data'''
    update_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    app.logger.info("Updating client ID %s with data: %s", client_id, update_data)
    response = requests.put(f'{DB_APP_URL}/update-client/{client_id}', json=update_data, timeout=30)
    app.logger.info("Client ID %s updated successfully", client_id)
    return jsonify(response.json()), response.status_code

@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id: str) -> tuple[Response, int]:
    '''Send request to delete client'''
    app.logger.info("Attempting to delete client ID: %s", client_id)
    response = requests.delete(f'{DB_APP_URL}/delete-client/{client_id}', timeout=30)
    app.logger.info("Client ID %s deleted successfully", client_id)
    return jsonify(response.json()), response.status_code

@app.route('/search-clients', methods=['GET'])
def search_clients() -> tuple[Response, int]:
    '''Handle search request'''
    params = {
        "name": request.args.get("name"),
        "surname": request.args.get("surname"),
        "product": request.args.get("product")
    }
    app.logger.info("Searching clients with params: %s", params)
    response = requests.get(f'{DB_APP_URL}/search-clients', params=params, timeout=30)
    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.logger.info("Starting Flask server on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
