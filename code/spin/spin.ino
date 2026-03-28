#include <ESP32Servo.h>

Servo ringServo;  // create servo object to control a servo
Servo gearServo;

int ringPos = 0;    // variable to store the servo position
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

  	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	ringServo.setPeriodHertz(50);    // standard 50 hz servo
	ringServo.attach(ringPin, 1000, 2000); // 

  gearServo.setPeriodHertz(50);
  gearServo.attach(gearPin, 1000, 2000);

  Serial.println("Ready");
}



void loop() {
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');
    input.trim();

    if (input == "push" || input == "pull") {
      gearCommand = input;
    } else {
      ringCommand = input;
    }
  }

  // makes big servo spin in one direction
  // command spin never turns itself off
  if (ringCommand == "spin" && ringDirection == "forward") {
    if (ringPos < 180) {
      ringPos += min(ringStep, 180);
      ringServo.write(ringPos);
      delay(10);
    } else {
      ringDirection = "backward";
    }
  }
  // handles other direction
  if (ringCommand == "spin" && ringDirection == "backward") {
    if (ringPos > 0) {
      ringPos -= max(ringStep, 0);
      ringServo.write(ringPos);
      delay(10);
    } else {
      ringDirection = "forward";
    }
  }

  // initial set up for pushing gears for smaller servo
  if (gearCommand == "push") {
    // first return to centre
    if (gearPos != 0){ 
      // set gearpos to 0
      gearPos = 0;
      gearServo.write(0);
      delay(10);
    } 
    gearCommand = "push_go";
  }

  // second part of rotating the servo until 180
  if (gearCommand == "push_go") {
    if (gearPos < 180) {
      gearPos += 1;
      gearServo.write(gearPos);
      delay(10);
      // command stays the same
    } else {
      gearCommand = "none";
    }
  }

  // pull the rod in via the gears back to zero
  if (gearCommand == "pull") {
    if (gearPos > 0){
      gearPos -= 1;
      gearServo.write(gearPos);
      delay(10);
    } else {
      gearCommand = "none";
    }
  }

  // changes the step of the big servo
  if (ringCommand == "fast"){
    ringStep = 5;
    ringCommand = "spin";
  }
  if (ringCommand == "slow"){
    ringStep = 1;
    ringCommand = "spin";
  }
  
}