# Embedded Systems Laboratory

This repository contains my **Embedded Systems laboratory projects** developed using **Arduino and Python**.  
The labs demonstrate fundamental embedded programming concepts such as **GPIO control, Analog-to-Digital Conversion (ADC), serial communication, hardware interrupts, and hardware–software integration with a Python GUI**.

---

# System Architecture

Arduino collects data from sensors and communicates with a Python interface through **serial communication**.
```
Hardware Inputs
(Joystick, Microphone, Button, Keypad, IR Remote, RFID)
        │
        ▼
   Arduino UNO
(Microcontroller + ADC + Timers + SPI)
        │
   Output Devices
 (LEDs, LCD, LED Matrix, Servo, Stepper Motor, Buzzer)
        │
        ▼
 Serial Communication
        │
        ▼
 Python GUI (tkinter / PyQt6)
 Real-time Monitoring & Control
```

---

# Labs

### Lab 1 – LED Sequence
Basic Arduino program controlling multiple LEDs sequentially using digital output pins.

**Concepts used**
- GPIO digital output
- Timing control using `delay()`

---

### Lab 2 – Joystick Direction Detection
Reads analog values from a joystick module and lights LEDs depending on the movement direction.

**Concepts used**
- Analog-to-Digital Conversion (ADC)
- Sensor input processing
- Direction detection logic

---

### Lab 3 – Reaction Game with RTC
Implements a reaction timing game using a **DS1307 Real-Time Clock** and a **MAX7219 LED matrix display**.

**Concepts used**
- RTC module communication
- SPI communication with LED matrix
- Embedded state machine logic

---

### Lab 4 – Joystick Monitoring GUI
Arduino reads joystick position and sends voltage data to a **Python PyQt6 GUI**, which visualizes joystick movement in real time.

**Concepts used**
- Serial communication
- GUI development with PyQt6
- Real-time data visualization

---

### Lab 5 – Sound Monitoring System
A microphone sensor measures sound levels.  
The Arduino displays sound information on a **16x2 LCD** and sends monitoring data to a **Python interface**.

**Concepts used**
- Hardware timer interrupts
- ADC signal sampling
- LCD interface
- Embedded event handling

---

### Lab 6 – Two-Player Reaction Game
A two-player competitive reaction game controlled via Arduino with a **Python tkinter GUI**.  
A random countdown triggers a buzzer; the first player to press their button wins the round.  
A servo motor and stepper motor respond to each round result, and the GUI tracks scores, reaction times, and player statistics with persistent CSV storage.

**Concepts used**
- Servo and stepper motor control
- Serial communication with Python
- State machine logic (IDLE → COUNTDOWN → ACTIVE)
- False start detection
- Python tkinter GUI with matplotlib statistics charts
- CSV-based persistent player data storage

---

### Lab 7 – RFID Security System
A multi-stage access control system using a **4x4 keypad**, **IR remote**, and **MFRC522 RFID reader**.  
The system transitions through three states: setting a master passcode on the keypad, unlocking via IR remote, and logging RFID tag scans.  
A **Python PyQt6 GUI** displays a live tag database with scan counts, timestamps, and search functionality backed by **SQLite**.

**Concepts used**
- SPI communication with RFID (MFRC522)
- IR signal decoding (IRremote library)
- 4x4 matrix keypad interfacing
- Multi-stage state machine (WAITING_FOR_PASSCODE → LOCKED → UNLOCKED)
- LED status indicators
- Serial communication with Python
- SQLite database management
- PyQt6 GUI with real-time serial thread

---

# Technologies Used

- **Arduino (C/C++)**
- **Python**
- **tkinter** and **PyQt6**
- Serial Communication
- Hardware Interrupts
- Analog-to-Digital Conversion (ADC)
- SPI Communication
- SQLite Database

---

# Hardware Components

- Arduino Uno
- Electret Microphone Module
- Analog Joystick Module
- MAX7219 LED Matrix
- 16x2 LCD Display
- Servo Motor (SG90)
- Stepper Motor (28BYJ-48 + ULN2003 driver)
- MFRC522 RFID Reader + RFID Tags
- 4x4 Matrix Keypad
- IR Receiver + IR Remote
- LEDs and resistors
- Push buttons
- Buzzer

---

# Skills Demonstrated

- Embedded C/C++ programming
- Sensor interfacing
- Hardware timers and interrupts
- Serial communication between microcontroller and PC
- Python GUI development (tkinter, PyQt6)
- Motor control (servo and stepper)
- RFID and IR signal processing
- Database integration (SQLite)
- Embedded system debugging and testing

---

# Author

**Pasha Zulfugarli**  
Computer Engineering Student  
ADA University
