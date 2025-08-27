This is my personal Github repository for all of my work related to my research at Biomimetic Millisystems Laboratory. The files related to Esp32 Tag positioning are the following:
1. WebAddressSourceCode: Arduino IDE Code for uploading a video stream to a local web address
2. cv2Cam2: a Python Script that will display a video stream from a local web address and perform Aruco tag detection
3. IptoIpCam: A PlatformIO Project that will directly send a video stream to your computer's UDP Port
4. IptoIpCam: A python Script that will read its UDP port, display a video stream, and perform Aruco Tag Detection
5. SerialCam1A: A PlatformIO Script that will encode a video stream to the Esp's Serial. For the dual Cam setup, upload this script to 2 different serial Ports corresponding to your esp Cameras
6. cv2Cam3: A Python Script that will read an ESP's serial, decode a video stream, and stitch frames together to display the stream, then perform Aruco Tag Detection
7. SerialDualCam: A python Script that will read multiple Serial ports, decode a video stream from each and display both video streams, and perform Aruco Tag detection on both streams.

The Files related to USB Camera Positional resolution testing are the following:
...
