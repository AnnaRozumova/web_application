"""This is the main file, which run ho,me page and has routs to other apps"""
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/webcamera-picture')
def get_webcamera_pic():
    return redirect('http://webcamera_app:5454')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)