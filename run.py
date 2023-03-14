import random
import time
import django

from paho.mqtt import client as mqtt_client

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import *
import prettytable as pt
import datetime
from datetime import date

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotdashboard.settings')

django.setup()

from datas.models import Data
from devices.models import Device
from django.conf import settings
from django.template.loader import render_to_string
from devices.views import *


broker = 'broker.hivemq.com'
port = 1883
# topic = "quan/python/mqtt"
topic = 'mq135'
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

API_KEY = "6113988046:AAGOsNELuloNndmtlKVH4OKHdWbCaccmJrA"

telegram_settings = settings.TELEGRAM
bot = telegram.Bot(token=API_KEY)


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
                # Data.objects.create(device=device, 
                #                     field_1=sub_lst[1], 
                #                     field_2=sub_lst[2], 
                #                     field_3=sub_lst[3],
                #                     field_4=sub_lst[4], 
                #                     field_5=sub_lst[5], 
                #                     field_6=sub_lst[6],
                #                     remote_address='127.0.0.1'
                #                     )
                bot.send_message(chat_id='-1001801209079', text=sub_lst)
                
            sub_lst.clear()
        else:
            sub_lst.append(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    print(chat_id)
    context.bot.send_message(chat_id=chat_id,
            text=f"Thank you for using our telegram bot! We will send you notifications here!")
    

def message(field_name, procedure, dt, numberlimit):
    message = 'Date: ' + str(dt)
    tb = pt.PrettyTable()
    tb.field_names = field_name
    data = [19.323,12112.12,12.121]
    for x in data:
        tb.add_row(x)
    message += f'<pre>{tb}</pre>'
    return message


def load_data(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    try:
        date_day = int(context.args[0])
        dt = date(datetime.today().year, datetime.today().month, date_day)
        if dt > datetime.today().date():
            dt = date(datetime.today().year if datetime.today().month - 1 > 0 else datetime.today().year - 1, datetime.today().month - 1 if datetime.today().month - 1 > 0 else 12, date_day)
    except ValueError:
        try:
            dt = date.fromisoformat(context.args[0])
        except IndexError:
            dt = datetime.today()
    except IndexError:
        dt = datetime.today()
    print(update['message']['chat']['username'], dt, datetime.now())
    try:
        numberlimit = int(context.args[1])
    except (IndexError, ValueError):
        numberlimit = 10
    return (dt, numberlimit)


def send_table(message_html, channel):
    bot = telegram.Bot(token=API_KEY)
    bot.send_message(chat_id="@%s" % channel,
                     text=message_html, parse_mode=telegram.ParseMode.HTML)
    return 1


def send_table(message_html, update: Update):
    update.channel_post.reply_text(text=message_html, parse_mode=telegram.ParseMode.HTML)
    return 1


def handle_message(update, context):
    print(update, context.args)
    if update.message is not None:
        text = str(update.message.text).lower()
        update.message.reply_text(f"Hi, {update['message']['chat']['first_name']}. Thank you for using our telegram bot! We will send you notifications here!")
    else:
        if update.channel_post.text.startswith("/"):
            args = update.channel_post.text.split(" ")


def run():
    client = connect_mqtt()
    # client.loop_start()

    client = connect_mqtt()


    # updater = Updater(API_KEY)
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('h', handle_message))
    print(0)
    # Start the Bot
    # updater.start_polling()
    # timeout=300
    print(1)
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    subscribe(client, [])

    # updater.idle()

    client.loop_forever()


# test()
run()