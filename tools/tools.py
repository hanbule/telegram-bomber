import datetime
import inspect
import os
import random
import sys

import pytz
from aiogram import types

from tools import config


def generate_progressbar(j: int, z: int):
    """ z - полное, j - скока выполнено"""
    prop = round(j * 100 / z)
    done = round(20 / 100 * prop)
    return ('▓' * done) + ('░' * (20 - done)) + ' (' + str(prop) + '%)'


def format_rus_number(number: str) -> str:
    num = list(number)
    if num[0] == "8":
        num.remove("8")
        num.insert(0, "+7")
    return "".join(num)


def get_time():
    return int(datetime.datetime.now(pytz.timezone(
        'Europe/Moscow'
    )).timestamp())


def get_formatted_time():
    return datetime.datetime.now(pytz.timezone(
        'Europe/Moscow'
    )).strftime("%H:%M:%S MSK")


def remove_non_ASCII(text):
    rus = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮiq'
    otpt_str = str()
    text = text.replace('ё', 'е').replace('Ё', 'Е')

    for i in text:
        num = ord(i)
        if num >= 0 or i in rus:
            if num <= 127 or i in rus:
                otpt_str = otpt_str + i

    return otpt_str


def get_full_number(code: int, phone: int):
    return int("{}{}".format(
        code,
        phone
    ))


def escape_html(text: str):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", str()).replace('"', str())


def get_full_name(message: (types.Message, types.callback_query)):
    name = str(message['from']['first_name'])
    try:
        name += ' ' + message['from']['last_name']
    except TypeError:
        pass

    name_list = list()

    for a in name.split():
        if str(a).startswith('#') or str(a).startswith('$'):
            continue
        else:
            name_list.append(a)

    if message.from_user.username == 'rivenhals':
        return 'Говночлен (Керил)'
    elif message.from_user.username == 'm4x3r1337':
        return 'Миксер'
    elif message.from_user.username == config.support:
        return 'Тех. Поддержка'
    elif message.from_user.username == 'gridnefff':
        return 'Гриднев кинь кота...'

    return escape_html(
        remove_non_ASCII(
            " ".join(name_list)
        ).replace('<', str()).replace(
            '>', str()
        ).replace('ульба', 'Лучший мальчик на свете!').replace(
            'kai', 'gay'
        ).replace('kei', 'gay'))


def load_services():
    services = os.listdir("services")
    sys.path.insert(0, "services")
    service_classes = {}

    for serv in services:
        if serv.endswith(".py") and serv != "service.py":
            module = __import__(serv[:-3])
            for member in inspect.getmembers(module, inspect.isclass):
                if member[1].__module__ == module.__name__:
                    service_classes[module] = member[0]
    return service_classes


def generate_key(length: int):
    symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
               'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
               'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z',
               'x', 'c', 'v', 'b', 'n', 'm', 'Q', 'W', 'E', 'R',
               'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F',
               'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B',
               'N', 'M']

    return str().join([random.choice(symbols) for _ in range(length)])
