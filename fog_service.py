# Fog Service – SAS-Surdos
# Recebe MQTT, valida evento e registra no Firebase (opcional)

import os, json, time, requests
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv

load_dotenv()

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "surdos/esp32/eventos"
CLIENT_ID = "fog_service_01"

FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL", "")
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET", "")

def firebase_push(event):
    if not FIREBASE_DB_URL:
        print("Firebase não configurado. Pulando.")
        return
    url = FIREBASE_DB_URL.rstrip("/") + "/events.json"
    r = requests.post(url, params={"auth": FIREBASE_SECRET}, json=event)
    print("Firebase resposta:", r.status_code, r.text)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("[FOG] Evento recebido:", data)
        firebase_push(data)
    except Exception as e:
        print("Erro:", e)

def main():
    client = mqtt_client.Client(CLIENT_ID)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC)
    print("[FOG] Conectado. Aguardando eventos...")
    client.loop_forever()


print("DEBUG Firebase URL:", FIREBASE_DB_URL)


if __name__ == "__main__":
    main()
