"""This is the main file, which run ho,me page and has routs to other apps
To build and run this in Docker container, use:
docker build -t app_image .
docker run -d --name app --network my_network -p 5000:5000 app_image
"""
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/webcamera-picture')
def get_webcamera_pic():
    return redirect('http://localhost:5454')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)