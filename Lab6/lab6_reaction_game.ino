#include <Servo.h>
#include <Stepper.h>


const int BTN1_PIN   = 2;
const int BTN2_PIN   = 3;
const int BUZZER_PIN = 8;
const int SERVO_PIN  = 9;
const int IN1 = 4, IN2 = 5, IN3 = 6, IN4 = 7;


#define SERVO_NEUTRAL  90
#define SERVO_PLAYER1  10
#define SERVO_PLAYER2  170


const int STEPS_PER_REV            = 2048;
const int STEPS_PER_POINT          = 300;
const unsigned long REACTION_TIMEOUT = 5000;


Servo gameServo;

Stepper gameStepper(STEPS_PER_REV, IN1, IN3, IN2, IN4);


enum GameState { IDLE, COUNTDOWN, ACTIVE };
GameState state = IDLE;


void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(A0));   

  pinMode(BTN1_PIN,   INPUT_PULLUP);
  pinMode(BTN2_PIN,   INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);

  
  gameServo.attach(SERVO_PIN, 500, 2500);
  gameServo.write(SERVO_NEUTRAL);

  gameStepper.setSpeed(12);     

  Serial.println("READY");
}


void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();                 
    handleCommand(cmd);
  }
}


void handleCommand(String cmd) {
  if (cmd == "START" && state == IDLE) {
    runRound();

  } else if (cmd.startsWith("WINNER:")) {
    int winner = cmd.substring(7).toInt();
    moveMotorsForWinner(winner);

  } else if (cmd.startsWith("VICTORY:")) {
    int winner = cmd.substring(8).toInt();
    victorySequence(winner);

  } else if (cmd == "RESET") {
    gameServo.write(SERVO_NEUTRAL);
    state = IDLE;
    Serial.println("RESET_OK");
  }
}


void runRound() {
  state = COUNTDOWN;

  int delaySeconds = random(1, 21);     
  unsigned long startTime = millis();
  int lastSentSecond = -1;

  
  while (millis() - startTime < (unsigned long)delaySeconds * 1000) {

    
    int remaining = delaySeconds - (int)((millis() - startTime) / 1000);
    if (remaining != lastSentSecond) {
      Serial.print("COUNTDOWN:");
      Serial.println(remaining);
      lastSentSecond = remaining;
    }

    
    if (digitalRead(BTN1_PIN) == LOW) {
      tone(BUZZER_PIN, 200, 400);   
      delay(400);
      Serial.println("FALSE:1");
      state = IDLE;
      return;
    }
    if (digitalRead(BTN2_PIN) == LOW) {
      tone(BUZZER_PIN, 200, 400);
      delay(400);
      Serial.println("FALSE:2");
      state = IDLE;
      return;
    }

    delay(10);
  }

  
  state = ACTIVE;
  tone(BUZZER_PIN, 1200, 600);          
  unsigned long buzzTime = millis();
  Serial.println("BUZZER");

  
  long t1 = -1, t2 = -1;
  bool btn1Seen = false, btn2Seen = false;

  while ((millis() - buzzTime) < REACTION_TIMEOUT) {
    if (!btn1Seen && digitalRead(BTN1_PIN) == LOW) {
      t1 = millis() - buzzTime;         
      btn1Seen = true;
    }
    if (!btn2Seen && digitalRead(BTN2_PIN) == LOW) {
      t2 = millis() - buzzTime;
      btn2Seen = true;
    }
    if (btn1Seen && btn2Seen) break;    
  }

  
  Serial.print("RESULT:");
  Serial.print(t1);
  Serial.print(":");
  Serial.println(t2);

  state = IDLE;
}


void moveMotorsForWinner(int winner) {
  
  if (winner == 1) {
    gameStepper.step(-STEPS_PER_POINT);
    gameServo.write(SERVO_PLAYER1);
  } else {
    gameStepper.step(STEPS_PER_POINT);
    gameServo.write(SERVO_PLAYER2);
  }
  Serial.println("MOTORS_OK");
}

void victorySequence(int winner) {
  gameStepper.step(STEPS_PER_REV);     

  if (winner == 1) gameServo.write(SERVO_PLAYER1);
  else             gameServo.write(SERVO_PLAYER2);

 
  int freqs[] = {1000, 1200, 1500, 1800};
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, freqs[i], 150);
    delay(200);
  }

  Serial.println("VICTORY_OK");
}
