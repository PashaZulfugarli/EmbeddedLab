#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>
#include <IRremote.hpp>


#define RST_PIN         9
#define SS_PIN          10
#define IR_RECEIVE_PIN  A1
#define LED_RED         A2
#define LED_GREEN       A3


  WAITING_FOR_PASSCODE,
  LOCKED,
  UNLOCKED
};

State currentState = WAITING_FOR_PASSCODE;

String masterCode = "";
String currentInput = "";


const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};


byte rowPins[ROWS] = {8, 7, 6, 5};
byte colPins[COLS] = {4, 3, 2, A0};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);


MFRC522 mfrc522(SS_PIN, RST_PIN);


const unsigned long IR_COOLDOWN_MS = 450;
const unsigned long RFID_COOLDOWN_MS = 3000;


void setup() {
  Serial.begin(9600);

  SPI.begin();
  mfrc522.PCD_Init();

  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);

  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);

  Serial.println("--- SECURITY SYSTEM INITIALIZED ---");
  Serial.println("Step 1: Enter a 4-digit code on the KEYPAD to lock.");
}

void loop() {
  updateLEDs();

  switch (currentState) {
    case WAITING_FOR_PASSCODE:
      handleKeypad();
      break;

    case LOCKED:
      handleIR();
      break;

    case UNLOCKED:
      handleRFID();
      break;
  }
}

void handleKeypad() {
  char key = keypad.getKey();

  if (!key) {
    return;
  }

  if (key >= '0' && key <= '9') {
    currentInput += key;
    Serial.print("*");

    if (currentInput.length() == 4) {
      masterCode = currentInput;
      currentInput = "";

      currentState = LOCKED;

      Serial.println();
      Serial.print("[CODE SAVED] Master code length: ");
      Serial.println(masterCode.length());
      Serial.println("[SYSTEM LOCKED] Use IR remote to unlock.");
    }
  }

  if (key == '*') {
    currentInput = "";
    Serial.println();
    Serial.println("[KEYPAD INPUT CLEARED]");
  }
}

void handleIR() {
  static unsigned long lastIRTime = 0;
  static uint16_t lastCommand = 0;

  if (!IrReceiver.decode()) {
    return;
  }

  uint16_t command = IrReceiver.decodedIRData.command;
  unsigned long now = millis();

  if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) {
    IrReceiver.resume();
    return;
  }

  if (command == lastCommand && now - lastIRTime < IR_COOLDOWN_MS) {
    IrReceiver.resume();
    return;
  }

  char digit = decodeIRDigit(command);

  if (digit != 'X') {
    currentInput += digit;

    Serial.print("IR Digit Recorded: ");
    Serial.print(digit);
    Serial.print(" (");
    Serial.print(currentInput.length());
    Serial.println("/4)");

    lastCommand = command;
    lastIRTime = now;

    if (currentInput.length() == 4) {
      if (currentInput == masterCode) {
        currentState = UNLOCKED;
        Serial.println("[ACCESS GRANTED] RFID Reader Enabled.");
      } else {
        Serial.println("[DENIED] Incorrect Code. Try again.");
      }

      currentInput = "";
    }
  }

  IrReceiver.resume();
}

void handleRFID() {
  static String lastUid = "";
  static unsigned long lastReadTime = 0;

  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  String uid = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uid += "0";
    }

    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();

  unsigned long now = millis();

  if (uid == lastUid && now - lastReadTime < RFID_COOLDOWN_MS) {
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    return;
  }

  lastUid = uid;
  lastReadTime = now;

  flashSuccessLED();

  Serial.print("DATA_PACKET:");
  Serial.println(uid);

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void updateLEDs() {
  static unsigned long lastMillis = 0;
  static bool blinkState = false;

  if (currentState == WAITING_FOR_PASSCODE) {
    if (millis() - lastMillis > 500) {
      lastMillis = millis();
      blinkState = !blinkState;

      digitalWrite(LED_RED, blinkState);
      digitalWrite(LED_GREEN, blinkState);
    }
  }

  else if (currentState == LOCKED) {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
  }

  else if (currentState == UNLOCKED) {
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, HIGH);
  }
}

void flashSuccessLED() {
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, HIGH);
  delay(150);

  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, HIGH);
}

char decodeIRDigit(uint16_t cmd) {
  switch (cmd) {
    case 0x16: return '0';
    case 0x0C: return '1';
    case 0x18: return '2';
    case 0x5E: return '3';
    case 0x08: return '4';
    case 0x1C: return '5';
    case 0x5A: return '6';
    case 0x42: return '7';
    case 0x52: return '8';
    case 0x4A: return '9';

    default:
      return 'X';
  }
}
