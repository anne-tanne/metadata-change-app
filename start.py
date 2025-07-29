#!/usr/bin/env python3
"""
Smart startup script for Metadata Editor
Automatically detects available ports and starts both frontend and backend
"""

import os
import sys
import time
import json
import socket
import subprocess
import threading
from pathlib import Path

def find_free_port(start_port=5000):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def check_port_in_use(port):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', port))
            return True
    except OSError:
        return False

def update_package_json(backend_port):
    """Update frontend package.json with the correct backend port"""
    package_json_path = Path("frontend/package.json")
    
    if not package_json_path.exists():
        print("❌ frontend/package.json not found")
        return False
    
    try:
        with open(package_json_path, 'r') as f:
            data = json.load(f)
        
        # Update proxy
        data['proxy'] = f"http://localhost:{backend_port}"
        
        with open(package_json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated frontend proxy to http://localhost:{backend_port}")
        return True
    except Exception as e:
        print(f"❌ Failed to update package.json: {e}")
        return False

def update_app_py(backend_port):
    """Update backend app.py with the correct port"""
    app_py_path = Path("app.py")
    
    if not app_py_path.exists():
        print("❌ app.py not found")
        return False
    
    try:
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        # Update the port in app.run()
        import re
        pattern = r'app\.run\(debug=False, host=\'0\.0\.0\.0\', port=\d+\)'
        replacement = f'app.run(debug=False, host=\'0.0.0.0\', port={backend_port})'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            
            with open(app_py_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated backend port to {backend_port}")
            return True
        else:
            print("⚠️  Could not find app.run() line in app.py")
            return False
    except Exception as e:
        print(f"❌ Failed to update app.py: {e}")
        return False

def start_backend(port):
    """Start the backend server"""
    print(f"🚀 Starting backend on port {port}...")
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ Backend started successfully on http://localhost:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend(port):
    """Start the frontend server"""
    print(f"🚀 Starting frontend on port {port}...")
    try:
        os.chdir("frontend")
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        os.chdir("..")
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        if process.poll() is None:
            print(f"✅ Frontend started successfully on http://localhost:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import flask
        import PIL
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check if frontend node_modules exists
    if not Path("frontend/node_modules").exists():
        print("❌ Frontend dependencies not installed")
        print("Run: cd frontend && npm install")
        return False
    
    print("✅ All dependencies OK")
    return True

def main():
    print("🎯 Smart Metadata Editor Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Find available ports
    print("\n🔍 Finding available ports...")
    
    backend_port = find_free_port(5000)
    if not backend_port:
        print("❌ No available ports found for backend")
        return
    
    frontend_port = find_free_port(3000)
    if not frontend_port:
        print("❌ No available ports found for frontend")
        return
    
    print(f"✅ Backend port: {backend_port}")
    print(f"✅ Frontend port: {frontend_port}")
    
    # Update configuration files
    print("\n⚙️  Updating configuration...")
    
    if not update_package_json(backend_port):
        print("⚠️  Continuing without updating package.json")
    
    if not update_app_py(backend_port):
        print("⚠️  Continuing without updating app.py")
    
    # Start servers
    print("\n🚀 Starting servers...")
    
    backend_process = start_backend(backend_port)
    if not backend_process:
        print("❌ Failed to start backend")
        return
    
    frontend_process = start_frontend(frontend_port)
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    # Success message
    print("\n" + "=" * 50)
    print("🎉 Metadata Editor is running!")
    print("=" * 50)
    print(f"📱 Frontend: http://localhost:{frontend_port}")
    print(f"🔧 Backend:  http://localhost:{backend_port}")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
        # Stop processes
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        print("✅ Servers stopped")

if __name__ == "__main__":
    main() 