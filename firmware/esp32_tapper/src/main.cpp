#include <Arduino.h>
#include <ArduinoJson.h>
#include "HX711.h"

// Pin Definitions
const int SOLENOID_PIN = 4;
const int TRIGGER_PIN = 2; // Sent to DAQ
const int HX711_DOUT_PIN = 16;
const int HX711_SCK_PIN = 17;

// HX711 Load Cell
HX711 scale;
float calibration_factor = -105.0; 

// State
unsigned long last_tap_time = 0;
const unsigned long MIN_INTER_TAP_MS = 500;

// Pulse width configurations based on calibration (mock values for now)
unsigned long pw_level_1 = 5000;
unsigned long pw_level_2 = 10000;
unsigned long pw_level_3 = 15000;
unsigned long current_pw = pw_level_1;

void setup() {
  Serial.begin(115200);
  
  pinMode(SOLENOID_PIN, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);
  
  pinMode(TRIGGER_PIN, OUTPUT);
  digitalWrite(TRIGGER_PIN, LOW);
  
  scale.begin(HX711_DOUT_PIN, HX711_SCK_PIN);
  scale.set_scale(calibration_factor);
  scale.tare(); // Reset the scale to 0
  
  Serial.println("{\"status\": \"ready\"}");
}

void fire_solenoid(unsigned long pulse_width_us) {
  // Fire pulse & trigger pulse simultaneously
  digitalWrite(TRIGGER_PIN, HIGH);
  digitalWrite(SOLENOID_PIN, HIGH);
  
  delayMicroseconds(pulse_width_us);
  
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(TRIGGER_PIN, LOW);
}

void process_command(String cmd) {
  cmd.trim();
  StaticJsonDocument<256> doc;
  
  if (cmd.startsWith("TAP")) {
    int level = cmd.substring(4).toInt();
    
    if (millis() - last_tap_time < MIN_INTER_TAP_MS) {
      doc["error"] = "Thermal protection: tap too soon";
    } else {
      unsigned long pw = current_pw;
      if (level == 1) pw = pw_level_1;
      else if (level == 2) pw = pw_level_2;
      else if (level == 3) pw = pw_level_3;
      
      // Measure preload
      float preload = scale.get_units(5);
      
      // Fire
      fire_solenoid(pw);
      last_tap_time = millis();
      
      // We cannot read HX711 fast enough for impact peak (80 SPS max).
      // So we report preload and the configured level.
      doc["tap_success"] = true;
      doc["level"] = level;
      doc["pulse_width_us"] = pw;
      doc["peak_force"] = preload; // (mocked as preload)
    }
  } 
  else if (cmd.startsWith("SET_PW")) {
    current_pw = cmd.substring(7).toInt();
    doc["pw_set"] = current_pw;
  }
  else if (cmd.equals("TARE")) {
    scale.tare();
    doc["tared"] = true;
  }
  else if (cmd.equals("READ_FORCE")) {
    doc["force"] = scale.get_units(5);
  }
  else if (cmd.equals("STATUS")) {
    doc["ready"] = true;
  }
  else if (cmd.equals("ID")) {
    doc["device"] = "ESP32_Tapper";
    doc["version"] = "1.0.0";
  }
  else {
    doc["error"] = "Unknown command";
  }
  
  doc["timestamp_ms"] = millis();
  serializeJson(doc, Serial);
  Serial.println();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    process_command(command);
  }
}
