#!/usr/bin/env python3
"""
Network App Starter
Runs the Flask app on local network and displays access information
"""

import socket
import webbrowser
from app_with_users import app, init_db
import os

def get_local_ip():
    """Get the local IP address"""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def display_network_info(host, port):
    """Display network access information"""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🚀 Flask App Started Successfully!")
    print("=" * 60)
    print(f"🏠 Local access: http://localhost:{port}")
    print(f"🌐 Network access: http://{local_ip}:{port}")
    print("=" * 60)
    print("📱 Other devices on your WiFi can access the app using:")
    print(f"   http://{local_ip}:{port}")
    print("=" * 60)
    print("👤 Default Admin Account:")
    print("   Username: youcef")
    print("   Password: kadari")
    print("=" * 60)
    print("✨ Features Available:")
    print("   • User Registration & Login")
    print("   • Product Catalog with Images")
    print("   • Order Management")
    print("   • Admin Panel")
    print("   • User Profiles")
    print("   • Network Image Serving")
    print("=" * 60)
    print("🖼️  Images are now served correctly across network!")
    print("   Upload images in admin panel and they'll be visible")
    print("   on all devices connected to your WiFi.")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Configuration
    host = '0.0.0.0'  # Listen on all interfaces
    port = 5000
    
    # Display network information
    display_network_info(host, port)
    
    try:
        # Start the Flask application
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for using the app!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Make sure port 5000 is available and try again.")
