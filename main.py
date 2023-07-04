import telebot
from telebot import types

bot = telebot.TeleBot('6369659318:AAGFf7v8U_ajecx17FS_5itGE16NP1HGnts')


@bot.message_handler(commands=['start'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Привет', url='https://habr.com/ru/all/')
    markup.add(btn1)
    bot.send_message(message.from_user.id, 'asdfsf', reply_markup=markup)


bot.polling(none_stop=True, interval=0)
