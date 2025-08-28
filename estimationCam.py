import cv2
import numpy as np
import matplotlib.pyplot as plt

step_size_mm = 0.1  # mm per step (adjust if you're using microns)
num_avg_rows = 5    # Rows to average around image center
blur_sigma = 2 
camera_index = 0
#delta_x = 0.03333 #30 microns
cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080) 

if not cap.isOpened():
    print("Could not open camera.")
    exit()

#let camera settle
for _ in range(8):
    ret, _ = cap.read()
    cv2.waitKey(40)

step_count = 0

try:
    while True:
        input(f"Step {step_count+1}: Press Enter to capture...")

        for i in range(5): #fixes cam delay
            ret, frame = cap.read()
            if not ret:
                print("failed to read frame.")
            #perform zoom
            """h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            zoom_fact = 10 #how much we zoom
            half_w, half_h = w // (2 * zoom_fact), h // (2 * zoom_fact)

            cropped = frame[center_y - half_h:center_y + half_h,
                            center_x - half_w:center_x + half_w]

            zoomed_frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)"""

        #grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        #Take horizontal slice
        center_y = h // 2
        strip = gray[center_y - num_avg_rows//2:center_y + num_avg_rows//2 + 1, :]
        profile = np.mean(strip, axis=0)

        #calculating estimated pixel 
        #This code so far does not automatically determine a range of pixels around the tag's position. I've just hard coded what this range should be
        #the sub_profile should cover every pixel making up the tag, low covers the left side of the tag, high covers right side of the tag
        #x_fit and mid_profile covers the split in the tag
        distance = np.arange(len(profile))
        sub_profile = profile[650:705]
        low_profile = profile[650:665]
        mid_profile = profile[665: 690]
        x_fit = distance[665:690]
        high_profile = profile[690:705]
        midpoint = (np.mean(high_profile) + np.mean(low_profile)) / 2
        print("midpoint Intensity: " + str(midpoint))

        for i in range(len(sub_profile) - 1):
            if sub_profile[i] <= midpoint:
                nPixel = i + 650
            else:
                print('breakpoint: ' + str(i) + ', ' + str(sub_profile[i]))
                break
        N = nPixel
        gray_slope = np.polyfit(x_fit, mid_profile, 1)
        slope, intercept = gray_slope
        x_hat = (midpoint - intercept) / slope  # scalar value

        print(f"Estimated edge model: intensity = {slope:.4f}·x + {intercept:.2f}")
        print(f"Estimated x̂ (subpixel edge location): {x_hat:.2f} pixels")

        step_count += 1

        #display intensity profile
        plt.figure(figsize=(6, 4))
        plt.plot(distance, profile, marker='o')
        plt.xlabel("Pixels")
        plt.ylabel("Intensity")
        plt.title("Intensity Profile of Stream")
        plt.grid(True)
        y_fit = np.polyval(gray_slope, x_fit)
        plt.plot(x_fit, y_fit, 'r--', linewidth=2, label="Best-fit line (transition)")

        plt.legend()
        plt.tight_layout()
        plt.show()

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
