/*
  ESP32 SAS-Surdos – Wokwi Simulation Version
  Detecta som e aciona LED vermelho + LED amarelo (vibração simulada)
*/
int soundPin = 34;
int ledAlerta = 2;
int ledVibra = 4;
int threshold = 1800;

void setup() {
  Serial.begin(115200);
  pinMode(ledAlerta, OUTPUT);
  pinMode(ledVibra, OUTPUT);
}

void loop() {
  int value = analogRead(soundPin);
  Serial.print("Som: ");
  Serial.println(value);

  if (value >= threshold) {
    Serial.println(">>> SOM DETECTADO! ALERTA ATIVADO!");
    digitalWrite(ledAlerta, HIGH);
    digitalWrite(ledVibra, HIGH);
    delay(400);
    digitalWrite(ledAlerta, LOW);
    digitalWrite(ledVibra, LOW);
  }

  delay(50);
}
