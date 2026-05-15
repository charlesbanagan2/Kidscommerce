"""
Run the Flask app with ngrok for public internet access.
This creates a secure tunnel to your local server.
"""

from pyngrok import ngrok
import subprocess
import sys

# Start ngrok tunnel
print("Starting ngrok tunnel...")
tunnel = ngrok.connect(5000)
print(f"Public URL: {tunnel.public_url}")
print("Share this URL to make your website accessible from anywhere!")
print("\nPress Ctrl+C to stop the server.")

# Start Flask app
try:
    subprocess.run([sys.executable, "app.py"])
except KeyboardInterrupt:
    print("\nStopping ngrok tunnel...")
    ngrok.disconnect(tunnel.public_url)
    print("Tunnel closed.")
