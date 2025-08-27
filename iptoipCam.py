import socket
import cv2
import numpy as np
import cv2.aruco as aruco

# Configuration
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 12345
PACKET_SIZE = 1400  # Should match the ESP32 packet size
HEADER_SIZE = 4     # Header size to read sequence number and last packet flag

marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
param_markers =  cv2.aruco.DetectorParameters()
detection = cv2.aruco.ArucoDetector(marker_dict, param_markers)

# Create a socket to listen for incoming UDP packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Buffer to store image bytes
image_data = bytearray()
expected_seq_no = 0

def receive_frame():
    global image_data, expected_seq_no
    while True:
        #print('sending packet...')
        packet, addr = sock.recvfrom(PACKET_SIZE + HEADER_SIZE)
        #print("packet recieved")
        
        # Read header
        seq_no = (packet[0] << 8) | packet[1]
        is_last_packet = packet[2]
        
        # Check if packet is in sequence
        if seq_no == expected_seq_no:
            # Append data after the header
            image_data.extend(packet[HEADER_SIZE:])
            expected_seq_no += 1

            # Check if this is the last packet
            if is_last_packet == 1:
                # Convert byte array to numpy array for decoding
                img_array = np.frombuffer(image_data, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is not None:
                    corners, ids, _ = detection.detectMarkers(frame)
                    if ids is not None:
                        aruco.drawDetectedMarkers(frame, corners, ids)
                        for i, corner in enumerate(corners):
                            # Get the center of the marker
                            center_x = int(corner[0][:, 0].mean())
                            center_y = int(corner[0][:, 1].mean())
                            print(f"Marker ID: {ids[i][0]}, Position: (x: {center_x}, y: {center_y})")

                    cv2.imshow("ESP32-CAM Stream", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                
                # Reset for next frame
                image_data = bytearray()  # Reassign instead of clear
                expected_seq_no = 0

        else:
            # Out-of-order packet or missing packet, reset and wait for new frame
            image_data = bytearray()  # Reassign instead of clear
            expected_seq_no = 0

    sock.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print('starting main...')
    receive_frame()