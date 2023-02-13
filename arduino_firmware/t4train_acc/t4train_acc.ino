/*
This code gets 20 samples from the x vector of the Arduino,
then sends the 20 samples to T4Train.
*/

#include <Arduino_LSM9DS1.h>


int delimeter_length = 4;
uint8_t delimiter[] = { 0xde, 0xad, 0xbe, 0xef };
#define CAPTURE_SIZE 20
uint16_t send_x[CAPTURE_SIZE + 2];

void setup() {

  Serial.begin(115200);
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1)
      ;
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  get_samples();
  send_samples();
}

void get_samples() {
  float x, y, z;
  uint16_t x_i, y_i, z_i;

  for (int i = 0; i < CAPTURE_SIZE; i++) {
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      x_i = int(32768 * x / 1000 / 4 + 100);  //get it back to int using a modified version of the formula used in the library
      send_x[i] = x_i;
    }
  }
}

void send_samples() {



  // Channel number (channel 1 = 0, channel 2 = 1... channel n = n-1)
  send_x[CAPTURE_SIZE] = 0;
  // Frame completion byte (only after all channels sent)
  send_x[CAPTURE_SIZE + 1] = 1;



  // Send the delimiter
  Serial.write(delimiter, sizeof(delimiter));
  Serial.write((uint8_t *)send_x, sizeof(send_x));




  
}



