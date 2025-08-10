#!/usr/bin/env python3
"""
🔧 Doorcam Installation Script
=============================

This script helps install dependencies for the Doorcam Pet Detection System.
It will check for existing installations and install missing packages.

Usage:
    python install.py [--jetson]

Options:
    --jetson    Install Jetson-specific packages (for NVIDIA Jetson devices)
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    major, minor = sys.version_info[:2]
    
    if major < 3 or (major == 3 and minor < 6):
        print(f"❌ Python {major}.{minor} is not supported. Please use Python 3.6 or higher.")
        return False
    
    print(f"✅ Python {major}.{minor} is compatible")
    return True

def install_basic_dependencies():
    """Install basic Python dependencies"""
    print("\n📦 Installing basic dependencies...")
    
    packages = [
        "opencv-python",
        "pillow", 
        "numpy",
        "customtkinter",
        "pathlib2",
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def install_jetson_dependencies():
    """Install Jetson-specific dependencies"""
    print("\n🤖 Installing Jetson dependencies...")
    print("ℹ️  Note: Jetson inference libraries need to be built from source")
    print("📖 See: https://github.com/dusty-nv/jetson-inference")
    
    # These are optional for Jetson development
    optional_packages = [
        "torch",  # PyTorch for Jetson
        "torchvision",
        "matplotlib",
        "scikit-learn"
    ]
    
    print("📦 Installing optional ML packages...")
    for package in optional_packages:
        run_command(f"pip install {package}", f"Installing {package} (optional)")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating project directories...")
    
    directories = [
        "pet_training_data",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_camera_access():
    """Test camera access"""
    print("\n📹 Testing camera access...")
    
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        
        if camera.isOpened():
            ret, frame = camera.read()
            if ret:
                print("✅ Camera is accessible and working")
                camera.release()
                return True
            else:
                print("⚠️  Camera opens but cannot capture frames")
                camera.release()
                return False
        else:
            print("❌ Cannot access camera device 0")
            print("💡 Make sure your camera is connected and not in use")
            return False
            
    except ImportError:
        print("⚠️  OpenCV not installed yet, cannot test camera")
        return True
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def verify_installation():
    """Verify that all components can be imported"""
    print("\n🔍 Verifying installation...")
    
    test_imports = [
        ("cv2", "OpenCV"),
        ("customtkinter", "CustomTkinter"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
    ]
    
    all_good = True
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} can be imported")
        except ImportError:
            print(f"❌ {name} cannot be imported")
            all_good = False
    
    return all_good

def show_next_steps():
    """Show what to do next"""
    print("\n🎉 Installation completed!")
    print("\n🚀 Next steps:")
    print("1. Train your pet:")
    print("   python launcher.py train")
    print("\n2. Run the door camera:")
    print("   python launcher.py run")
    print("\n3. Configure settings:")
    print("   python launcher.py config")
    print("\n📖 For more help, see README.md")

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install Doorcam dependencies")
    parser.add_argument("--jetson", action="store_true", help="Install Jetson-specific packages")
    args = parser.parse_args()
    
    print("🐾 Doorcam Pet Detection System - Installation Script")
    print("=" * 55)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install basic dependencies
    if not install_basic_dependencies():
        print("\n❌ Failed to install basic dependencies")
        sys.exit(1)
    
    # Install Jetson dependencies if requested
    if args.jetson:
        install_jetson_dependencies()
    
    # Create directories
    create_directories()
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages may not have installed correctly")
        print("💡 Try running: pip install -r requirements.txt")
    
    # Test camera
    check_camera_access()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
