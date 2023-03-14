import random
import time
import django

from paho.mqtt import client as mqtt_client

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotdashboard.settings')

django.setup()

from datas.models import Data
from devices.models import Device


broker = 'broker.hivemq.com'
port = 1883
# topic = "quan/python/mqtt"
topic = 'mq135'
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# lst = []


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, sub_lst: list):
    def on_message(client, userdata, msg):
        print(f"Received {msg.payload.decode()} from {msg.topic} topic")
        if msg.payload.decode() == 'mq135':
            print(sub_lst)
            if len(sub_lst) == 7:
                device = Device.objects.get(id=int(sub_lst[0]))
                Data.objects.create(device=device, 
                                    field_1=sub_lst[1], 
                                    field_2=sub_lst[2], 
                                    field_3=sub_lst[3],
                                    field_4=sub_lst[4], 
                                    field_5=sub_lst[5], 
                                    field_6=sub_lst[6],
                                    remote_address='127.0.0.1'
                                    )
            sub_lst.clear()
        else:
            sub_lst.append(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    # client.loop_start()
    subscribe(client, [])
    client.loop_forever()




run()