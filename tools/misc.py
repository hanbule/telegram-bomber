import asyncio
import datetime
import json
import os

import phonenumbers
import requests
from aiogram import Bot, Dispatcher, types
from phonenumbers import carrier
from bs4 import BeautifulSoup as bs

import __main__
from handlers import trial_mailing
from tools import config, tools
from tools import database

# Initialization of the executable folder
PATH = os.path.dirname(os.path.abspath(__main__.__file__))

proxy_status = False
ip = str()
proxy_country = str()
latest_trial_mailing = datetime.datetime.timestamp(datetime.datetime.now())


def logger(title: str, message: str):
    for line in message.splitlines():
        print(f'[{tools.get_formatted_time()}] [{title}] {line}')

        with open(PATH + '/latest.log', 'a') as f:
            f.write(f'[{tools.get_formatted_time()}] [{title}] {line}\n')


logger('Bot', 'Starting...')
gays = list()


def telegram_api_connector():
    global ip
    global proxy_status
    global proxy_country

    try:
        proxy_status = requests.get('https://telegram.org').status_code != 200

    except (BaseException, Exception):
        proxy_status = True

    if not proxy_status:
        ip = requests.get('https://ip.beget.ru/').text
        proxy_country = requests.get(
            f'http://www.geoplugin.net/json.gp?{ip}', timeout=5
        ).json()['geoplugin_countryCode']

        logger('Connector', 'Started without proxy!')

        return Bot(token=config.bot_token)

    else:
        ip = requests.get('https://ip.beget.ru/',
                          proxies=dict(http=config.proxy,
                                       https=config.proxy)).text
        proxy_country = requests.get(
            f'http://www.geoplugin.net/json.gp?{ip}', timeout=5
        ).json()['geoplugin_countryCode']

        logger('Connector', 'Started with proxy!')

        return Bot(token=config.bot_token,
                   proxy=config.proxy)


async def startup_task(dispatcher):
    str(dispatcher)
    admins = database.get_users()["admin_ids"]
    me = await bot.get_me()
    logger('Bot', f'Started on {me["first_name"]} (@{me["username"]}) with id {me["id"]}')

    for admin in admins:
        try:
            await bot.send_message(int(admin),
                                   f'Started on {me["first_name"]} (@{me["username"]}) with id {me["id"]}')
        except (BaseException, Exception):
            pass


async def thinker(message: types.Message):
    global latest_trial_mailing

    if message.from_user.id not in database.get_users()['telegram_ids']:
        logger('Thinker', f'{tools.get_full_name(message)} with id {message.from_user.id} '
                          f'registered')
        database.create_user(
            message.from_user.id, tools.get_full_name(message), message.from_user.username, tools.get_time()
        )

    logger('Message', f'{tools.get_full_name(message)} with id {message.from_user.id} '
                      f'send message {message.text}')

    if datetime.datetime.timestamp(datetime.datetime.now()) - latest_trial_mailing > 125000:
        latest_trial_mailing = datetime.datetime.timestamp(datetime.datetime.now())
        trial_mailing.start_mailing(database.get_users()['trial_ids'])

    if database.get_user(message.from_user.id)['ban_status'] and message.from_user.id in gays:
        return

    if database.get_user(message.from_user.id)['ban_status'] and message.from_user.id not in gays:
        gays.append(message.from_user.id)
        await message.reply(f'Вы были заблокированы. Для '
                            f'разблокировки, пожалуйста, '
                            f'обратитесь в тех. поддержку (@{config.support}). '
                            f'Ваш персональный код - <b>{message.from_user.id}</b>', parse_mode='html')
        return False

    if message.from_user.username != database.get_user(message.from_user.id)['user_name']:
        logger('Updater', f'{tools.get_full_name(message)} with id {message.from_user.id} '
                          f'update username {message.from_user.username}')
        database.update_user(
            message.from_user.id, tools.get_full_name(message), message.from_user.username
        )

    if tools.get_full_name(message) != database.get_user(message.from_user.id)['full_name']:
        logger('Updater', f'{tools.get_full_name(message)} with id {message.from_user.id} '
                          f'update fullname {tools.get_full_name(message)}')
        database.update_user(
            message.from_user.id, tools.get_full_name(message), message.from_user.username
        )

    return True


async def admin_thinker(message: types.Message):
    user_name = message.from_user.username
    if user_name in config.creators or user_name == config.support:
        return True

    else:
        text = 'Номер <b>недействителен</b>. ' \
               'Для получения информации об ' \
               'использовании бота, пожалуйста, ' \
               'используйте <b>помощь.</b>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        await message.delete()
        return False


def get_contact(number: int):
    num_name = []
    phone_ow = requests.get(f'https://phonebook.space/?number=%2B{number}').text
    content = bs(phone_ow, 'html.parser').find('div', class_='results')
    for i in content.find_all('li'):
        num_name.append(i.text.strip())

    if len(num_name) < 1:
        int('a')

    return num_name[-1]


def check_bomber(message: (types.message, str), default_cycles: int):
    if type(message) == str:
        text = message
    else:
        text = message.text
    try:
        raw_number = text.split(',')[0]

        if raw_number[0] == "8":
            raw_number = tools.format_rus_number(raw_number)

        phone = f'+{raw_number.replace("+", "")}'
        phone = phonenumbers.parse(phone, None)

    except (ValueError,
            IndexError,
            phonenumbers.phonenumberutil.NumberParseException):
        return False

    if not phonenumbers.is_valid_number(phone):
        return False

    try:
        cycles = int(text.split(',', maxsplit=1)[1])

    except (ValueError, IndexError):
        cycles = default_cycles

    code = int(phone.country_code)
    number = int(phone.national_number)
    formatted_phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    try:
        formatted_title = get_contact(int(f'{code}{number}')) + ' (' + formatted_phone + ')'
    except (Exception, BaseException):
        formatted_title = formatted_phone

    request = json.loads(
        requests.get(
            f'http://rosreestr.subnets.ru/?get=num&format=json&num=7{number}'
        ).text
    ) if code == 7 else dict()

    try:
        operator = request['0']['operator'] if code == 7 else carrier.name_for_number(phone, "en")
    except KeyError:
        operator = carrier.name_for_number(phone, "en")

    try:
        operator = request['0']['moved2operator']
    except KeyError:
        pass

    country = 'Россия' if code == 7 else 'Украина' if code == 380 else 'Беларусь' if code == 375 else 'Неизвестно'

    try:
        region = request['0']['region'] if code == 7 else 'Неизвестно'
    except KeyError:
        region = 'Неизвестно'

    if not operator:
        operator = 'Неизвестно'
    else:
        if operator == "MTS" and country == "Беларусь":
            operator += " BY"
        elif operator == "MTS" and country == "Украина":
            operator += " UKR"
        elif (operator == "MTS" or operator == "МТС") and country == "Россия":
            operator += " RUS" if operator == "MTS" else " РУС"

    attack_id = tools.generate_key(16)

    return {"attack_id": attack_id,
            "code": code,
            "number": number,
            "formatted": formatted_phone,
            "formatted_title": formatted_title,
            "cycles": cycles,
            "operator": operator,
            "country": country,
            "region": region,
            "from_user": message.from_user.id}


async def check_channel_sub(telegram_id: int, check_trial: bool = False):
    if check_trial and telegram_id not in database.get_users()['trial_ids']:
        return

    try:
        user = await bot.get_chat_member(config.channel_id, telegram_id)
        return user['status'] != 'member'

    except (Exception, BaseException):
        return False


bot = telegram_api_connector()
dp = Dispatcher(bot)
