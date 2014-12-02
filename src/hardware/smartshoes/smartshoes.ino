#include <Wire.h>
#include <L3G.h>
#include <LSM303.h>
#include <RFduinoBLE.h>
#include <stdint.h>

#define BLELED 4
#define DEBUG false

#define LDRS0 0
#define LDRS1 1
#define LDRS2 2

#define LDROUT 3

#define CALIBRATELDR true

int ldrthresh = 30;

int rawldr[40] = {0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0};

L3G gyro;
LSM303 accelComp;

int deviceConnected = false;

char packet[19] = {
  0x1, 0x2, 0x3, 0x4, 0x5, 0x6,
  0x7, 0x8, 0x9, 0xA, 0xB, 0xC,
  0xD, 0xE, 0xF, 0x1, 0x2, 0x3,
  0.0
};

void i2c_init() {
  Wire.begin();
}

void gyro_init() {
  if (!gyro.init()) {
    Serial.println("Failed to autodetect gyro type!");
    while(1);
  }

  gyro.enableDefault();
  gyro.writeReg(L3G_CTRL_REG4, 0x20); // 2000 dps full scale
  gyro.writeReg(L3G_CTRL_REG1, 0x0F); // normal power mode, all axes enabled, 100 Hz
}

void accelComp_init() {
  if (!accelComp.init()) {
    Serial.println("Failed to autodetect accel type!");
    while(1);
  }

  accelComp.enableDefault();
  accelComp.writeReg(LSM303::CTRL2, 0x18); // 8 g full scale: AFS = 011

}

void setldrthresh() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(BLELED, HIGH);
    //A0 000
    digitalWrite(LDRS0, LOW);
    digitalWrite(LDRS1, LOW);
    digitalWrite(LDRS2, LOW);
    rawldr[i*8] = analogRead(LDROUT);

    //A1 001
    digitalWrite(LDRS0, HIGH);
    rawldr[i*8 + 1] = analogRead(LDROUT);

    //A3 011
    digitalWrite(LDRS1, HIGH);
    rawldr[i*8 + 3] = analogRead(LDROUT);

    //A2 010
    digitalWrite(LDRS0, LOW);
    rawldr[i*8 + 2] = analogRead(LDROUT);

    //A6 110
    digitalWrite(LDRS2, HIGH);
    rawldr[i*8 + 6] = analogRead(LDROUT);

    //A7 111
    digitalWrite(LDRS0, HIGH);
    rawldr[i*8 + 7] = analogRead(LDROUT);

    //A5 101
    digitalWrite(LDRS1, LOW);
    rawldr[i*8 + 5] = analogRead(LDROUT);

    //A4 100
    digitalWrite(LDRS0, LOW);
    rawldr[i*8 + 4] = analogRead(LDROUT);

    delay(500);
    digitalWrite(BLELED, LOW);
    delay(500);
  }

  int toeSum = 0;
  int restSum = 0;

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 8; j++) {
      if (j == 4) {
        toeSum += rawldr[i*8 + j];
      } else {
        restSum += rawldr[i*8 + j];
      }
    }
  }

  ldrthresh = ((toeSum / 5) + (restSum / 35)) / 2;
}

void offBoard_init() {
  pinMode(LDRS0, OUTPUT);
  pinMode(LDRS1, OUTPUT);
  pinMode(LDRS2, OUTPUT);

  pinMode(LDROUT, INPUT);

  if (CALIBRATELDR) {
    setldrthresh();
  }
}

void setup() {
  if (DEBUG) {
    Serial.begin(9600);
  }

  i2c_init();

  gyro_init();
  accelComp_init();

  pinMode(BLELED, OUTPUT);

  offBoard_init();

  RFduinoBLE.deviceName = "SmartShoes";
  RFduinoBLE.begin();
}

void gyro_read() {
  gyro.read();

  int gix = (int) gyro.g.x;
  int giy = (int) gyro.g.y;
  int giz = (int) gyro.g.z;

  char *x = (char *) &(gix);
  char *y = (char *) &(giy);
  char *z = (char *) &(giz);

  packet[0] = x[0];
  packet[1] = x[1];

  packet[2] = y[0];
  packet[3] = y[1];

  packet[4] = z[0];
  packet[5] = z[1];

  if (DEBUG) {
    Serial.print(" G ");
    Serial.print("X: ");
    Serial.print((int)gyro.g.x);
    Serial.print(" Y: ");
    Serial.print((int)gyro.g.y);
    Serial.print(" Z: ");
    Serial.print((int)gyro.g.z);
  }
}

void accel_read() {
  accelComp.readAcc();

  char *x = (char *) &(accelComp.a.x);
  char *y = (char *) &(accelComp.a.y);
  char *z = (char *) &(accelComp.a.z);

  packet[6] = x[0];
  packet[7] = x[1];

  packet[8] = y[0];
  packet[9] = y[1];

  packet[10] = z[0];
  packet[11] = z[1];

  if (DEBUG) {
    Serial.print(" A ");
    Serial.print("X: ");
    Serial.print(accelComp.a.x);
    Serial.print(" Y: ");
    Serial.print(accelComp.a.y);
    Serial.print(" Z: ");
    Serial.print(accelComp.a.z);
  }
}

void compass_read() {
  accelComp.readMag();

  char *x = (char *) &(accelComp.m.x);
  char *y = (char *) &(accelComp.m.y);
  char *z = (char *) &(accelComp.m.z);

  packet[12] = x[0];
  packet[13] = x[1];

  packet[14] = y[0];
  packet[15] = y[1];

  packet[16] = z[0];
  packet[17] = z[1];

  if (DEBUG) {
    Serial.print(" M ");
    Serial.print("X: ");
    Serial.print(accelComp.m.x);
    Serial.print(" Y: ");
    Serial.print(accelComp.m.y);
    Serial.print(" Z: ");
    Serial.print(accelComp.m.z);
  }
}

void offBoard_read() {
  char sensorData = 0;
  int av;

  //A0 000
  digitalWrite(LDRS0, LOW);
  digitalWrite(LDRS1, LOW);
  digitalWrite(LDRS2, LOW);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 0;

  //A1 001
  digitalWrite(LDRS0, HIGH);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 1;

  //A3 011
  digitalWrite(LDRS1, HIGH);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 3;

  //A2 010
  digitalWrite(LDRS0, LOW);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 2;

  //A6 110
  digitalWrite(LDRS2, HIGH);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 6;

  //A7 111
  digitalWrite(LDRS0, HIGH);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 7;

  //A5 101
  digitalWrite(LDRS1, LOW);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 5;

  //A4 100
  digitalWrite(LDRS0, LOW);
  av = analogRead(LDROUT);
  if (av < ldrthresh) sensorData |= 1 << 4;

  packet[18] = sensorData;
}

void loop() {
  if (deviceConnected) {
    gyro_read();
    accel_read();
    compass_read();
    offBoard_read();

    RFduinoBLE.send(packet, sizeof(packet));

    if (DEBUG) {
      Serial.println("");
    }
  }

  //delay(100);
}

void RFduinoBLE_onConnect() {
  deviceConnected = true;
  digitalWrite(BLELED, HIGH);
}

void RFduinoBLE_onDisconnect() {
  deviceConnected = false;
  digitalWrite(BLELED, LOW);
}

