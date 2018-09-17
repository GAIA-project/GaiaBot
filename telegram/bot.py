#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from sparkworks import SparkWorks
import datetime
import os
import redis

r = redis.StrictRedis(host='redis', port=6379, db=0)

token = os.environ['TELEGRAM_BOT_TOKEN']

s = SparkWorks(os.environ['SPARKS_CLIENT'], os.environ['SPARKS_SECRET'])
s.connect(os.environ['SPARKS_USERNAME'], os.environ['SPARKS_PASSWORD'])

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

helpText = "Ask question for the school's data like the following:\n" \
           "What is the temperature in the school?\n" \
           "What is the power consumption of the school building?\n\n" \
           "You can also use simplified quick commands like 'temperature' or 'power'."

locations = {'location-1': {'name': 'Greece',
                            'schools': [{'id': 19640, 'name': "Γυμνάσιο Πενταβρύσου Καστοριάς"},
                                        {'id': 156886, 'name': "1ο Επαγγελματικό Λύκειο Πατρών"},
                                        {'id': 623592, 'name': "2ο Δημοτικό Σχολείο Παραλίας Πατρών "},
                                        {'id': 27827, 'name': "8ο Γυμνάσιο Πατρών"},
                                        {'id': 506265, 'name': "1o Δημοτικό Σχολείο Ψυχικού Αττικής"},
                                        {'id': 510924, 'name': "2o Γυμνάσιο Ν. Ιωνίας"},
                                        {'id': 141587, 'name': "1o Γυμνάσιο Ραφήνας"},
                                        {'id': 205623, 'name': "Δημοτικό Σχολείο Φιλοθέης"},
                                        {'id': 144024, 'name': "Δημοτικό Σχολείο Λυγιάς"},
                                        {'id': 155851, 'name': "5ο Δημοτικό Σχολείο Νέας Σμύρνης"},
                                        {'id': 157185, 'name': "Ελληνογερμανική Αγωγή"},
                                        {'id': 144242, 'name': "1ο Γυμνάσιο Ν. Φιλαδέλφειας"},
                                        {'id': 510923, 'name': "3o ΓΕΛ Ν. Φιλαδέλφειας"},
                                        {'id': 141611, 'name': "Πειραματικό Γυμνάσιο Πατρών"},
                                        {'id': 155877, 'name': "2ο Δημοτικό Σχολείο Παραλίας Πατρών"},
                                        {'id': 155849, 'name': "6ο Δημοτικό Σχολείο Καισαριανής"},
                                        {'id': 155865, 'name': "46ο Δημοτικό Σχολείο Πατρών"},
                                        {'id': 144243, 'name': "Δημοτικό Σχολείο Μεγίστης"},
                                        {'id': 157089, 'name': "1ο Εργαστηριακό Κέντρο Πατρών"}]},
             'location-2': {'name': 'Sweden', 'schools': [{'id': 159705, 'name': "Soderhamn"}, ]},
             'location-3': {'name': 'Italy',
                            'schools': [{'id': 155076, 'name': "Gramsci-Keynes School"},
                                        {'id': 155077, 'name': "Sapienza"}]}}

schoolNames = []
for item in locations['location-1']['schools']:
    schoolNames.append(item)
for item in locations['location-2']['schools']:
    schoolNames.append(item)
for item in locations['location-3']['schools']:
    schoolNames.append(item)


def getSchoolStrId(id):
    return id.replace('school-', '')


def getSchoolIntId(id):
    return int(getSchoolStrId(id))


def getSchoolNameFromId(id):
    return [item for item in schoolNames if item["id"] == getSchoolIntId(id)][0]["name"]


def start(bot, update):
    keyboard = []
    for key in locations:
        keyboard.append([InlineKeyboardButton(locations[key]['name'], callback_data=key)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose your country:', reply_markup=reply_markup)


def saveDB(userId, schoolId):
    r.set(str(userId), schoolId)


def getSchoolFromDB(userId):
    return r.get(str(userId))


def button(bot, update):
    query = update.callback_query
    logger.info(update)

    if query.data.startswith('location'):
        keyboard = []
        for school in locations[query.data]['schools']:
            keyboard.append([InlineKeyboardButton(school['name'], callback_data='school-' + str(school['id']))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="Please choose your school: ".format(query.data),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        bot.edit_message_reply_markup(reply_markup=reply_markup,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
    elif query.data.startswith('school'):
        bot.edit_message_text(text="Selected {}".format(getSchoolNameFromId(query.data) + "\n" + helpText),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        logger.info(type(update.callback_query))
        logger.info(update.callback_query.from_user)
        userId = int(update.callback_query.from_user.id)
        schoolId = str(query.data)
        saveDB(userId, schoolId)


def help(bot, update):
    update.message.reply_text("Use /start to select your school.\n" + helpText)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def handle_message(bot, update):
    userId = str(update.message.from_user.id)
    logger.info(userId)
    schooId = getSchoolFromDB(userId)
    text = ""
    message = update.message.text.lower().split(" ")

    if 'temperature' in message:
        bot.send_message(chat_id=update.message.chat_id, text="Retrieving data...")
        latest = s.latest(s.resource("site-" + getSchoolStrId(schooId) + "/Temperature"))
        text = "Last Update: %s\n" % (datetime.datetime.fromtimestamp(latest['latestTime'] / 1000))
        text += "Latest value: %.2f %s\n" % (latest['latest'], latest["uom"])
        text += "Daily aggregate: %.2f %s\n" % (latest['latestDay'], latest["uom"])
    elif 'power' in message or 'energy' in message:
        bot.send_message(chat_id=update.message.chat_id, text="Retrieving data...")
        latest = s.latest(s.resource("site-" + getSchoolStrId(schooId) + "/Calculated Power Consumption"))
        text = "Last Update: %s\n" % (datetime.datetime.fromtimestamp(latest['latestTime'] / 1000))
        if latest["uom"] == 'mWh':
            text += "Latest value: %.2f %s\n" % (latest['latest'] / 1000, 'Wh')
            text += "Daily aggregate: %.2f %s\n" % (latest['latestDay'] / 1000000, 'kWh')
        else:
            text += "Latest value: %.2f %s\n" % (latest['latest'], latest["uom"])
            text += "Daily aggregate: %.2f %s\n" % (latest['latestDay'], latest["uom"])
    bot.send_message(chat_id=update.message.chat_id, text=text)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
