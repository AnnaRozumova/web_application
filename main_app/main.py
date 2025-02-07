"""This is the main file, which has a frontend of apps.
To build and run this in Docker container, use:
docker compose up --build -d
"""
import os
from flask import Flask, render_template, redirect, request, jsonify, Response
from dotenv import load_dotenv
import requests
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)

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
def home():
    return render_template('home.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        name = request.form.get('name')
        sender_email = request.form.get('email')
        message_text = request.form.get('message')

        if not name or not sender_email or not message_text:
            return jsonify({'error': 'Missing form fields'}), 400
        
        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=sender_email,
            recipients=[os.getenv('MAIL_USERNAME')],
            body=f"Name: {name}\Email: {sender_email}\n\nMessage:\n{message_text}"
        )

        mail.send(msg)

        return jsonify({'success': 'Email sent successfully!'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webcamera-app')
def get_webcamera_pic():
    return render_template('webcamera_app.html')

@app.route('/capture-photo', methods=['POST'])
def capture_photo():
    try:
        response = requests.post(f"{WEBCAMERA_APP_URL}/capture-photo", timeout=2)

        if response.status_code == 200:
            return Response(response.content, content_type=response.headers['Content-Type'])
        else:
            return jsonify({'error': 'Failed to capture photo', 'details': response.json()}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Service unavailable', 'details': str(e)}), 500

@app.route('/capture-and-save-photo', methods=['POST'])
def capture_and_save_photo():
    response = requests.post(f'{WEBCAMERA_APP_URL}/capture-and-save-photo', timeout=2)
    return jsonify(response.json()), response.status_code

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    response = requests.get(f'{WEBCAMERA_APP_URL}/download/{filename}', timeout=2)
    if response.status_code == 200:
        url = response.json().get('url')
        return redirect(url)
    return jsonify({'error': 'File not found or already deleted.'}), response.status_code

@app.route('/wiki-app', methods=['GET', 'POST'])
def wiki_app():
    if request.method == 'POST':
        query = request.form['query']

        response = requests.post(f"{WIKI_APP_URL}/query", json={'query': query}, timeout=3)

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
    response = requests.post(f'{DB_APP_URL}/add-client', json=client_data, timeout=2)
    if response.status_code == 201:
        return jsonify({"success": True, "message": "Client added successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to add client."})

@app.route('/update-client/<client_id>', methods=['POST'])
def update_client(client_id):
    update_data = {
        "name": request.form.get("name"),
        "surname": request.form.get("surname"),
        "email": request.form.get("email"),
        "shipping_address": request.form.get("shipping_address"),
        "products": request.form.getlist("products")
    }
    response = requests.put(f'{DB_APP_URL}/update-client/{client_id}', json=update_data, timeout=2)
    return jsonify(response.json()), response.status_code

@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    response = requests.delete(f'{DB_APP_URL}/delete-client/{client_id}', timeout=2)
    return jsonify(response.json()), response.status_code

@app.route('/search-clients', methods=['GET'])
def search_clients():
    params = {
        "name": request.args.get("name"),
        "surname": request.args.get("surname"),
        "product": request.args.get("product")
    }
    response = requests.get(f'{DB_APP_URL}/search-clients', params=params, timeout=2)
    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)