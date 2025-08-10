#!/usr/bin/env python3
"""
🐾 Enhanced Doorcam Pet Detection System
=======================================

Advanced door camera system with:
- Pet detection based on actual dimensions
- Pose-aware distance calculation
- Dual motor control for door operation
- Smart door logic (open for persons, close for pets)
"""

import cv2
import json
from pathlib import Path
from jetson_inference import detectNet
from jetson_utils import videoSource
from pet_trainer import PetDetector
from config import PetConfig
from pet_distance_calculator import PetDistanceCalculator
from motor_controller import MotorController, DoorState

class EnhancedDoorCam:
    def __init__(self):
        # Initialize Jetson inference
        self.net = detectNet("ssd-mobilenet-v2", threshold=0.5)
        self.camera = videoSource("/dev/video0")
        
        # Pet detection system
        self.pet_detector = PetDetector()
        self.config = PetConfig()
        
        # Distance calculator with pet dimensions
        self.distance_calculator = PetDistanceCalculator()
        
        # Motor controller for door operation
        self.motor_controller = MotorController(simulation_mode=True)  # Change to False for real hardware
        self.motor_controller.set_state_callback(self.on_door_state_change)
        
        # Door state tracking
        self.door_locked = True
        self.person_detected = False
        self.pets_too_close = False
        self.last_action_time = 0
        
        # COCO class IDs for common pets
        self.PET_CLASSES = {
            16: "bird",
            17: "cat", 
            18: "dog"
        }
        
        # Load dynamic thresholds based on trained pets
        self.load_pet_based_thresholds()
    
    def load_pet_based_thresholds(self):
        """Load pixel thresholds based on actual pet dimensions"""
        try:
            profile_file = Path("pet_training_data/pet_profiles.json")
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    pet_profiles = json.load(f)
                
                # Calculate thresholds based on actual pet dimensions
                self.DISTANCE_THRESHOLDS = self.distance_calculator.get_recommended_thresholds(pet_profiles)
                print(f"✅ Loaded dimension-based thresholds for {len(pet_profiles)} trained pets")
                
                # Show pet information
                for pet_name, profile in pet_profiles.items():
                    height = profile.get('height_inches', 'unknown')
                    length = profile.get('length_inches', 'unknown')
                    pet_type = profile.get('pet_type', 'unknown')
                    print(f"🐾 {pet_name}: {height}\"H x {length}\"L ({pet_type})")
                
            else:
                # Use default thresholds for a medium dog
                self.DISTANCE_THRESHOLDS = self.distance_calculator.calculate_thresholds_for_pet(24, 30, 'dog')
                print("📏 Using default thresholds (24\"H x 30\"L dog)")
        
        except Exception as e:
            print(f"⚠️  Error loading pet thresholds: {e}")
            # Fallback to basic thresholds
            self.DISTANCE_THRESHOLDS = {
                'front_facing': {'close': 250000, 'medium': 150000, 'far': 50000},
                'side_profile': {'close': 350000, 'medium': 200000, 'far': 80000},  # Side profiles appear larger
                'back_facing': {'close': 200000, 'medium': 120000, 'far': 45000},
                'upside_down_front': {'close': 220000, 'medium': 130000, 'far': 48000},
                'upside_down_side': {'close': 280000, 'medium': 160000, 'far': 60000},
                'standing': {'close': 270000, 'medium': 160000, 'far': 55000}
            }
    
    def on_door_state_change(self, new_state: DoorState):
        """Handle door state changes from motor controller"""
        if new_state == DoorState.OPEN:
            self.door_locked = False
        elif new_state == DoorState.CLOSED:
            self.door_locked = True
        
        print(f"🚪 Door is now {new_state.value.upper()}")
    
    def classify_pet_pose(self, detection, img):
        """Classify the pose/angle of detected pet using improved heuristics"""
        # Extract bounding box
        bbox = (detection.Left, detection.Top, detection.Right, detection.Bottom)
        
        # Calculate dimensions
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        aspect_ratio = width / height
        
        # Position on screen
        center_y = (bbox[1] + bbox[3]) / 2
        img_height = img.height if hasattr(img, 'height') else 1080
        
        # Improved pose classification based on aspect ratio and position
        if aspect_ratio > 1.8:
            return 'side_profile'  # Very wide = side view
        elif aspect_ratio < 0.6:
            return 'upside_down_front'  # Very tall = upside down front
        elif center_y > img_height * 0.7:
            # Bottom of image - likely upside down
            return 'upside_down_side' if aspect_ratio > 1.2 else 'upside_down_front'
        elif aspect_ratio > 1.4:
            return 'back_facing'  # Wide but not too wide
        elif 0.8 <= aspect_ratio <= 1.3:
            return 'standing'  # Square-ish = standing/sitting
        else:
            return 'front_facing'  # Default
    
    def should_lock_door(self, detection, pose, class_name):
        """Determine if door should be locked based on pet detection"""
        area = detection.Area
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        if area > thresholds['close']:
            print(f"🔒 PET TOO CLOSE: {class_name} detected at {area} pixels ({pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {class_name} detected at medium distance - {area} pixels ({pose})")
            return False
        else:
            print(f"✅ SAFE: {class_name} detected far away - {area} pixels ({pose})")
            return False
    
    def should_open_door(self):
        """
        Smart door opening logic
        Opens ONLY when person detected AND no pets too close
        """
        if not self.person_detected:
            return False
        
        if self.pets_too_close:
            print("🚫 Person detected BUT pets too close - door stays locked for safety!")
            return False
        
        if not self.door_locked:
            return False  # Already open
        
        return True
    
    def should_close_door(self):
        """Door closes immediately when pets get too close"""
        return self.pets_too_close and not self.door_locked
    
    def detect_custom_pets(self, img):
        """Detect custom trained pets"""
        custom_detections = self.pet_detector.detect_pets(img)
        return custom_detections
    
    def process_door_action(self):
        """Process door opening/closing based on current detections"""
        import time
        current_time = time.time()
        
        # Avoid rapid door movements (wait at least 2 seconds between actions)
        if current_time - self.last_action_time < 2.0:
            return
        
        # Check if door should open
        if self.should_open_door():
            print("👤 OPENING DOOR: Person detected, no pets too close")
            if self.motor_controller.open_door():
                self.last_action_time = current_time
        
        # Check if door should close (higher priority for safety)
        elif self.should_close_door():
            print("🐾 CLOSING DOOR: Pet(s) detected too close!")
            if self.motor_controller.close_door():
                self.last_action_time = current_time
    
    def run(self):
        """Main detection loop with smart door control"""
        print("🎥 Starting Enhanced Door Camera System with Smart Pet Detection...")
        print("🤖 Motor Control: ENABLED")
        print("🐕 Pet-based Distance Calculation: ACTIVE")
        print("🚪 Smart Door Logic: Person=OPEN, Pet-too-close=CLOSE")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while True:
                img = self.camera.Capture()
                
                if img is None:
                    continue
                if not self.camera.IsStreaming():
                    break
                
                # Reset detection flags
                self.person_detected = False
                self.pets_too_close = False
                
                # Standard Jetson inference detection
                detections = self.net.Detect(img)
                
                # Check for custom trained pets
                custom_pets = self.detect_custom_pets(img)
                
                # Process standard detections
                for detection in detections:
                    class_id = detection.ClassID
                    class_name = self.net.GetClassDesc(class_id)
                    
                    # Person detection
                    if class_id == 1:  # Person
                        if detection.Area > 300000:  # Large enough to be a real person
                            self.person_detected = True
                            print(f"👤 Person detected - Area: {detection.Area}")
                    
                    # Pet detection
                    elif class_id in self.PET_CLASSES:
                        pet_type = self.PET_CLASSES[class_id]
                        pose = self.classify_pet_pose(detection, img)
                        
                        print(f"🐾 {pet_type.title()} detected - Area: {detection.Area}, Pose: {pose}")
                        
                        if self.should_lock_door(detection, pose, pet_type):
                            self.pets_too_close = True
                
                # Process custom pet detections
                for custom_detection in custom_pets:
                    pet_name = custom_detection['name']
                    confidence = custom_detection['confidence']
                    area = custom_detection['area']
                    pose = custom_detection['pose']
                    
                    print(f"🏠 Custom pet '{pet_name}' detected - Confidence: {confidence:.2f}, Area: {area}, Pose: {pose}")
                    
                    # Use same threshold logic for custom pets
                    if self.should_lock_door_custom(area, pose, pet_name):
                        self.pets_too_close = True
                
                # Make door decisions based on detections
                self.process_door_action()
                
                # Small delay to prevent excessive processing
                cv2.waitKey(1)
        
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Enhanced Door Camera...")
        finally:
            # Cleanup
            self.motor_controller.cleanup()
            print("✅ System shutdown complete")
    
    def should_lock_door_custom(self, area, pose, pet_name):
        """Check if door should lock for custom detected pets"""
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        if area > thresholds['close']:
            print(f"🔒 CUSTOM PET TOO CLOSE: {pet_name} at {area} pixels ({pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {pet_name} at medium distance - {area} pixels ({pose})")
            return False
        else:
            print(f"✅ SAFE: {pet_name} far away - {area} pixels ({pose})")
            return False

if __name__ == "__main__":
    door_cam = EnhancedDoorCam()
    door_cam.run()

    def classify_pet_pose(self, detection, img):
        """Classify the pose/angle of detected pet using basic heuristics"""
        # Extract bounding box
        bbox = (detection.Left, detection.Top, detection.Right, detection.Bottom)
        
        # Calculate aspect ratio
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        aspect_ratio = width / height
        
        # Simple heuristics for pose classification
        # This is a basic implementation - you could use more sophisticated ML models
        if aspect_ratio > 1.5:
            return 'side_profile'
        elif aspect_ratio < 0.8:
            return 'upside_down_front'
        elif bbox[1] > img.height * 0.6:  # Bottom of image
            return 'upside_down_side'
        elif aspect_ratio > 1.2:
            return 'back_facing'
        else:
            return 'front_facing'

    def should_lock_door(self, detection, pose, class_name):
        """Determine if door should be locked based on pet detection"""
        area = detection.Area
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        # Check if pet is too close
        if area > thresholds['close']:
            print(f"🔒 LOCKING DOOR: {class_name} detected too close ({area} pixels, pose: {pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {class_name} detected at medium distance ({area} pixels, pose: {pose})")
            return False
        else:
            print(f"✅ SAFE: {class_name} detected far away ({area} pixels, pose: {pose})")
            return False

    def detect_custom_pets(self, img):
        """Detect custom trained pets"""
        custom_detections = self.pet_detector.detect_pets(img)
        return custom_detections

    def run(self):
        """Main detection loop"""
        print("🎥 Starting Enhanced Door Camera System...")
        print("🐕 Pet detection enabled with pose classification")
        print("🔒 Door will lock when pets get too close")
        
        while True:
            img = self.camera.Capture()
            
            if img is None:
                continue
            if not self.camera.IsStreaming():
                break
                
            # Standard Jetson inference detection
            detections = self.net.Detect(img)
            
            # Check for custom trained pets
            custom_pets = self.detect_custom_pets(img)
            
            door_should_lock = False
            
            # Process standard detections
            for detection in detections:
                class_id = detection.ClassID
                class_name = self.net.GetClassDesc(class_id)
                
                # Check if it's a pet
                if class_id in self.PET_CLASSES:
                    pet_type = self.PET_CLASSES[class_id]
                    pose = self.classify_pet_pose(detection, img)
                    
                    print(f"🐾 Detected {pet_type} ({class_name}) - Area: {detection.Area}, Pose: {pose}")
                    
                    if self.should_lock_door(detection, pose, pet_type):
                        door_should_lock = True
                
                # Original person detection logic
                elif class_id == 1 and detection.Area > 300000:
                    print("👤 Person detected - unlocking door")
                    self.door_locked = False
            
            # Process custom pet detections
            for custom_detection in custom_pets:
                pet_name = custom_detection['name']
                confidence = custom_detection['confidence']
                area = custom_detection['area']
                pose = custom_detection['pose']
                
                print(f"🏠 Custom pet detected: {pet_name} (confidence: {confidence:.2f}, area: {area}, pose: {pose})")
                
                if self.should_lock_door_custom(area, pose, pet_name):
                    door_should_lock = True
            
            # Update door state
            if door_should_lock and not self.door_locked:
                print("🔒 LOCKING DOOR due to pet proximity")
                self.door_locked = True
                # TODO: Add actual door locking mechanism here
            
            # Small delay to prevent excessive processing
            cv2.waitKey(1)

    def should_lock_door_custom(self, area, pose, pet_name):
        """Check if door should lock for custom detected pets"""
        thresholds = self.DISTANCE_THRESHOLDS.get(pose, self.DISTANCE_THRESHOLDS['front_facing'])
        
        if area > thresholds['close']:
            print(f"🔒 LOCKING DOOR: {pet_name} detected too close ({area} pixels, pose: {pose})")
            return True
        elif area > thresholds['medium']:
            print(f"⚠️ WARNING: {pet_name} detected at medium distance ({area} pixels, pose: {pose})")
            return False
        else:
            print(f"✅ SAFE: {pet_name} detected far away ({area} pixels, pose: {pose})")
            return False

if __name__ == "__main__":
    door_cam = EnhancedDoorCam()
    try:
        door_cam.run()
    except KeyboardInterrupt:
        print("\n🛑 Door camera system stopped")
