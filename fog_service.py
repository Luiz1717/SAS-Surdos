# fog_service.py
import json
import time
import sqlite3
import requests
import logging
from paho.mqtt import client as mqtt

# CONFIG
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "sas_surdos/alerta"
CLIENT_ID = "fog_service_1"

# FIREBASE REALTIME DATABASE
CLOUD_ENDPOINT = "https://sas-surdos-default-rtdb.firebaseio.com/alerts.json"

DB_FILE = "fog_alerts.db"
LOG_FORMAT = "%(asctime)s %(levelname)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# DB: criar tabela
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            payload TEXT,
            received_ts INTEGER,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_alert(device, payload):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('INSERT INTO alerts (device, payload, received_ts, sent) VALUES (?, ?, ?, 0)',
                (device, json.dumps(payload), int(time.time()*1000)))
    conn.commit()
    conn.close()

def send_to_cloud(payload):
    try:
        r = requests.post(CLOUD_ENDPOINT, json=payload, timeout=10)
        r.raise_for_status()
        logging.info("Enviado para Firebase! Código: %s", r.status_code)
        return True
    except Exception as e:
        logging.error("Erro ao enviar para Firebase: %s", e)
        return False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Conectado ao MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error("Falha ao conectar MQTT, rc=%s", rc)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except:
        logging.error("Payload inválido: %s", msg.payload)
        return

    device = payload.get("device", "unknown")
    logging.info("Alerta recebido de %s: %s", device, payload)

    save_alert(device, payload)

    ok = send_to_cloud(payload)
    if not ok:
        logging.info("Guardado para retry posterior.")

def retry_unsent():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, payload FROM alerts WHERE sent = 0 ORDER BY id LIMIT 10')
    rows = cur.fetchall()
    for row in rows:
        rid, payload_json = row
        payload = json.loads(payload_json)
        if send_to_cloud(payload):
            cur.execute('UPDATE alerts SET sent = 1 WHERE id = ?', (rid,))
            conn.commit()
    conn.close()

def main():
    init_db()
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            retry_unsent()
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Encerrando fog service...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

