#include <Arduino.h>
#include <LiquidCrystal.h>

const int micPin = A0;

// LCD pins
const int lcdRs = 12;
const int lcdE  = 11;
const int lcdD4 = 5;
const int lcdD5 = 4;
const int lcdD6 = 3;
const int lcdD7 = 2;

const int alertLed = 8;

LiquidCrystal lcd(lcdRs, lcdE, lcdD4, lcdD5, lcdD6, lcdD7);

const int soundThreshold = 400;

volatile bool alertTriggered = false;
volatile int isrSoundLevel = 0;
volatile uint8_t isrTickCount = 0;

ISR(TIMER1_COMPA_vect) {

  isrSoundLevel = analogRead(micPin);

  isrTickCount++;

  if (isrSoundLevel > soundThreshold) {
    alertTriggered = true;
  }
}

const unsigned long ledFlashDuration = 200;

unsigned long ledOnTime = 0;
bool ledFlashing = false;

void setup() {

  Serial.begin(9600);

  pinMode(alertLed, OUTPUT);
  digitalWrite(alertLed, LOW);

  lcd.begin(16, 2);

  lcd.print("Sound Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Initialising...");

  delay(1000);

  lcd.clear();

  // ---- Timer1 configuration ----

  noInterrupts();

  TCCR1A = 0;
  TCCR1B = 0;

  TCNT1 = 0;

  OCR1A = 155;

  TCCR1B |= (1 << WGM12);

  TCCR1B |= (1 << CS12) | (1 << CS10);

  TIMSK1 |= (1 << OCIE1A);

  interrupts();

  Serial.println("STATE=READY");
}

void loop() {

  noInterrupts();

  int soundLevel = isrSoundLevel;
  uint8_t ticks = isrTickCount;

  interrupts();

  if (ticks >= 10) {

    noInterrupts();
    isrTickCount = 0;
    interrupts();

    float soundVolt = soundLevel * 5.0 / 1023.0;

    lcd.setCursor(0, 0);
    lcd.print("Lvl:");
    lcd.print(soundVolt, 2);
    lcd.print("V      ");

    lcd.setCursor(0, 1);
    lcd.print("Raw:");
    lcd.print(soundLevel);

    if (soundLevel > soundThreshold) {
      lcd.print(" LOUD ");
    }
    else {
      lcd.print(" OK   ");
    }

    Serial.print("level=");
    Serial.print(soundLevel);
    Serial.print(",volt=");
    Serial.print(soundVolt, 2);
    Serial.print(",status=");

    if (soundLevel > soundThreshold) {
      Serial.println("LOUD");
    }
    else {
      Serial.println("OK");
    }
  }

  if (alertTriggered) {

    alertTriggered = false;

    digitalWrite(alertLed, HIGH);

    ledOnTime = millis();

    ledFlashing = true;
  }

  if (ledFlashing && (millis() - ledOnTime >= ledFlashDuration)) {

    digitalWrite(alertLed, LOW);

    ledFlashing = false;
  }
}
