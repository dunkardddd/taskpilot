from flask import Flask
from threading import Thread
import os
import time

app = Flask('')

@app.route('/')
def home():
    return f"Discord Task Bot is alive! Uptime: {time.time()}"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/status')
def status():
    return {
        "status": "online",
        "bot": "Discord Task Bot",
        "uptime": time.time(),
        "message": "Bot is running and ready to accept commands"
    }

def run():
    # Use lighter configuration for Replit
    app.run(
        host='0.0.0.0', 
        port=8080, 
        debug=False,
        use_reloader=False,
        threaded=True
    )

def keep_alive():
    """Start the keep-alive web server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive server started on port 8080")

# WSGI application for Gunicorn
application = app
