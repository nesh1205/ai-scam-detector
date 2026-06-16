#!/usr/bin/env python3
"""
AI Scam Detector - Setup Script
Checks Python version, creates virtual environment, and installs dependencies
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ ERROR: Python 3.8+ required!")
        return False
    
    return True

def create_venv():
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    if os.path.exists(".venv"):
        print("✓ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False

def get_pip_executable():
    """Get the correct pip executable for the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(".venv", "Scripts", "pip.exe")
    else:
        return os.path.join(".venv", "bin", "pip")

def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Dependencies")
    
    pip_executable = get_pip_executable()
    
    if not os.path.exists(pip_executable):
        print(f"✗ pip not found at {pip_executable}")
        return False
    
    try:
        # Upgrade pip
        print("Upgrading pip...")
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        print("Installing requirements from requirements.txt...")
        subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
        
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    print_header("Checking Configuration")
    
    if os.path.exists(".env"):
        print("✓ .env file found")
        return True
    elif os.path.exists(".env.example"):
        print("⚠ .env file not found, but .env.example exists")
        print("  Copy .env.example to .env and update with your settings")
        return True
    else:
        print("✗ No .env file found")
        print("  Create .env with your API keys and configuration")
        return False

def verify_requirements():
    """Verify all requirements are installed"""
    print_header("Verifying Installation")
    
    required_packages = [
        'flask',
        'flask_cors',
        'google.generativeai',
        'firebase_admin',
        'dotenv',
        'requests'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def main():
    """Run setup steps"""
    print("\n")
    print("╔" + "═"*48 + "╗")
    print("║" + " AI Scam Detector - Setup Script ".center(48) + "║")
    print("╚" + "═"*48 + "╝")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Virtual Environment Setup", create_venv),
        ("Dependency Installation", install_dependencies),
        ("Configuration Check", check_env_file),
        ("Installation Verification", verify_requirements),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n✗ Setup failed at: {step_name}")
            return False
    
    print_header("Setup Complete!")
    print("""
✓ All checks passed! Your environment is ready.

Next steps:
1. Edit .env file with your API keys if needed
2. Run the application:
   
   Windows (Command Prompt):
   > start.bat
   
   Windows (PowerShell):
   > .\\start.ps1
   
   macOS/Linux:
   > ./run.sh
   
3. Open your browser to http://localhost:5000

Admin Dashboard:   http://localhost:5000/admin
Database Viewer:   http://localhost:5000/database

Admin Credentials:
   Username: thinesh
   Password: thinesh123@

For more help, check README.md
    """)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

