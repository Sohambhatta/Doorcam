"""
🐾 Original Doorcam System (Legacy)
===================================

This is your original implementation. 
For the enhanced version with pet detection, use:

    python launcher.py run

Or run the enhanced system directly:

    python enhanced_doorcam.py

The new system includes:
- Pet detection with pose classification
- Custom pet training via GUI
- Distance-based door locking
- Modern configuration management
"""

from jetson_inference import detectNet
from jetson_utils import videoSource

def main():
    """Original doorcam implementation"""
    print("🚪 Starting Original Doorcam System...")
    print("💡 For enhanced pet detection, run: python launcher.py run")
    print("🐾 To train custom pets, run: python launcher.py train")
    
    net = detectNet("ssd-mobilenet-v2", threshold=0.5)
    camera = videoSource("/dev/video0")      # '/dev/video0' for V4L2
    door_locked = True
    
    while True:
        img = camera.Capture()
        
        if img is None: # capture timeout
            continue
        if not camera.IsStreaming():
            break
        detections = net.Detect(img)
        
        for detection in detections:
            print(f"Class ID: {detection.ClassID}")
            print(f"Class Name: {net.GetClassDesc(detection.ClassID)}")
            print(f"Area: {detection.Area}")
            
            if detection.ClassID == 1 and detection.Area > 300000 and door_locked:
                print("👤 Person detected - unlocking door")
                door_locked = False
                # This is where the unlocking actually happens.
            
            # Simple pet detection (basic version)
            elif detection.ClassID in [16, 17, 18]:  # bird, cat, dog
                pet_type = {16: "bird", 17: "cat", 18: "dog"}[detection.ClassID]
                if detection.Area > 200000:  # Pet is close
                    print(f"🐾 {pet_type} detected close to door - locking for safety")
                    door_locked = True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Doorcam system stopped")

    