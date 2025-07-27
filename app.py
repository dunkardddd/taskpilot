"""
Main application file for Render deployment
Starts Flask server immediately and Discord bot in background
"""
import os
import threading
from flask import Flask
from main import setup_and_run_bot

# Create Flask app for Render web service
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Taskpilot Discord Bot is alive! 🤖"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}

@app.route('/ping')
def ping():
    return "pong"

def start_discord_bot():
    """Start Discord bot in background thread"""
    setup_and_run_bot()

if __name__ == '__main__':
    # Start Discord bot in background thread
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask server on main thread (required for Render)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)