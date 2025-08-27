#Using Aruco Tag Detection with an EspCam uploading to a web address.
import cv2
import cv2.aruco as aruco
import time
import urllib.request
import numpy as np

#function to detect tag in frame
marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
param_markers =  cv2.aruco.DetectorParameters()
detection = cv2.aruco.ArucoDetector(marker_dict, param_markers)

#define usb cam
URL = "Enter Valid IP Address"

fps = 10 #setting up saving videos to computer
width, height = 320, 240
videoFile = cv2.VideoWriter("savedCaptures/videoCapture.mp4", 
                            cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
                            fps = fps, frameSize = (width, height))
print(f"FPS: {fps}, Width: {width}, Height: {height}")
count = 0
total = np.array(0)

while (True): #reading the url each tick and pulling the frame from response. everything else is same as cv2Cam1
    start_time = time.time()
    try:
        with urllib.request.urlopen(URL) as response:
            image_data = response.read()
        frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Failed to fetch frame: {e}")
        continue

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, c = detection.detectMarkers(gray_frame)
    if ids is not None:
         aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.resize(frame, (width, height))
    videoFile.write(frame)
    cv2.imshow("Webcam: ", frame)
    if cv2.waitKey(1) == ord('q'):
        break

    end_time = time.time()
    total = np.append(total, end_time - start_time)
    count += 1
    print(f"Frame processed in {end_time - start_time:.2f} seconds")

videoFile.release()
print('Average time between frames: ' + str(np.sum(total) / count) )
print('fps: ' + str(count / np.sum(total)) )
cv2.destroyAllWindows()
