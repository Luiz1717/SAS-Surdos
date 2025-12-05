# Emulador de Atuadores – SAS-Surdos

import json
from paho.mqtt import client as mqtt_client

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "surdos/esp32/eventos"
CLIENT_ID = "actuator_01"

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    level = data.get("nivel", 0)
    print("[ACT] Evento:", data)
    if level > 1400:
        print("[ACT] LED VERMELHO ON / VIBRAÇÃO ON")
    else:
        print("[ACT] Sem alerta.")

def main():
    client = mqtt_client.Client(CLIENT_ID)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC)
    print("[ACT] Emulador pronto.")
    client.loop_forever()

if __name__ == "__main__":
    main()
