#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiUdp.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.ino" //change to the filepath to camera_pins.ino in the src


// Replace with your network credentials
const char* ssid = "Your WIfi Network Name";
const char* password = "Your Password";

// UDP settings
WiFiUDP udp;
const char* udpAddress = "Ip Address of your Computer";  // Replace with the IP address of your computer
const int udpPort = 12345; // Choose any port number
const int packetSize = 1400;  // Max packet size for each UDP transmission
const int headerSize = 4;     // Header size for sequence number and last packet flag


void setup() {
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  // Start UDP
  udp.begin(udpPort);
  Serial.println("UDP started");

  // Initialize camera
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
  config.pin_xclk = XCLK_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Set frame size and quality
  config.frame_size = FRAMESIZE_VGA;  
  config.jpeg_quality = 8;
  config.fb_count = 2;

  // Initialize the camera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }
  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 2);     // -2 to 2
  s->set_contrast(s, 1);       // -2 to 2
  s->set_saturation(s, 1);
  s->set_special_effect(s, 2);

  s->set_sharpness(s, 1); 
  s->set_quality(s, 8);      // JPEG quality (lower value = higher quality)
  s->set_gain_ctrl(s, 1);     // Enable gain control
  s->set_whitebal(s, 1);      // Enable white balance
  s->set_exposure_ctrl(s, 1); // Enable exposure control
  s->set_awb_gain(s, 1);      // Enable auto white balance gain
  s->set_agc_gain(s, 15);     // Set AGC gain (0 to 30 for fine control)
  s->set_aec2(s, 1);          // Enable additional exposure control
  s->set_denoise(s, 1);       // Enable denoise
}

void loop() {
  // Capture frame
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  int totalLen = fb->len;
  int seqNo = 0;

   for (int offset = 0; offset < totalLen; offset += packetSize) {
    int packetLen = min(packetSize, totalLen - offset);
    uint8_t buffer[headerSize + packetLen];

    // Add header with sequence number and last packet flag
    buffer[0] = (seqNo >> 8) & 0xFF;  // Higher byte of seqNo
    buffer[1] = seqNo & 0xFF;          // Lower byte of seqNo
    buffer[2] = (offset + packetLen >= totalLen) ? 1 : 0; // Last packet flag
    memcpy(buffer + headerSize, fb->buf + offset, packetLen);

    udp.beginPacket(udpAddress, udpPort);
    udp.write(buffer, headerSize + packetLen);
    udp.endPacket();

    seqNo++;
    delay(100);  // Small delay to prevent UDP buffer overload
  }

  //Serial.println("frame sent");
  esp_camera_fb_return(fb);
  delay(1000);  // Adjust delay to control frame rate
  
}
