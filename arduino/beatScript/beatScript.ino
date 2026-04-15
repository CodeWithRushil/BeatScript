#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

String incoming = "";

const int ledPins[] = {2, 3, 4, 5};
unsigned long lastLedUpdate = 0;
int ledStep = 0;
int currentPattern = 0;
int ledInterval = 150;
bool discoActive = false;

String getLine(String text, int start) {
  int end = start + 16;
  if (end >= text.length()) return text.substring(start);
  int spaceIndex = text.lastIndexOf(' ', end);
  if (spaceIndex <= start) spaceIndex = end;
  return text.substring(start, spaceIndex);
}

void displayText(String text) {
  lcd.clear();
  String line1 = getLine(text, 0);
  String line2 = "";
  if (text.length() > line1.length()) {
    line2 = getLine(text, line1.length());
  }
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void turnOffLEDs() {
  for (int i = 0; i < 4; i++) digitalWrite(ledPins[i], LOW);
}

void runDisco() {
  if (!discoActive) {
    turnOffLEDs();
    return;
  }
  if (millis() - lastLedUpdate > ledInterval) {
    lastLedUpdate = millis();
    ledStep++;
    turnOffLEDs();
    switch (currentPattern) {
      case 0:
        digitalWrite(ledPins[ledStep % 4], HIGH);
        break;
        
      case 1:
        if (ledStep % 2 == 0) {
          digitalWrite(ledPins[0], HIGH);
          digitalWrite(ledPins[2], HIGH);
        } else {
          digitalWrite(ledPins[1], HIGH);
          digitalWrite(ledPins[3], HIGH);
        }
        break;
        
      case 2:
        if (ledStep % 2 == 0) {
          digitalWrite(ledPins[0], HIGH);
          digitalWrite(ledPins[3], HIGH);
        } else {
          digitalWrite(ledPins[1], HIGH);
          digitalWrite(ledPins[2], HIGH);
        }
        break;
        
      case 3:
        digitalWrite(ledPins[random(0, 4)], HIGH);
        digitalWrite(ledPins[random(0, 4)], HIGH);
        break;
    }
  }
}

void smartDelay(unsigned long ms) {
  unsigned long start = millis();
  while (millis() - start < ms) {
    runDisco();
  }
}

void countdown() {
  for (int i = 5; i > 0; i--) {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Starting in:");
    lcd.setCursor(0,1);
    lcd.print(i);
    smartDelay(1000);
  }

  lcd.clear();
  lcd.print("PLAY NOW!");
  smartDelay(400);
}

void setup() {
  lcd.init();
  lcd.backlight();
  for (int i = 0; i < 4; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
  Serial.begin(9600);
  Serial.setTimeout(50);
}

void loop() {
  runDisco();
  if (Serial.available()) {
    incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming.startsWith("TITLE:")) {
      String song = incoming.substring(6);
      displayText(song);
      discoActive = true;
      currentPattern = 0;
      smartDelay(2000);
      countdown();
    }

    else if (incoming == "NO_LYRICS") {
      lcd.clear();
      lcd.print("No Lyrics Found");
      discoActive = false;
      turnOffLEDs();
      smartDelay(2000);
    }

    else {
      displayText(incoming);
      currentPattern = random(0, 4);      
      ledInterval = random(80, 250);
    }
  }
}