# Doorcam
This project recognizes a person standing in front of a door. While this doesn't use facial recognition, this project is useful for different reasons. Doors are used for safety and privacy. Sometimes we dont want pets to enter into random rooms, and mess around with objects. Sometimes, the air shifting in the house causes doors to slam shut and scares pets. This project is a start for a bigger project. As the camera recognizes a person, it will trigger a mechanism to open the lock, and let the person in. After a few seconds, a second camera checks for people in the door frame. If there is no one, it triggers a motorized mechanism that pulls the door back in with a thread. This project's goal was to create the first camera, that opens the door. That way, people can close the door on their own. While the lock mechanism is still not here, the coding part was my focus.  Since I don't recieve input, there are no pictures of the camera's progress.
## The Algorithm
Using the Jetson Inference github: https://github.com/dusty-nv/jetson-inference,  
I was able to find code that runs the camera conituously and detects the objects in the frame. Starting with that, I figured out what class detects a person, and then went on to the next steps. Here is my code:
```python
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
```
Now, lets break down code. THe code starts off with importing all the necassary libraries for it to run. We imported detectNet and videoSource, and videoOutput. Then we defined a few variables to help us out in the while loop. the "net" variable helps us define detections, and holds the libraries. The "camera" variable is how we define the input, and the "door_locked" prevents the code from opening the door every frame that it sees a person. 
```python
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = videoSource("/dev/video0")      # '/dev/video0' for V4L2
door_locked = True
```
Now, we have the main loop. The while loop starts off by defining img as the input from the camera per frame. Then we made sure that even is the camera isnt detecting anything, keep running. THen we said that if the camera is not streaming, then stop. Then, we defined detections with the help of "net", and "img".
``` python
while True:
    img = camera.Capture()
    
    if img is None: # capture timeout
        continue
    if not camera.IsStreaming():
        break
    detections = net.Detect(img)

```
Next, we made a for loop inside the mainloop that defines detection in detections, so that we can define individual classes. In order the debug the code, we made the first 3 print statements. They display the classID, and its description, and the Area of the frame that its detected on. Then we made the for loop that is supposed to open and close the door. Since we don't have live motors present, and the extra camera, this camera is capable of unlocking the door, once. This is where I made sure that the area is big enough so that the camera doesn't recognis random movement. Then we made it so that it only open ths door once  using the boolean variable "door_locked".
```python
for detection in detections:
        print(detection.ClassID)
        print(net.GetClassDesc(detection.ClassID))
        print(detection.Area)
        if detection.ClassID == 1 and detection.Area > 300000 and door_locked:
            print("unlocking door") # This is where the unlocking and locking actually happens.
            door_locked = False
```
## Running the program 
1) Start by ssh remote connecting to your nano on vs code.
2) Then have your camera plugged into your nano.
3) Copy the full code above.
4) Paste it into a .py file, and run it. Make sure you are in the right directory.
5) The code is incomplete, allowing you to use it and have it connect to whatever motor you have, and have the freedom to use it for any purpose.
6) Have the camera mounted, and you are good to go!
