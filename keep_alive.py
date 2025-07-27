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
    port = int(os.environ.get('PORT', 8080))
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        use_reloader=False,
        threaded=True
    )

def keep_alive():
    """Start the keep-alive web server in a separate thread"""
    port = int(os.environ.get('PORT', 8080))
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print(f"🌐 Keep-alive server started on port {port}")

# WSGI application for Gunicorn
application = app
