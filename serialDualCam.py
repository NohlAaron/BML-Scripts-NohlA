#This code is an upgraded version of cv2Cam3. Instead of reading a singular serial port printed by 240723-155823-esp32cam,
#It will read 2 different serial monitors, left and right, at the same time. both cams use seperate esp32 cam code that is
#identicial to 240723-155823-esp32cam, with the difference being what they upload to.

import serial
import cv2
import numpy as np
import time
import base64
import cv2.aruco as aruco

#function to detect tag in frame
marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
param_markers =  cv2.aruco.DetectorParameters()
detection = cv2.aruco.ArucoDetector(marker_dict, param_markers)

left_port = 'COM7'  # Adjust as needed
right_port = 'COM8'  # Adjust as needed
baud_rate =  500000 #750000 #921600 #1000000

left = serial.Serial(left_port, baud_rate, timeout=1)
print(f"Connected to {left_port} at {baud_rate} baud.")
right = serial.Serial(right_port, baud_rate, timeout=1)
print(f"Connected to {right_port} at {baud_rate} baud.")
left.setDTR(False)
left.setRTS(False)
right.setDTR(False)
right.setRTS(False)

def read_serial_data(ser):
    data = b''
    start_marker = b'START'
    end_marker = b'END'
    receiving = False

    while True:
        line = ser.readline()
        if start_marker in line:
            data = b''
            receiving = True
            continue
        if end_marker in line:
            break
        if receiving:
            data += line.strip()
    return data

def validate_base64_string(data):
    try:
        if len(data) % 4 != 0:
            data += b'=' * (4 - len(data) % 4)
        base64.b64decode(data)
        return True
    except Exception as e:
        #print(f"Invalid base64 data: {e}")
        return False

def decode_base64_image(data):
    if not validate_base64_string(data):
        return None
    try:
        decoded_data = base64.b64decode(data)
        np_data = np.frombuffer(decoded_data, np.uint8)
        image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        #print(f"Error decoding image: {e}")
        return None

def process_frame(data, window):
    image = decode_base64_image(data)
    if image is not None:
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detection.detectMarkers(gray_frame)
        if ids is not None:
            aruco.drawDetectedMarkers(image, corners, ids)
        cv2.imshow(window, image)
    else:
        print(f"Failed to decode image for {window}")

def main():
    left.flushInput()
    right.flushInput()
    print(f"inputs flushed, please wait 10 seconds...")
    time.sleep(10)
    while True:
        #print("Reading from both serial ports...")
        base64_dataL = read_serial_data(left)
        base64_dataR = read_serial_data(right)

        if base64_dataL:
            process_frame(base64_dataL, 'Left Image')
        
        if base64_dataR:
            process_frame(base64_dataR, 'Right Image')
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    left.close()
    right.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print('starting main...')
    main()
