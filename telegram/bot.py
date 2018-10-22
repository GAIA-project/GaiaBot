#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import datetime
import logging
import os

import redis
from sparkworks import SparkWorks
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import utils

r = redis.StrictRedis(host='redis', port=6379, db=0)

token = os.environ['TELEGRAM_BOT_TOKEN']

s = SparkWorks(os.environ['SPARKS_CLIENT'], os.environ['SPARKS_SECRET'])
s.connect(os.environ['SPARKS_USERNAME'], os.environ['SPARKS_PASSWORD'])

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

helpText = "List the school's measured properties using the 'list' command.\n" \
           "Show the currently selected school using the 'school' command.\n" \
           "Ask a question for the school's data by typing the property's name.\n" \
           "You can also ask questions for the school's data like the following:\n" \
           "What is the temperature in the school?\n" \
           "What is the power consumption of the school building?\n\n"

phenomena = s.phenomena()


def start(bot, update):
    keyboard = []
    for key in utils.locations:
        keyboard.append([InlineKeyboardButton(utils.locations[key]['name'], callback_data=key)])
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
        for school in utils.locations[query.data]['schools']:
            keyboard.append([InlineKeyboardButton(school['name'], callback_data='school-' + school['uuid'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="Please choose your school: ".format(query.data),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        bot.edit_message_reply_markup(reply_markup=reply_markup,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
    elif query.data.startswith('school'):
        bot.edit_message_text(text="Selected {}".format(utils.getSchoolNameFromId(query.data) + "\n" + helpText),
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
    message = update.message.text.lower().split(" ")
    messageParts = []
    for messagePart in message:
        messageParts.append(messagePart.encode('ascii', 'ignore'))
    properties = utils.getSiteProperties(s, utils.getSchoolStrId(schooId))

    if "list" in messageParts:
        text = "Sensed properties: \n"
        props = []
        for property in properties:
            props.append(property['property'].title())
        for property in sorted(set(props)):
            text += "- %s\n" % (property)
    elif "school" in messageParts:
        text = "Current School: \n"
        text += "- %s\n" % (utils.getSchoolNameFromId(schooId).title())
    else:
        resource = utils.findResource(properties, messageParts)
        logger.info('Requested "%s" returned "%s"', message, resource)
        if resource is not None:
            text = ""
            bot.send_message(chat_id=update.message.chat_id,
                             text="Retrieving data for %s..." % (utils.getSchoolNameFromId(schooId).title()))
            resource_uuid = resource['resourceUuid']
            latest = s.latest(resource_uuid)
            divi1 = 1
            divi2 = 1
            try:
                uom1 = latest['uom']
                uom2 = latest['uom']
                if 'power' in message:
                    divi1 = 1000
                    uom1 = "Wh"
                    divi2 = 1000000
                    uom2 = "kWh"
                text += "Property: %s\n" % (resource['property'])
                text += "Last Update: %s\n" % (datetime.datetime.fromtimestamp(latest['latestTime'] / 1000))
                text += "Latest value: %.2f %s\n" % (latest['latest'] / divi1, uom1)
                text += "Daily aggregate: %.2f %s\n" % (latest['latestDay'] / divi2, uom2)
            except KeyError:
                exit(0)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Such data are not available.")
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
