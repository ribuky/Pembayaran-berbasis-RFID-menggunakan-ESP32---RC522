#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFiManager.h>  

// Server Flask API
String serverBase = "http://127.0.0.1:5000/api/tapping/";

// Pin RC522
#define SS_PIN 21
#define RST_PIN 22

// Indikator
#define BUZZER_PIN 25
#define LED_BIRU 26
#define LED_MERAH 27
#define BUTTON_PIN 4

MFRC522 rfid(SS_PIN, RST_PIN);

// UID CACHE
String lastUID = "";
unsigned long lastScanTime = 0;

// Button Press Handling
unsigned long pressStart = 0;
bool buttonPressed = false;
int clickCount = 0;
unsigned long lastClickTime = 0;

void resetUIDCache() {
  lastUID = "";
  Serial.println("[CACHE] UID Cache Reset!");
}

// WIFI CONFIG MODE
void startWiFiConfig() {
  WiFiManager wm;
  wm.resetSettings();     // reset WiFi sambungan sebelumnya
  wm.setTimeout(180);     // timeout 3 menit

  if (!wm.startConfigPortal("KANTIN-RFID", "12345678")) {
    Serial.println("Gagal Konfigurasi");
    delay(3000);
    ESP.restart();
  }

  Serial.println("WiFi Config Berhasil! Rebooting...");
  delay(1000);
  ESP.restart();
}

void setup() {
  Serial.begin(115200);

  // Pin setup
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BIRU, OUTPUT);
  pinMode(LED_MERAH, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // RFID
  SPI.begin();
  rfid.PCD_Init();

  // WiFiManager (Auto Connect)
  WiFiManager wm;
  bool res = wm.autoConnect("KANTIN-RFID");

  if (!res) {
    Serial.println("Gagal AutoConnect WiFi!");
    delay(2000);
    ESP.restart();
  }

  Serial.println("WiFi Tersambung!");
  tone(BUZZER_PIN, 2000, 100);
}

void handleButton() {
  if (digitalRead(BUTTON_PIN) == LOW && !buttonPressed) {
    buttonPressed = true;
    pressStart = millis();
  }

  if (digitalRead(BUTTON_PIN) == HIGH && buttonPressed) {
    buttonPressed = false;
    unsigned long pressDuration = millis() - pressStart;

    // Klik cepat
    if (pressDuration < 300) {
      clickCount++;
      lastClickTime = millis();
    }

    // 1 klik = reload WiFi
    // 3 klik = reset UID Cache
    // Tekan lama = mode WiFi Config / Restart
    if (pressDuration >= 2000 && pressDuration < 6000) {
      Serial.println("Restart ESP...");
      ESP.restart();
    }

    if (pressDuration >= 6000) {
      Serial.println("Masuk WiFi Config Mode...");
      startWiFiConfig();
    }
  }

  if (clickCount > 0 && millis() - lastClickTime > 400) {
    if (clickCount == 1) {
      Serial.println("Reload WiFi...");
      WiFi.disconnect();
      delay(200);
      WiFi.reconnect();
    }
    if (clickCount == 3) {
      resetUIDCache();
    }
    clickCount = 0;
  }
}

void loop() {
  handleButton();

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Ambil UID
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Cegah double-scan
  if (uid == lastUID && millis() - lastScanTime < 1500) {
    return;
  }
  
  lastUID = uid;
  lastScanTime = millis();

  Serial.println("UID Tapped: " + uid);

  // Kirim GET ke server
  if (WiFi.status() == WL_CONNECTED) {
    String targetURL = serverBase + uid;

    HTTPClient http;
    http.begin(targetURL);

    int code = http.GET();
    Serial.print("HTTP Code: ");
    Serial.println(code);

    String resp = http.getString();
    Serial.println(resp);

    if (resp.indexOf("\"status\":\"success\"") >= 0) {
      digitalWrite(LED_BIRU, HIGH);
      tone(BUZZER_PIN, 2000, 150);
      delay(300);
      digitalWrite(LED_BIRU, LOW);
    } else {
      digitalWrite(LED_MERAH, HIGH);
      tone(BUZZER_PIN, 800, 250);
      delay(350);
      digitalWrite(LED_MERAH, LOW);
    }

    http.end();
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
