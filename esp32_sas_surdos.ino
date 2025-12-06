#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ============ CONFIG PARA WOKWI ============
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT
const char* mqttServer = "test.mosquitto.org";
const uint16_t mqttPort = 1883;

const char* topic_alert = "sas_surdos/alerta";

// Pinos simulados no Wokwi
const int pinoSom = 34;     // potenciômetro A0 do wokwi
const int ledAlerta = 2;   
const int ledVibra = 4;    

// threshold e debounce
const int threshold = 2000;
const unsigned long debounceMs = 3000;

// ============ GLOBALS ============
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastPublish = 0;
const char* deviceId = "ESP32_SAS_SURDOS_WOKWI";

// ============ FUNCOES ============
void connectWiFi() {
  Serial.print("Conectando WiFi ");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi conectado, IP: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {
  Serial.print("Conectando MQTT...");
  client.setServer(mqttServer, mqttPort);
  while (!client.connected()) {
    if (client.connect(deviceId)) {
      Serial.println("conectado ao broker!");
      client.subscribe("sas_surdos/teste");
    } else {
      Serial.print("Erro, rc=");
      Serial.println(client.state());
      delay(1000);
    }
  }
}

void publishAlert(int sensorValue) {
  unsigned long now = millis();
  if (now - lastPublish < debounceMs) return;

  StaticJsonDocument<200> doc;
  doc["device"] = deviceId;
  doc["type"] = "som_detectado";
  doc["value"] = sensorValue;
  doc["threshold"] = threshold;
  doc["ts_ms"] = now;

  char buffer[256];
  size_t n = serializeJson(doc, buffer);

  if (client.publish(topic_alert, buffer, n)) {
    Serial.print("Publicado: ");
    Serial.println(buffer);
    lastPublish = now;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledAlerta, OUTPUT);
  pinMode(ledVibra, OUTPUT);

  connectWiFi();
  connectMQTT();
}

void loop() {
  if (!client.connected()) connectMQTT();
  client.loop();

  int value = analogRead(pinoSom);

  if (value >= threshold) {
    Serial.println(">>> SOM DETECTADO!");

    digitalWrite(ledAlerta, HIGH);
    digitalWrite(ledVibra, HIGH);

    publishAlert(value);

    delay(300);
    digitalWrite(ledAlerta, LOW);
    digitalWrite(ledVibra, LOW);
  }

  delay(50);
}
