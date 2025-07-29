#!/usr/bin/env python3
"""
Setup script for MetaData Editor
Installs dependencies and sets up the development environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    return True

def check_nodejs():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} detected")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js not found")
    print("Please install Node.js from https://nodejs.org/")
    return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    if not run_command("npm install", "Installing frontend dependencies", cwd=frontend_dir):
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "uploads", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def main():
    """Main setup function"""
    print("🎯 MetaData Editor Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Check Node.js
    if not check_nodejs():
        print("\n❌ Node.js is required but not found")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("\n❌ Failed to install frontend dependencies")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("  python start.py")
    print("\nOr run backend and frontend separately:")
    print("  python app.py")
    print("  cd frontend && npm start")
    print("\nThe application will be available at:")
    print("  Frontend: http://localhost:3000")
    print("  Backend API: http://localhost:5000")

if __name__ == "__main__":
    main() 