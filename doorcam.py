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