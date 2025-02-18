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
def home() -> Response:
    '''Route which render home page'''
    return render_template('home.html')

@app.route('/send-email', methods=['POST'])
def send_email() -> tuple[Response, int]:
    '''Function handle sending message on email through form'''
    try:
        name = request.form.get('name')
        sender_email = request.form.get('email')
        message_text = request.form.get('message')

        if not name or not sender_email or not message_text:
            return jsonify({'error': 'Missing form fields'}), 400
        recipient_email: str = os.getenv('MAIL_USERNAME') or ""
        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=sender_email,
            recipients=[recipient_email] if recipient_email else [],
            body=f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_text}"
        )

        mail.send(msg)

        return jsonify({'success': 'Email sent successfully!'}), 200
    except (ValueError, requests.exceptions.RequestException, smtplib.SMTPException) as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webcamera-app')
def get_webcamera_pic() -> Response:
    '''Route which render webcamera application'''
    return render_template('webcamera_app.html', WEBCAMERA_APP_URL=WEBCAMERA_APP_URL)

@app.route('/upload', methods=['POST'])
def upload_photo() -> tuple[Response, int]:
    '''Receives an image from the frontend and forwards it to the webcamera service'''
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        files = {'image': (request.files['image'].filename, request.files['image'].read(), 'image/jpeg')}
        response = requests.post(f'{WEBCAMERA_APP_URL}/upload', files=files, timeout=30)

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Webcamera service unavailable', 'details': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename: str) -> Response:
    '''Download image from server by URL'''
    response = requests.get(f'{WEBCAMERA_APP_URL}/download/{filename}', timeout=20)
    if response.status_code == 200:
        url = response.json().get('url')
        return redirect(url)
    return jsonify({'error': 'File not found or already deleted.'}), response.status_code

@app.route('/wiki-app', methods=['GET', 'POST'])
def wiki_app():
    '''Handle request to wikipedia from user'''
    if request.method == 'POST':
        query = request.form['query']

        response = requests.post(f"{WIKI_APP_URL}/query", json={'query': query}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return render_template('wiki_app.html', title=data['title'], summary=data['summary'], url=data['url'], main_image=data['main_image'])
        if response.status_code == 404:
            error_message = response.json().get('error', 'Article nor found.')
            return render_template('wiki_app.html', error=error_message)

        return render_template('wiki_app.html', error="An error occured while fetching data.")

    return render_template('wiki_app.html')

@app.route('/db-app')
def db_app() -> Response:
    '''Route which render DataBase manager template'''
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
    response = requests.post(f'{DB_APP_URL}/add-client', json=client_data, timeout=30)
    if response.status_code == 201:
        return jsonify({"success": True, "message": "Client added successfully!"})
    return jsonify({"success": False, "message": "Failed to add client."})

@app.route('/update-client/<client_id>', methods=['POST'])
def update_client(client_id: str) -> Response:
    '''Send request to DataBase handler to update data'''
    update_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.put(f'{DB_APP_URL}/update-client/{client_id}', json=update_data, timeout=30)
    return jsonify(response.json()), response.status_code

@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id: str) -> Response:
    '''Send request to delete client'''
    response = requests.delete(f'{DB_APP_URL}/delete-client/{client_id}', timeout=30)
    return jsonify(response.json()), response.status_code

@app.route('/search-clients', methods=['GET'])
def search_clients():
    '''Handle search request'''
    params = {
        "name": request.args.get("name"),
        "surname": request.args.get("surname"),
        "product": request.args.get("product")
    }
    response = requests.get(f'{DB_APP_URL}/search-clients', params=params, timeout=30)
    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
