from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

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
        print(detection.ClassID)
        print(net.GetClassDesc(detection.ClassID))
        print(detection.Area)
        if detection.ClassID == 1 and detection.Area > 300000 and door_locked:
            print("unlocking door") # This is where the unlocking and locking actually happens.
            door_locked = False

    var = "hello!"

    