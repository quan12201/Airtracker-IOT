from paho.mqtt import client as mqtt_client
import time
import json
import random

broker = 'broker.hivemq.com'
# broker = 'broker.emqx.io'
port = 1883
topic = 'quan/python/mqtt'
username = 'emqx'
password = 'public'
client_id = f'python-mqtt-{random.randint(0, 1000)}'


MESSAGE = {
    'id': 11,
    'packet_no': 126,
    'temperature': 30,
    'humidity': 60,
    'tds': 1100,
    'ph': 5.0,
}


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    # msg_count = 0
    # while True:
    time.sleep(1)
        # msg = f"messages: {msg_count}"
        # msg_count += 1
    msg = json.dumps(MESSAGE)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run_publish():
    client = connect_mqtt()
    client.loop_start()
    publish(client)  

run_publish()