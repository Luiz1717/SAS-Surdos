# Simulador de eventos MQTT – SAS-Surdos

import time, json, random
from paho.mqtt import client as mqtt_client

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "surdos/esp32/eventos"
CLIENT_ID = "simulator_01"

def make_payload(level):
    return json.dumps({"tipo":"som","nivel":level,"timestamp":int(time.time()*1000)})

def main():
    client = mqtt_client.Client(CLIENT_ID)
    client.connect(BROKER, PORT)
    client.loop_start()
    print("[SIM] Publicando eventos...")
    try:
        while True:
            base = random.randint(200,600)
            spike = random.choice([0, random.randint(1500,3000)])
            level = max(base, spike)
            payload = make_payload(level)
            client.publish(TOPIC, payload)
            print("[SIM] Enviado:", payload)
            time.sleep(1)
    except KeyboardInterrupt:
        client.loop_stop()

if __name__ == "__main__":
    main()
