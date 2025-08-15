import os
import sys
import webbrowser
import time
from web_server import run_server

def main():
    print("🚀 Launching ORANGUTYPE Web Version...")
    print("=" * 50)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    required_files = ['index.html', 'style.css', 'web_server.py', 'backend.py', 'typing_logic.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please make sure all files are in the same directory.")
        return
    print("✅ All required files found")
    print("🌐 Starting web server...")
    import threading
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    print("🌍 Opening browser...")
    try:
        webbrowser.open('http://localhost:8000')
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please manually navigate to: http://localhost:8000")
    print("\n" + "=" * 50)
    print("🎯 ORANGUTYPE is now running!")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        print("👋 Thanks for using ORANGUTYPE!")

if __name__ == '__main__':
    main()
