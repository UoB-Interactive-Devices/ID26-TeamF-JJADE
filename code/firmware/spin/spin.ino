#include <ESP32Servo.h>

Servo ringServo;
Servo gearServo;

int ringPos = 0;
int targetRingPos = 0;

int gearPos = 0;

int ringPin = D9;
int gearPin = D8;

String input = "none";
String selectedSpice = "none";

bool gearPushingOut = false;
bool gearPullingBack = false;

bool isMovingRing = false;
bool isDispensing = false;
bool dispenseStarted = false;

unsigned long lastRingMove = 0;
unsigned long lastGearMove = 0;

const int ringStepSize = 1;       // degrees per step
const int ringMoveInterval = 15;   // ms between ring steps
const int gearMoveInterval = 10;   // ms between gear steps

int getSpicePosition(String spice) {
  spice.toLowerCase();

  if (spice == "cumin") return 30;
  if (spice == "pepper") return 45;
  if (spice == "salt") return 75;
  if (spice == "oregano") return 98;
  if (spice == "flakes") return 120;

  return -1;
}

void startSpiceSequence(String spice) {
  int targetPos = getSpicePosition(spice);

  if (targetPos == -1) {
    Serial.println("ERR unknown spice");
    return;
  }

  selectedSpice = spice;
  targetRingPos = targetPos;
  isMovingRing = true;
  isDispensing = false;
  dispenseStarted = false;
  gearPushingOut = false;
  gearPullingBack = false;

  Serial.print("OK ");
  Serial.println(spice);
}

void handleCommand(String input) {
  input.trim();
  input.toLowerCase();

  if (input.startsWith("spice ")) {
    String spice = input.substring(6);
    spice.trim();
    startSpiceSequence(spice);
  } else if (input == "reset") {
    ringPos = 0;
    targetRingPos = 0;
    gearPos = 0;
    ringServo.write(ringPos);
    gearServo.write(gearPos);
    isMovingRing = false;
    isDispensing = false;
    dispenseStarted = false;
    Serial.println("OK reset");
  } else {
    Serial.println("ERR unknown command");
  }
}

void readSerial() {
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');
    handleCommand(input);
  }
}

void updateRing() {
  if (!isMovingRing) return;

  if (millis() - lastRingMove < ringMoveInterval) return;
  lastRingMove = millis();

  if (ringPos < targetRingPos) {
    ringPos += ringStepSize;
    if (ringPos > targetRingPos) ringPos = targetRingPos;
    ringServo.write(ringPos);
  } else if (ringPos > targetRingPos) {
    ringPos -= ringStepSize;
    if (ringPos < targetRingPos) ringPos = targetRingPos;
    ringServo.write(ringPos);
    } else {
    isMovingRing = false;
    isDispensing = true;
    dispenseStarted = false;
    gearPushingOut = true;
    gearPullingBack = false;
  }
}

void updateGear() {
  if (!isDispensing) return;

  if (millis() - lastGearMove < gearMoveInterval) return;
  lastGearMove = millis();

  if (gearPushingOut) {
    if (gearPos < 180) {
      gearPos += 1;
      if (gearPos > 180) gearPos = 180;
      gearServo.write(gearPos);
    } else {
      gearPushingOut = false;
      gearPullingBack = true;
    }
    return;
  }

  if (gearPullingBack) {
    if (gearPos > 0) {
      gearPos -= 1;
      if (gearPos < 0) gearPos = 0;
      gearServo.write(gearPos);
    } else {
      gearPullingBack = false;
      isDispensing = false;
      Serial.println("DONE");
    }
  }
}

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

  ringServo.write(ringPos);
  gearServo.write(gearPos);

  Serial.println("Ready");
}

void loop() {
  readSerial();
  updateRing();
  updateGear();
}