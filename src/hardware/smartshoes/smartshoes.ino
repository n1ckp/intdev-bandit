#include <Wire.h>
#include <L3G.h>
#include <LSM303.h>
#include <RFduinoBLE.h>

#define BLELED 4
#define DEBUG true

L3G gyro;
LSM303 accelComp;

int deviceConnected = false;

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

void setup() {
  Serial.begin(9600);

  i2c_init();

  gyro_init();
  accelComp_init();
  
  pinMode(BLELED, OUTPUT);
  
  //RFduinoBLE_advdata = advdata;
  //RFduinoBLE_advdata_len = sizeof(advdata);
  RFduinoBLE.deviceName = "SmartShoes";
  RFduinoBLE.begin();
}

char* gyro_read() {
  gyro.read();
  
  char *x = (char *) &(gyro.g.x);
  char *y = (char *) &(gyro.g.y);
  char *z = (char *) &(gyro.g.z);

  char data[12] = {
    x[0], x[1], x[2], x[3],
    y[0], y[1], y[2], y[3],
    z[0], z[1], z[2], z[3]
  };
  
  if (DEBUG) {
    Serial.print(" G ");
    Serial.print("X: ");
    Serial.print((int)gyro.g.x);
    Serial.print(" Y: ");
    Serial.print((int)gyro.g.y);
    Serial.print(" Z: ");
    Serial.print((int)gyro.g.z);
  }

  return data;
}

char* accel_read() {
  accelComp.readAcc();
  
  char data[6] = {
    char(accelComp.a.x && 0xF),
    char(accelComp.a.x >> 8),
    char(accelComp.a.y && 0xF),
    char(accelComp.a.y >> 8),
    char(accelComp.a.z && 0xF),
    char(accelComp.a.z >> 8)
  };

  if (DEBUG) {
    Serial.print(" A ");
    Serial.print("X: ");
    Serial.print(accelComp.a.x);
    Serial.print(" Y: ");
    Serial.print(accelComp.a.y);
    Serial.print(" Z: ");
    Serial.print(accelComp.a.z);
  }
  
  return data;
}

char* compass_read() {
  accelComp.readMag();
  
  char data[6] = {
    char(accelComp.m.x && 0xF),
    char(accelComp.m.x >> 8),
    char(accelComp.m.y && 0xF),
    char(accelComp.m.y >> 8),
    char(accelComp.m.z && 0xF),
    char(accelComp.m.z >> 8)
  };
  
  if (DEBUG) {
    Serial.print(" M ");
    Serial.print("X: ");
    Serial.print(accelComp.m.x);
    Serial.print(" Y: ");
    Serial.print(accelComp.m.y);
    Serial.print(" Z: ");
    Serial.print(accelComp.m.z);
  }
  
  return data;
}

void loop() {
  if (deviceConnected) {
    char *gdata = gyro_read();
    char *adata = accel_read();
    char *mdata = compass_read();         
    
    char packet[24] = {
      gdata[0], gdata[1], gdata[2], gdata[3], gdata[4], gdata[5],
      gdata[6], gdata[7], gdata[8], gdata[9], gdata[10], gdata[11],
      adata[0], adata[1], adata[2], adata[3], adata[4], adata[5],
      mdata[0], mdata[1], mdata[2], mdata[3], mdata[4], mdata[5]
    };
     
    while(!RFduinoBLE.send(packet, 24)) {
      Serial.print(".");
    }

    if (DEBUG) {
      Serial.println("");
      Serial.println(packet);
    }
  }

  delay(100);
}

void RFduinoBLE_onConnect() {
  deviceConnected = true;
  digitalWrite(BLELED, HIGH);
}

void RFduinoBLE_onDisconnect() {
  deviceConnected = false;
  digitalWrite(BLELED, LOW);
}

