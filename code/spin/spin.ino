#include <ESP32Servo.h>

Servo ringServo;
Servo gearServo;

int ringPos = 0;
int gearPos = 0;

int ringPin = D9;
int gearPin = D8;

String ringCommand = "none";
String gearCommand = "none";
String ringDirection = "forward";
String input = "none";
int ringStep = 1;

void setup() {
  Serial.begin(115200);

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  ringServo.setPeriodHertz(50);
  ringServo.attach(ringPin, 500, 2500);

  gearServo.setPeriodHertz(50);
  gearServo.attach(gearPin, 500, 2500);

  Serial.println("Ready");
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();

  if (cmd == "push" || cmd == "pull") {
    gearCommand = cmd;
    Serial.print("OK ");
    Serial.println(cmd);
    return;
  }

  if (cmd == "spin") {
    ringCommand = "spin";
    Serial.println("OK spin");
    return;
  }

  if (cmd == "stop") {
    ringCommand = "stop";
    Serial.println("OK stop");
    return;
  }

  if (cmd == "fast") {
    ringStep = 5;
    ringCommand = "spin";
    Serial.println("OK fast");
    return;
  }

  if (cmd == "slow") {
    ringStep = 1;
    ringCommand = "spin";
    Serial.println("OK slow");
    return;
  }

  Serial.print("ERR unknown command: ");
  Serial.println(cmd);
}

void readSerial() {
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');
    handleCommand(input);
  }
}

void updateRing() {
  if (ringCommand != "spin") {
    return;
  }

  if (ringDirection == "forward") {
    if (ringPos < 180) {
      ringPos += ringStep;
      if (ringPos > 180) ringPos = 180;
      ringServo.write(ringPos);
      delay(10);
    } else {
      ringDirection = "backward";
    }
  } else if (ringDirection == "backward") {
    if (ringPos > 0) {
      ringPos -= ringStep;
      if (ringPos < 0) ringPos = 0;
      ringServo.write(ringPos);
      delay(10);
    } else {
      ringDirection = "forward";
    }
  }
}

void updateGear() {
  if (gearCommand == "push") {
    if (gearPos != 0) {
      gearPos = 0;
      gearServo.write(gearPos);
      delay(10);
      return;
    }
    gearCommand = "push_go";
  }

  if (gearCommand == "push_go") {
    if (gearPos < 180) {
      gearPos += 1;
      if (gearPos > 180) gearPos = 180;
      gearServo.write(gearPos);
      delay(10);
    } else {
      gearCommand = "none";
    }
  }

  if (gearCommand == "pull") {
    if (gearPos > 0) {
      gearPos -= 1;
      if (gearPos < 0) gearPos = 0;
      gearServo.write(gearPos);
      delay(10);
    } else {
      gearCommand = "none";
    }
  }
}

void loop() {
  readSerial();
  updateRing();
  updateGear();
}