import os
import telebot
import Scheduler

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Добро пожаловать в бота расписаний.')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    scheduler = Scheduler.Scheduler(os.environ['USER_LOGIN'], os.environ['USER_PASSWORD'])
    schedule = scheduler.get_by_group(message.text)
    if schedule:
        bot.reply_to(message, schedule)
    else:
        bot.reply_to(message, 'Нет такой группы или нет расписания у данной группы')

bot.polling()
