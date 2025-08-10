#!/usr/bin/env python3
"""
🎮 Doorcam Demo Script
=====================

A simple demonstration of the pet detection system without requiring
actual Jetson hardware. This script simulates the detection logic
using mock data.

Usage:
    python demo.py
"""

import time
import random
from pathlib import Path

class MockDetection:
    """Mock detection object for demonstration"""
    def __init__(self, class_id, area, left=100, top=100, right=300, bottom=200):
        self.ClassID = class_id
        self.Area = area
        self.Left = left
        self.Top = top
        self.Right = right
        self.Bottom = bottom

class MockNet:
    """Mock detection network for demonstration"""
    def __init__(self):
        self.classes = {
            1: "person",
            16: "bird", 
            17: "cat",
            18: "dog"
        }
    
    def GetClassDesc(self, class_id):
        return self.classes.get(class_id, "unknown")

class DemoSystem:
    """Demo version of the door camera system"""
    
    def __init__(self):
        self.net = MockNet()
        self.door_locked = True
        
        # Pet detection thresholds
        self.DISTANCE_THRESHOLDS = {
            'front_facing': {'close': 250000, 'medium': 150000, 'far': 50000},
            'side_profile': {'close': 180000, 'medium': 100000, 'far': 40000},
            'back_facing': {'close': 200000, 'medium': 120000, 'far': 45000},
        }
        
        # Demo scenarios
        self.scenarios = [
            {"type": "person", "class_id": 1, "area": 350000, "action": "unlock"},
            {"type": "cat_close", "class_id": 17, "area": 280000, "action": "lock"},
            {"type": "dog_medium", "class_id": 18, "area": 120000, "action": "warning"},
            {"type": "cat_far", "class_id": 17, "area": 30000, "action": "safe"},
            {"type": "bird", "class_id": 16, "area": 45000, "action": "safe"},
            {"type": "dog_side", "class_id": 18, "area": 190000, "pose": "side_profile", "action": "lock"},
        ]
    
    def classify_pet_pose(self, detection):
        """Mock pose classification"""
        # Randomly assign poses for demo
        poses = ['front_facing', 'side_profile', 'back_facing']
        return random.choice(poses)
    
    def should_lock_door(self, detection, pose, class_name):
        """Determine if door should be locked"""
        area = detection.Area
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        if area > thresholds['close']:
            print(f"🔒 LOCKING DOOR: {class_name} detected too close ({area} pixels, pose: {pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {class_name} detected at medium distance ({area} pixels, pose: {pose})")
            return False
        else:
            print(f"✅ SAFE: {class_name} detected far away ({area} pixels, pose: {pose})")
            return False
    
    def process_detection(self, scenario):
        """Process a single detection scenario"""
        print("\n📹 Camera frame captured...")
        
        detection = MockDetection(scenario["class_id"], scenario["area"])
        class_name = self.net.GetClassDesc(detection.ClassID)
        
        print(f"🎯 Detected: {class_name} (Class ID: {detection.ClassID}, Area: {detection.Area})")
        
        # Handle person detection
        if detection.ClassID == 1:
            if detection.Area > 300000 and self.door_locked:
                print("👤 Person detected - unlocking door")
                self.door_locked = False
                return
        
        # Handle pet detection
        if detection.ClassID in [16, 17, 18]:  # bird, cat, dog
            pet_type = {16: "bird", 17: "cat", 18: "dog"}[detection.ClassID]
            pose = scenario.get('pose', self.classify_pet_pose(detection))
            
            print(f"🐾 Pet detected: {pet_type}, pose: {pose}")
            
            if self.should_lock_door(detection, pose, pet_type) and not self.door_locked:
                print("🔒 LOCKING DOOR due to pet proximity")
                self.door_locked = True
    
    def run_demo(self):
        """Run the demonstration"""
        print("🐾 DOORCAM PET DETECTION SYSTEM - DEMO MODE")
        print("=" * 50)
        print("🎮 This demo simulates pet detection without requiring actual hardware")
        print("📹 Each scenario represents a camera frame with different detections\n")
        
        input("Press Enter to start the demo...")
        
        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\n{'='*20} SCENARIO {i}/{len(self.scenarios)} {'='*20}")
            print(f"🎯 Scenario: {scenario['type']}")
            print(f"🚪 Door status: {'🔒 LOCKED' if self.door_locked else '🔓 UNLOCKED'}")
            
            self.process_detection(scenario)
            
            # Show final door state
            final_status = "🔒 LOCKED" if self.door_locked else "🔓 UNLOCKED"
            print(f"🚪 Final door status: {final_status}")
            
            if i < len(self.scenarios):
                time.sleep(2)  # Pause between scenarios
                print("\n" + "."*50)
        
        print(f"\n{'='*50}")
        print("🎉 Demo completed!")
        print("\n💡 To run the actual system:")
        print("   1. Train your pet: python launcher.py train")
        print("   2. Run detection: python launcher.py run")
        print("   3. Configure settings: python launcher.py config")

def show_system_info():
    """Show information about the system files"""
    print("\n📋 SYSTEM COMPONENTS:")
    print("=" * 30)
    
    files = [
        ("launcher.py", "Main launcher - start here"),
        ("enhanced_doorcam.py", "Advanced detection system"),
        ("pet_training_gui.py", "Modern GUI for pet training"),
        ("pet_trainer.py", "Custom pet detection logic"),
        ("config.py", "Configuration management"),
        ("config_manager.py", "Settings GUI"),
        ("install.py", "Dependency installer"),
        ("demo.py", "This demonstration script"),
    ]
    
    for filename, description in files:
        file_path = Path(filename)
        status = "✅" if file_path.exists() else "❌"
        print(f"{status} {filename:<25} - {description}")
    
    print("\n📊 TRAINING DATA:")
    data_dir = Path("pet_training_data")
    if data_dir.exists():
        profile_file = data_dir / "pet_profiles.json"
        if profile_file.exists():
            try:
                import json
                with open(profile_file, 'r') as f:
                    profiles = json.load(f)
                print(f"🐾 Trained pets: {len(profiles)}")
                for name in profiles.keys():
                    print(f"   - {name}")
            except Exception:
                print("🐾 Training data found but couldn't read profiles")
        else:
            print("🐾 No trained pets yet")
    else:
        print("🐾 No training data directory")

def main():
    """Main demo function"""
    print("🎮 Welcome to the Doorcam Pet Detection Demo!")
    print("\nChoose an option:")
    print("1. Run detection demo")
    print("2. Show system information")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo = DemoSystem()
            demo.run_demo()
            break
        elif choice == "2":
            show_system_info()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
