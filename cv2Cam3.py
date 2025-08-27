#This code is used in combination with 240723-155823-esp32cam (or serialCam1A). This reads the esp32 serial monitor to find frame data,
#decode that data, then reconstruct the frame with tag detection and display the image. Works with a singular cam, the
#upgraded script will account for multiple cams printing to multiple serial monitors.

import serial
import cv2
import numpy as np
import time
import base64
import cv2.aruco as aruco
import matplotlib.pyplot as plt


#function to detect tag in frame
marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
param_markers =  cv2.aruco.DetectorParameters()
detection = cv2.aruco.ArucoDetector(marker_dict, param_markers)

serial_port = 'COM5'  # Adjust as needed
baud_rate = 921600 #750000 #921600 #1000000

ser = serial.Serial(serial_port, baud_rate, timeout=1)
ser.setDTR(False)
ser.setRTS(False)
print(f"Connected to {serial_port} at {baud_rate} baud.")

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
        image = cv2.imdecode(np_data, cv2.IMREAD_COLOR) #, cv2.IMREAD_COLOR
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
            for i, corner in enumerate(corners):
                # Get the center of the marker
                center_x = int(corner[0][:, 0].mean())
                center_y = int(corner[0][:, 1].mean())
                print(f"Marker ID: {ids[i][0]}, Position: (x: {center_x}, y: {center_y})")

        cv2.imshow(window, image)
    else:
        print(f"Failed to decode image for {window}")

def main():
    ser.flushInput()
    print(f"input flushed, please wait 7 seconds...")
    time.sleep(7)
    while True:
        base64_data = read_serial_data(ser)

        if base64_data:
            process_frame(base64_data, 'Center Image')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ser.close()
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    print('starting main...')
    main()
