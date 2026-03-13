# Embedded Systems Laboratory

This repository contains my **Embedded Systems laboratory projects** developed using **Arduino and Python**.  
The labs demonstrate fundamental embedded programming concepts such as **GPIO control, Analog-to-Digital Conversion (ADC), serial communication, hardware interrupts, and hardware–software integration with a Python GUI**.

---

# System Architecture

Arduino collects data from sensors and communicates with a Python interface through **serial communication**.
```
Hardware Inputs
(Joystick, Microphone, Button)
        │
        ▼
   Arduino UNO
(Microcontroller + ADC + Timers)
        │
   Output Devices
 (LEDs, LCD, LED Matrix)
        │
        ▼
 Serial Communication
        │
        ▼
 Python GUI (PyQt6)
 Real-time Monitoring
```

Additional hardware components include **LCD displays, LEDs, and an RTC module**.

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

# Technologies Used

- **Arduino (C/C++)**
- **Python**
- **PyQt6**
- Serial Communication
- Hardware Interrupts
- Analog-to-Digital Conversion (ADC)

---

# Hardware Components

- Arduino Uno
- Electret Microphone Module
- Analog Joystick Module
- MAX7219 LED Matrix
- 16x2 LCD Display
- LEDs and resistors
- Push buttons

---

# Skills Demonstrated

- Embedded C/C++ programming
- Sensor interfacing
- Hardware timers and interrupts
- Serial communication between microcontroller and PC
- Python GUI development
- Embedded system debugging and testing

---

# Author

**Pasha Zulfugarli**  
Computer Engineering Student  
ADA University
