#include <Wire.h>

#include <RTClib.h>

#include <LedControl.h>



// MAX7219 pins

const int DIN_PIN = 11;

const int CLK_PIN = 13;

const int CS_PIN = 10;



// IO pins

const int BUTTON_PIN = 2;

const int LED_PIN = 7;



// Game settings

const int TARGET_VALUE = 7;

const unsigned long WINDOW = 10000;  // ±100 ms as required



RTC_DS1307 rtc;

LedControl lc(DIN_PIN, CLK_PIN, CS_PIN, 1);



// State machine

int state = 0;   // 0 = idle, 1 = counting

int counter = 0;

int lastSecond = -1;

unsigned long targetTime = 0;

int lastButton = HIGH;



// Digit patterns

const byte DIGITS[10][8] = {

 {B00111100,B01100110,B01101110,B01110110,B01100110,B01100110,B00111100,B00000000},

 {B00011000,B00111000,B00011000,B00011000,B00011000,B00011000,B00111100,B00000000},

 {B00111100,B01100110,B00000110,B00001100,B00110000,B01100000,B01111110,B00000000},

 {B00111100,B01100110,B00000110,B00011100,B00000110,B01100110,B00111100,B00000000},

 {B00001100,B00011100,B00101100,B01001100,B01111110,B00001100,B00001100,B00000000},

 {B01111110,B01100000,B01111100,B00000110,B00000110,B01100110,B00111100,B00000000},

 {B00111100,B01100110,B01100000,B01111100,B01100110,B01100110,B00111100,B00000000},

 {B01111110,B01100110,B00000110,B00001100,B00011000,B00011000,B00011000,B00000000},

 {B00111100,B01100110,B01100110,B00111100,B01100110,B01100110,B00111100,B00000000},

 {B00111100,B01100110,B01100110,B00111110,B00000110,B01100110,B00111100,B00000000}

};



void setup() {

 pinMode(BUTTON_PIN, INPUT_PULLUP);

 pinMode(LED_PIN, OUTPUT);



 lc.shutdown(0, false);

 lc.setIntensity(0, 8);

 lc.clearDisplay(0);



 Wire.begin();

 rtc.begin();



 displayNumber(0);

}



void loop() {



 int button = digitalRead(BUTTON_PIN);

 bool pressed = (lastButton == HIGH && button == LOW);

 lastButton = button;



 DateTime now = rtc.now();

 int sec = now.second();



 // ---------- IDLE ----------

 if (state == 0) {

  if (pressed) {

   counter = 0;

   displayNumber(counter);

   lastSecond = sec;

   state = 1;

  }

 }



 // ---------- COUNTING ----------

 else if (state == 1) {



  // EARLY PRESS

  if (pressed && counter < TARGET_VALUE) {

   showEarly();

   resetGame();

   return;

  }



  if (sec != lastSecond) {

   lastSecond = sec;

   counter++;



   if (counter <= 9) {

    displayNumber(counter);

   }



   if (counter == TARGET_VALUE) {

    targetTime = millis();

   }



   if (counter == 10) {

    showTen();

   }

  }



  // CORRECT or LATE press (after target)

  if (pressed && counter >= TARGET_VALUE) {



   unsigned long diff = millis() - targetTime;



   if (diff <= WINDOW) {

    showCorrect();

   } else {

    showLate();

   }



   resetGame();

  }

 }

}



// ---------------- FUNCTIONS ----------------



void displayNumber(int value) {

 lc.clearDisplay(0);

 for (int row = 0; row < 8; row++) {

  lc.setRow(0, row, DIGITS[value][row]);

 }

}



void showTen() {

 for (int row = 0; row < 8; row++) {

  lc.setRow(0, row, B11111111);

 }

}



void showEarly() {

 digitalWrite(LED_PIN, HIGH);

 delay(1500);

 digitalWrite(LED_PIN, LOW);

}



void showCorrect() {

 for (int i = 0; i < 6; i++) {

  digitalWrite(LED_PIN, HIGH);

  delay(200);

  digitalWrite(LED_PIN, LOW);

  delay(200);

 }

}



void showLate() {

 for (int i = 0; i < 12; i++) {

  digitalWrite(LED_PIN, HIGH);

  delay(80);

  digitalWrite(LED_PIN, LOW);

  delay(80);

 }

}



void resetGame() {

 counter = 0;

 displayNumber(0);

 state = 0;

}
