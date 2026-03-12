#include <ESP32Servo.h>

Servo myservo;  // create servo object to control a servo
Servo gearservo;

int pos = 0;    // variable to store the servo position
int gearPos = 0;
#if defined(CONFIG_IDF_TARGET_ESP32S2) || defined(CONFIG_IDF_TARGET_ESP32S3)
int servoPin = D9;
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
int servoPin = D9;
#else
int servoPin = D9;
#endif

int gearPin = D8;


String command = "none";
String direction = "forward";
int step = 1;


void setup() {
  Serial.begin(115200);

  	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, 1000, 2000); // 

  gearservo.setPeriodHertz(50);
  gearservo.attach(gearPin, 1000, 2000);

  Serial.println("Ready");
}



void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
  }

  // makes big servo spin in one direction
  // command spin never turns itself off
  if (command == "spin" && direction == "forward") {
    if (pos < 180) {
      pos += min(step, 180);
      myservo.write(pos);
      delay(10);
    } else {
      direction = "backward";
    }
  }
  // handles other direction
  if (command == "spin" && direction == "backward") {
    if (pos > 0) {
      pos -= max(step, 0);
      myservo.write(pos);
      delay(10);
    } else {
      direction = "forward";
    }
  }

  // initial set up for pushing gears for smaller servo
  if (command == "push") {
    // first return to centre
    if (gearPos != 0){ 
      // set gearpos to 0
      gearservo.write(0);
      delay(10);
      command = "push_go"
    } 
  }

  // second part of rotating the servo until 180
  if (command == "push_go") {
    if (gearPos < 180) {
      gearPos += 1;
      gearservo.write(gearPos);
      delay(10);
    } 
  }

  // pull the rod in via the gears back to zero
  if (command == "pull") {
    if (gearPos > 0){
      gearPos -= 1;
      gearservo.write(gearPos);
      delay(10);
    }
  }

  // changes the step of the big servo
  if (command == "fast"){
    step = 5;
    command = "spin";
  }
  if (command == "slow"){
    step = 1;
    command = "spin";
  }
  
}