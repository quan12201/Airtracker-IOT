import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import *
import prettytable as pt
import django
import os
import datetime
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotdashboard.settings')

django.setup()

from django.conf import settings
from django.template.loader import render_to_string
from devices.views import *

API_KEY = "6113988046:AAGOsNELuloNndmtlKVH4OKHdWbCaccmJrA"


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


if __name__ == '__main__':
    telegram_settings = settings.TELEGRAM
    updater = Updater(API_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('h', handle_message))
    bot = telegram.Bot(token=API_KEY)
    # Start the Bot
    updater.start_polling()
    # timeout=300

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    for i in range(2):
        print(i)
        bot.send_message(chat_id='-1001801209079', text=f"Thank you for using our telegram bot! We will send you notifications here!")

    updater.idle()
