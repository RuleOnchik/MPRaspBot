import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import datetime
import random
import time
import os
import sys

sys.path.append('C:\\Users\\truel\\AppData\\Local\\Programs\\Python')

# from MyMods.ERP import ShablonReply as sr
# from MyMods.ERP import SimpleFunks as smf
from MyMods.ERP import SimpleParams as smp
# from MyMods.ERP import AnalysePack as ap
from MyMods.ERP import SeleniumPack as sp

import raspisanie


def sender(id, text, keyboard=None):
    post = {'chat_id' : id, 'message' : text, 'random_id' : 0}
    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    bot.method('messages.send', post)

def keyboard_start():
    keyboard = VkKeyboard()
    keyboard.add_button('/Сейчас', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Расписание', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Цитата волка', VkKeyboardColor.PRIMARY)
    # keyboard.add_line()
    return keyboard

def keyboard_weekdays():
    keyboard = VkKeyboard()
    keyboard = VkKeyboard()
    keyboard.add_button('/Понедельник', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Вторник', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Среда', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('/Четверг', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Пятница', VkKeyboardColor.PRIMARY)
    keyboard.add_button('/Суббота', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('/Назад', VkKeyboardColor.NEGATIVE)

    return keyboard

Token = '53a987c023bf8f643b9504614a8241fc1269160637a7e1e836a544483383344de8f9390e66982d77b8bde'

bot = vk_api.VkApi(token = Token)
longpoll = VkLongPoll(bot)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            message = event.text.casefold()
            id = event.chat_id
            print(id, "|", message)

            if message == "начать":
                answer_text = f"Привет!\nВыбери что тебе нужно из списка и тогда поговорим дальше)\n\nЕсли ты впервый раз, то обязательно сначала задай группу!\nДля этого напиши\n\n /Группа: XXX-XXX\n\nгде XXX-XXX - номер группы"
                sender(id, answer_text, keyboard_start())
                continue

            if "/группа:" in message:
                answer_text = raspisanie.make_log_json(message[1:], id, "Vkontakte")
                sender(id, answer_text)
                continue

            if message == "/stop":
                exit()

            if '[club210995972|@raspisaniegroup201341]' in message:
                message = message.split('[club210995972|@raspisaniegroup201341]')[1].strip()
                # print(message)

                if message == "/сейчас":
                    try:
                        answer_text, link = raspisanie.now_schedule(id, "Vkontakte")
                    except Exception as error:
                        answer_text = str(error)
                        link = None

                    if link:
                        inline_keyboard = VkKeyboard(inline=True)
                        inline_keyboard.add_openlink_button(f'{link[0]}',f'{link[1]}')
                    else:
                        inline_keyboard = None
                    sender(id, answer_text, inline_keyboard)
                    continue

                if message == "/расписание":
                    answer_text = "Какой день интересует?)"
                    sender(id, answer_text, keyboard_weekdays())
                    continue

                if message == "/назад":
                    answer_text = "Назад"
                    sender(id, answer_text, keyboard_start())
                    continue

                if message in ["/понедельник", "/вторник", "/среда", "/четверг", "/пятница", "/суббота"]:

                    try:
                        answer_text, links = raspisanie.day_schedule(message[1:], id, "Vkontakte")
                    except Exception as error:
                        answer_text = str(error)
                        links = None

                    if links:
                        inline_keyboard = VkKeyboard(inline=True)
                        len_links = len(links)
                        for text, link in links:
                            len_links = len_links - 1
                            inline_keyboard.add_openlink_button(f'{text}',f'{link}')
                            if len_links: inline_keyboard.add_line()
                    else:
                        inline_keyboard = None
                    sender(id, answer_text, inline_keyboard)
                    continue

                if message == "/цитата волка":
                    with open('Citati.txt', 'r', encoding='utf-8') as f:
                        citati = f.read().split(f"\n")
                        f.close()
                    r = random.randint(0, len(citati)-1)
                    answer_text = f"Цитата №{r+1}\n"+citati[r]
                    sender(id, answer_text)
                    continue
