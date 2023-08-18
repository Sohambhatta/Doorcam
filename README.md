# Doorcam
This project recognizes a person standing in front of a door. While this doesn't use facial recognition, this project is useful for different reasons. Doors are used for safety and privacy. Sometimes we dont want pets to enter into random rooms, and mess around with objects. Sometimes, the air shifting in the house causes doors to slam shut and scares pets. This project is a start for a bigger project. As the camera recognizes a person, it will trigger a mechanism to open the lock, and let the person in. After a few seconds, a second camera checks for people in the door frame. If there is no one, it triggers a motorized mechanism that pulls the door back in with a thread. This project's goal was to create the first camera, that opens the door. That way, people can close the door on their own. While the lock mechanism is still not here, the coding part was my focus. 
## The Algorithm
Using the Jetson Inference github: https://github.com/dusty-nv/jetson-inference,  
I was able to find code that runs the camera conituously and detects the objects in the frame. Starting with that, I figured out what class detects a person, and then went on to the next steps. Here is my code:
```python
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = videoSource("/dev/video0")      # '/dev/video0' for V4L2

for i in range(30):
    img = camera.Capture()

    if img is None: # capture timeout
        continue
    if not camera.IsStreaming():
        break
    detections = net.Detect(img)
    for detection in detections:
        print(detection.ClassID)
        print(net.GetClassDesc(detection.ClassID))
```



