#include <ESP32Servo.h>

Servo myservo;  // create servo object to control a servo

int pos = 0;    // variable to store the servo position
#if defined(CONFIG_IDF_TARGET_ESP32S2) || defined(CONFIG_IDF_TARGET_ESP32S3)
int servoPin = D9;
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
int servoPin = D9;
#else
int servoPin = D9;
#endif


String command = "none";
String direction = "forward";


void setup() {
  Serial.begin(115200);

  	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, 1000, 2000); // 

  Serial.println("Ready");
}



void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
  }

  if (command == "spin" && direction == "forward") {
    if (pos < 180) {
      pos += 1;
      myservo.write(pos);
      delay(10);
    } else {
      direction = "backward";
    }
  }
  if (command == "spin" && direction == "backward") {
    if (pos > 0) {
      pos -= 1;
      myservo.write(pos);
      delay(10);
    } else {
      direction = "forward";
    }
  }
  
}