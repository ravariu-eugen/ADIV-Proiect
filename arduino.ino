#include <Arduino_LSM6DS3.h>

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }

  
  
}

void loop() {
  float x, y, z;
  while(!Serial.available());
  char c = Serial.read();
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    Serial.print("Acc ");
    Serial.print(x);
    Serial.print(' ');
    Serial.print(y);
    Serial.print(' ');
    Serial.println(z);
  }
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(x, y, z);
    Serial.print("Gyro ");
    Serial.print(x);
    Serial.print(' ');
    Serial.print(y);
    Serial.print(' ');
    Serial.println(z);
  }
}
