import requests
from bs4 import BeautifulSoup as BS
import telebot as tb
from telebot import types
import json
import hashlib
from lxml import etree
import threading
from apscheduler.schedulers.blocking import BlockingScheduler
import time

def read_data(file_name):
  with open(file_name, 'r', encoding="utf-8") as file:
    return json.load(file)

def write_data(data, file_name):
  with open(file_name, 'w', encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

def get_keyword(url, path, headers={}):
  r = requests.get(url=url, headers=headers)
  json_data = r.json()
  for i in path:
    json_data = json_data[i]
  return json_data

def get_update(data, hash):
  update = data["SCHEDULE"][hash]
  try:
    keyword = get_keyword(update["URL"], update["PATH"], data["HEADERS"])
    if keyword != update["KEYWORD"]:
      bot.send_message(update["USER"], f'Что-то новое с "{update["NAME"]}"\n{update["URL"]}')
      data["SCHEDULE"][hash]["KEYWORD"] = keyword
      write_data(data, "data.json")
  except:
    pass

data = read_data("data.json")

bot = tb.TeleBot(data["TOKEN"])

Stage1 = "Придумайте название для отслеживания:"
Stage2 = "Отлично! Теперь через пробел введите URL сайта для отслежки и полный XPATH до нужного текста"
Stage3 = "Осталось немного! Теперь выберите то, как часто бот будет проверятся значение"
Stage4 = "Ваша проверка полностью готова! Полный список проверок вы сможете посмотреть, если я не забуду написать для этого код ;)"
URLError = "Текст или Веб-сайт не был найден :( Попробуйте проверить URL и XPATH и повторить попытку позже"
GeneralError = "Что-то пошло не так :( Повторите попытку позже"
Start = "Данные были успешно записаны"

@bot.message_handler(commands=['start', 'help'])
def start(chat):
  print(chat.chat.id)
  data = read_data("data.json")
  if chat.chat.id not in data["USERS"]:
    data["USERS"][chat.chat.id] = {"STAGE": 0, "CURRENT": None}
    bot.send_photo(chat.chat.id, "https://gachi.gay/b113o")
    write_data(data, "data.json")

  bot.send_message(chat.chat.id, Start)

@bot.message_handler(commands=['newschedule'])
def newschedule(chat):
  data = read_data("data.json")
  if chat.chat.id not in data["USERS"]:
    data["USERS"][chat.chat.id] = {"STAGE":1, "CURRENT":{}}
  bot.send_message(chat.chat.id, Stage1)

@bot.message_handler()
def mess(chat):
  try:
    data = read_data("data.json")
    if chat.chat.id not in data["USERS"]:
      data["USERS"][chat.chat.id] = {"STAGE": 0, "CURRENT": None}
    if data["USERS"][chat.chat.id]["STAGE"] == 0:
      bot.send_message(chat.chat.id, GeneralError)
    if data["USERS"][chat.chat.id]["STAGE"] == 1:
      data["USERS"][chat.chat.id]["CURRENT"]["NAME"] = chat.chat.text
      bot.send_message(chat.chat.id, Stage2)
      data["USERS"][chat.chat.id]["STAGE"] = 2
    if data["USERS"][chat.chat.id]["STAGE"] == 2:
      text = chat.chat.text.split()
      data["USERS"][chat.chat.id]["CURRENT"]["URL"] = text[0]
      data["USERS"][chat.chat.id]["CURRENT"]["XPATH"] = text[1]

      bot.send_message(chat.chat.id, Stage3)
      data["USERS"][chat.chat.id]["STAGE"] = 3

    # if chat.reply_to_message.text == 'Напишите текст...':
    #   bot.delete_message(chat.chat.id, chat.message_id)
    #
    #   markup = types.InlineKeyboardMarkup()
    #   btn1 = types.InlineKeyboardButton('сменить текст', callback_data='change_text1')
    #   btn2 = types.InlineKeyboardButton('делать ничего', callback_data='do_nothing')
    #   markup.row(btn1, btn2)
    #   bot.edit_message_text(chat.text, chat.chat.id, chat.reply_to_message.message_id, reply_markup=markup)
    #
    # else:
    #   bot.send_message(chat.chat.id, 'ок')
  except:
    pass


@bot.callback_query_handler(func=lambda callback: True)
def callback_chat(callback):
  if callback.data == 'change_text1':
    bot.edit_message_text('Напишите текст...', callback.message.chat.id, callback.message.message_id)
  elif callback.data == 'do_nothing':
    bot.delete_message(callback.message.chat.id, callback.message.reply_to_message.message_id)
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    bot.send_message(callback.message.chat.id, 'ок')

def parse():
  data = read_data("data.json")
  jobs = data["SCHEDULE"]
  print(jobs)
  scheduler = BlockingScheduler()
  for i in jobs:
    print(i)
    scheduler.add_job(get_update, 'interval', minutes=jobs[i]["COOLDOWN"], args=[data, i])
    bot.send_message(jobs[i]["USER"], f'Проверка по вашему протоколу "{jobs[i]["NAME"]}" пошла и пудет проводится каждые {jobs[i]["COOLDOWN"]} мин.')
    bot.send_photo(jobs[i]["USER"], "https://gachi.gay/guEKw")
    bot.send_message(661768940,
                     f'Проверка по вашему протоколу "{jobs[i]["NAME"]}" пошла и пудет проводится каждые {jobs[i]["COOLDOWN"]} мин.')
    bot.send_photo(661768940, "https://gachi.gay/guEKw")
  scheduler.start()
  while 1:
    time.sleep(5)
    for i in data["SCHEDULE"]:
      if i not in jobs:
        jobs = data["SCHEDULE"]
        scheduler.add_job(get_update, 'interval', minutes=jobs[i]["COOLDOWN"], args=[data, i])

def main():
  # print(get_keyword("https://back.genotek.ru/api/price/", ["premium", "/full-genome/", "price"], data["HEADERS"]))
  # pass

  parsingThread = threading.Thread(parse())
  parsingThread.start()

  pollingThread = threading.Thread(bot.polling(none_stop=True))
  pollingThread.start()





if __name__ == "__main__":
  main()