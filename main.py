import update as update
from telegram.ext import Updater, CommandHandler
import requests
import re


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    return contents['url']


def send_messege(bot, update):
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=get_url())


def main():
    updater = Updater('6369659318:AAGFf7v8U_ajecx17FS_5itGE16NP1HGnts')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('send_message', send_messege))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
