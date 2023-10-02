from flask import Flask
from threading import Thread
import subprocess

app = Flask('ProURL Bot')

@app.route('/')
def home():
  return "ProURL Telegram Bot is Running!"

def run_gunicorn():
    gunicorn_command = [
        'gunicorn',
        '-b', '0.0.0.0:8080',
        '-w', '4',
        'webserver:app',
    ]
    subprocess.Popen(gunicorn_command)

def keep_alive():
    t = Thread(target=run_gunicorn)
    t.start()