//Code for the the 'Left' Camera. Prints to COM port 7. 

#include <Arduino.h>
#include "esp_camera.h"
#include "mbedtls/base64.h"

// Select camera model
#define CAMERA_MODEL_AI_THINKER // Has PSRAM

//replace with the filepath to camera_pins.h.ino in the src
#include "camera_pins.h.ino"

void setup() {
  Serial.begin(500000); //1000000
  delay(1000);
  
  // Enable the camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Init with high specs to pre-allocate larger buffers
  if (psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 10;
    config.fb_count = 3;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 15;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void loop() {
  // Capture a frame
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  // Allocate buffer for base64 encoding
  size_t encoded_length = 4 * ((fb->len + 2) / 3);
  uint8_t * encoded_buf = (uint8_t *)malloc(encoded_length + 1); // +1 for null terminator

  if (encoded_buf) {
    size_t output_len;
    int ret = mbedtls_base64_encode(encoded_buf, encoded_length + 1, &output_len, fb->buf, fb->len);

    if (ret == 0) {
      Serial.println("START");
      // Send the base64 encoded frame buffer
      Serial.write(encoded_buf, output_len);
      Serial.println(); // Add newline for better readability on the receiver side

      Serial.println("END");
    } else {
      Serial.printf("Base64 encoding failed with error %d\n", ret);
    }

    free(encoded_buf);
  } else {
    Serial.println("Failed to allocate memory for base64 encoding");
  }

  // Return the frame buffer back to the driver for reuse
  esp_camera_fb_return(fb);

}


