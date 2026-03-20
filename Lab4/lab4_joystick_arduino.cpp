#include <Arduino.h>



const int xPin = A0;

const int yPin = A1;



const int upLed = 10;

const int downLed = 9;

const int leftLed = 11;

const int rightLed = 6;



bool running = false;

unsigned long lastSend = 0;

const unsigned long interval = 50;




const bool LED_ACTIVE_LOW = false;



inline void ledOn(int pin) { digitalWrite(pin, LED_ACTIVE_LOW ? LOW : HIGH); }

inline void ledOff(int pin) { digitalWrite(pin, LED_ACTIVE_LOW ? HIGH : LOW ); }



inline void allOff() {

 ledOff(upLed);

 ledOff(downLed);

 ledOff(leftLed);

 ledOff(rightLed);

}



void setup() {

 Serial.begin(9600);



 pinMode(xPin, INPUT);

 pinMode(yPin, INPUT);



 pinMode(upLed, OUTPUT);

 pinMode(downLed, OUTPUT);

 pinMode(leftLed, OUTPUT);

 pinMode(rightLed, OUTPUT);



 allOff();



 Serial.println("SYSTEM READY");

}



void loop() {



 

 if (Serial.available()) {

  String cmd = Serial.readStringUntil('\n');

  cmd.trim();



  if (cmd == "START") {

   running = true;

   Serial.println("STATE=RUNNING");

  }



  if (cmd == "STOP") {

   running = false;

   allOff();

   Serial.println("STATE=STOPPED");

  }

 }



 if (!running) {

  allOff();

  return;

 }



 

 unsigned long now = millis();

 if (now - lastSend < interval) return;

 lastSend = now;



 

 int xVal = analogRead(xPin);

 int yVal = analogRead(yPin);



 float xVolt = xVal * 5.0 / 1023.0;

 float yVolt = yVal * 5.0 / 1023.0;



 allOff();



 String direction = "CENTER";



 if (yVal <= 510) {

  ledOn(upLed);

  direction = "UP";

 }

 else if (yVal >= 525) {

  ledOn(downLed);

  direction = "DOWN";

 }

 else if (xVal <= 505) {

  ledOn(leftLed);

  direction = "LEFT";

 }

 else if (xVal >= 515) {

  ledOn(rightLed);

  direction = "RIGHT";

 }



 

 Serial.print("x=");

 Serial.print(xVolt, 2);

 Serial.print(",y=");

 Serial.print(yVolt, 2);

 Serial.print(",dir=");

 Serial.println(direction);

}
