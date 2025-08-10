#!/usr/bin/env python3
"""
🐾 Doorcam Pet Detection System Launcher
===========================================

This launcher provides easy access to all components of the Doorcam system:
1. Pet Training GUI - Collect training data for your pets
2. Enhanced Door Camera - Run the main detection system
3. Configuration Manager - Adjust detection thresholds

Usage:
    python launcher.py [command]

Commands:
    train    - Launch the Pet Training GUI
    run      - Start the Enhanced Door Camera system  
    config   - Open configuration settings
    help     - Show this help message

Examples:
    python launcher.py train     # Start pet training
    python launcher.py run       # Start door camera
    python launcher.py config    # Adjust settings
"""

import sys
import subprocess
from pathlib import Path
import argparse

def print_banner():
    """Print the application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🐾 DOORCAM PET DETECTION SYSTEM 🏠                    ║
║                                                              ║
║     Advanced AI-powered door security with pet detection     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        ('cv2', 'opencv-python'),
        ('customtkinter', 'customtkinter'),
        ('PIL', 'pillow'),
        ('numpy', 'numpy'),
    ]
    
    missing = []
    for module, package in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:")
        for package in missing:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies are installed")
    return True

def launch_training_gui():
    """Launch the pet training GUI"""
    print("🚀 Starting Pet Training GUI...")
    try:
        subprocess.run([sys.executable, "pet_training_gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching training GUI: {e}")
        return False
    except FileNotFoundError:
        print("❌ pet_training_gui.py not found!")
        return False
    return True

def launch_door_camera():
    """Launch the enhanced door camera system"""
    print("🚀 Starting Enhanced Door Camera System...")
    print("📹 Make sure your camera is connected!")
    print("🤖 Motor control system initialized")
    print("🔒 Smart door logic: Person=OPEN, Pet-close=CLOSE")
    print("📏 Using dimension-based pet detection thresholds")
    print("👤 Door opens only when person detected AND no pets too close")
    print("🐾 Door closes immediately when pets get too close")
    print("\n⚠️  Press Ctrl+C to stop the system\n")
    
    try:
        subprocess.run([sys.executable, "enhanced_doorcam.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching door camera: {e}")
        return False
    except FileNotFoundError:
        print("❌ enhanced_doorcam.py not found!")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Door camera system stopped by user")
    return True

def launch_config_manager():
    """Launch the configuration manager"""
    print("🚀 Starting Configuration Manager...")
    try:
        subprocess.run([sys.executable, "config_manager.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching config manager: {e}")
        return False
    except FileNotFoundError:
        print("❌ config_manager.py not found!")
        print("💡 You can manually edit pet_config.json instead")
        return False
    return True

def show_system_status():
    """Show current system status"""
    print("📊 SYSTEM STATUS")
    print("=" * 50)
    
    # Check if training data exists
    data_dir = Path("pet_training_data")
    if data_dir.exists():
        profile_file = data_dir / "pet_profiles.json"
        if profile_file.exists():
            try:
                import json
                with open(profile_file, 'r') as f:
                    profiles = json.load(f)
                print(f"🐾 Trained pets: {len(profiles)}")
                for name, profile in profiles.items():
                    img_count = profile.get('total_images', 0)
                    pose_count = len(profile.get('poses', []))
                    print(f"   - {name}: {img_count} images, {pose_count} poses")
            except Exception:
                print("🐾 Trained pets: Unable to read profiles")
        else:
            print("🐾 Trained pets: None")
    else:
        print("🐾 Trained pets: None")
    
    # Check config file
    config_file = Path("pet_config.json")
    if config_file.exists():
        print("⚙️ Configuration: ✅ Custom config found")
    else:
        print("⚙️ Configuration: 📝 Using defaults")
    
    # Check camera access
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            print("📹 Camera: ✅ Available")
            camera.release()
        else:
            print("📹 Camera: ❌ Not accessible")
    except Exception:
        print("📹 Camera: ❓ Unable to check")
    
    print()

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="🐾 Doorcam Pet Detection System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py train     # Start pet training GUI
  python launcher.py run       # Start door camera system
  python launcher.py config    # Open configuration manager
  python launcher.py status    # Show system status
        """
    )
    
    parser.add_argument(
        'command', 
        nargs='?',
        choices=['train', 'run', 'config', 'status', 'help'],
        default='help',
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == 'help':
        parser.print_help()
        print("\n🆘 QUICK START GUIDE:")
        print("1. First time? Run: python launcher.py train")
        print("2. Train your pet with photos from different angles")
        print("3. Save the training data")
        print("4. Run the door camera: python launcher.py run")
        print("\n📞 Need help? Check the README.md file")
        return
    
    if args.command == 'status':
        show_system_status()
        return
    
    # Check dependencies for commands that need them
    if args.command in ['train', 'run', 'config']:
        print("🔍 Checking dependencies...")
        if not check_dependencies():
            sys.exit(1)
        print()
    
    # Execute the requested command
    success = False
    if args.command == 'train':
        success = launch_training_gui()
    elif args.command == 'run':
        success = launch_door_camera()
    elif args.command == 'config':
        success = launch_config_manager()
    
    if success:
        print("✅ Command completed successfully")
    else:
        print("❌ Command failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
