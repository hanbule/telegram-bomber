import sys

from handlers import start_message
from tools.misc import dp, logger, bot, admin_thinker, thinker
from tools import tools, config, misc, database, hwinfo
from aiogram import types, exceptions
import __main__
import psutil
import os
import datetime
import speedtest as speed
import platform
import asyncio


def generate_admin_kb():
    kb = types.InlineKeyboardMarkup()
    logs = types.InlineKeyboardButton(
        "Логи 🧻",
        callback_data="admin logs"
    )
    hwinfo_ = types.InlineKeyboardButton(
        "HWInfo 🌈",
        callback_data="admin hwinfo"
    )
    status = types.InlineKeyboardButton(
        "Статус 🌈",
        callback_data="admin status"
    )
    reboot = types.InlineKeyboardButton(
        "РЕБУТ БЛЯТЬ НЕ НАЖИМАЙ!!!!",
        callback_data="admin reboot"
    )
    pay_logs = types.InlineKeyboardButton(
        "гейментс логс",
        url=config.payments_logs_invite
    )
    attack_logs = types.InlineKeyboardButton(
        "атак логс",
        url=config.attacks_logs_invite
    )
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )
    kb.row(logs)
    kb.row(hwinfo_, status)
    kb.row(reboot)
    kb.row(pay_logs, attack_logs)
    kb.row(cancel)
    return kb


# Кнопка назад шобы в админ панель выйти а не на главное меню
def generate_back_admin_kb():
    kb = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message admin"
    )
    kb.row(cancel)
    return kb


def ping(ip: str):
    if platform.system().lower() == "windows":
        parameter = "-n"
    else:
        parameter = "-c"

    timestamp = datetime.datetime.now().timestamp()

    os.system(f"ping {parameter} 1 {ip} > .trash")

    ping_result = round((datetime.datetime.now().timestamp() - timestamp) * 1000)

    try:
        os.remove('./.trash')
    except (Exception, BaseException):
        pass

    return ping_result


@dp.callback_query_handler(lambda e: e.data.startswith('admin'))
async def admin_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        await callback_query.answer(str(), False)
    except exceptions.InvalidQueryID:
        pass

    message_type = callback_query.data.split(' ', maxsplit=2)[1]

    # Логи
    if message_type == 'logs':
        kb = types.InlineKeyboardMarkup()
        send = types.InlineKeyboardButton(
            "Выслать 🧻",
            callback_data="admin sendlog"
        )
        delete = types.InlineKeyboardButton(
            "Удалить 🗑",
            callback_data="admin dellog"
        )
        cancel = types.InlineKeyboardButton(
            "Назад 🔙",
            callback_data="start_message admin"
        )

        kb.row(send, delete)
        kb.row(cancel)

        text = '<b>Выбери действие:</b>'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            return

    if message_type == 'sendlog':
        text = '<b>Логи высраты.</b>'

        try:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=text, parse_mode='html', reply_markup=generate_back_admin_kb())
        except exceptions.MessageNotModified:
            pass

        return await bot.send_document(chat_id=callback_query.from_user.id,
                                       document=open(f'{__main__.PATH}/latest.log', 'rb'))

    if message_type == 'dellog':
        text = '<b>Логи выебаны.</b>'

        with open(f'{__main__.PATH}/latest.log', 'w', encoding="utf-8") as f:
            f.write(str())

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=generate_back_admin_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'hwinfo':
        try:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text='<b>Wait...</b>', parse_mode='html',
                                        reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton(
                                            "Wait... 🔙",
                                            callback_data="passed"
                                        )))
        except exceptions.MessageNotModified:
            pass

        info = await hwinfo.hwinfo()

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=info, parse_mode='html',
                                               reply_markup=generate_back_admin_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'status':
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(
            "Wait... 🔙",
            callback_data="passed"
        ))
        process = psutil.Process(os.getpid())
        memory_usage = round(process.memory_info().rss / 1e+6)

        ip = misc.ip.replace('\n', str())
        proxy_country = misc.proxy_country
        proxy_status = misc.proxy_status

        proxy_status = f'PROXY {proxy_country} ({ip})' if proxy_status else f'Прямое {proxy_country} ({ip})'

        text = f'<b>Connection:</b> {proxy_status}\n' \
               f'<b>Ping Aiogram:</b> Wait...\n' \
               f'<b>Ping SQL:</b> Wait...\n' \
               f'<b>Ping DonatePay:</b> Wait...\n' \
               f'<b>Download:</b> Wait...\n' \
               f'<b>Upload:</b> Wait...\n' \
               f'<b>Server:</b> Wait...\n' \
               f'<b>Memory:</b> {memory_usage}mb'

        timestamp = datetime.datetime.now().timestamp()

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text, parse_mode='html', reply_markup=kb)

        ping_aio = round((datetime.datetime.now().timestamp() - timestamp) * 1000)
        ping_db = ping(config.db_settings['host'])
        ping_donates = ping('104.20.6.54')

        text = f'<b>Connection:</b> {proxy_status}\n' \
               f'<b>Ping Aiogram:</b> {ping_aio}ms\n' \
               f'<b>Ping SQL:</b> {ping_db}ms\n' \
               f'<b>Ping DonatePay:</b> {ping_donates}ms\n' \
               f'<b>Download:</b> Wait...\n' \
               f'<b>Upload:</b> Wait...\n' \
               f'<b>Server:</b> Wait...\n' \
               f'<b>Memory:</b> {memory_usage}mb'

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text, parse_mode='html', reply_markup=kb)

        tester = speed.Speedtest()
        tester.get_best_server()
        tester.download()
        tester.upload()

        download = round(tester.results.dict()["download"] / 2 ** 20)
        upload = round(tester.results.dict()["upload"] / 2 ** 20)
        server = tester.results.dict()["server"]["country"] + ', ' + tester.results.dict()["server"]["name"]  # noqa

        text = f'<b>Connection:</b> {proxy_status}\n' \
               f'<b>Ping Aiogram:</b> {ping_aio}ms\n' \
               f'<b>Ping SQL:</b> {ping_db}ms\n' \
               f'<b>Ping DonatePay:</b> {ping_donates}ms\n' \
               f'<b>Download:</b> {download} MiB/s\n' \
               f'<b>Upload:</b> {upload} MiB/s\n' \
               f'<b>Server:</b> {server}\n' \
               f'<b>Memory:</b> {memory_usage}mb'

        logger('Status', f'Connection: {proxy_status}\n'
                         f'Ping Aiogram: {ping_aio}ms\n'
                         f'Ping SQL: {ping_db}ms\n'
                         f'Ping DonatePay: {ping_donates}ms\n'
                         f'Download: {download} MiB/s\n'
                         f'Upload: {upload} MiB/s\n'
                         f'Server: {server}\n'
                         f'Memory: {memory_usage}mb')

        return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                           message_id=callback_query.message.message_id,
                                           text=text, parse_mode='html', reply_markup=generate_back_admin_kb())

    # РЕБУТ НАХУЙ, СПАСАЙТЕСЬ КТО МОЖЕТ
    if message_type == 'reboot':
        # Получение списка админов
        admins = database.get_users()["admin_ids"]

        # Логирование перезапуска
        for admin in admins:
            try:
                await bot.send_message(int(admin), f'{tools.get_full_name(callback_query)} перезапустил бота!')
            except (BaseException, Exception):
                pass

        # Остановка поллинга
        dp.stop_polling()
        await asyncio.sleep(3)

        # Обновление сообщения
        try:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text='Перезагрузка...', reply_markup=generate_back_admin_kb())
        except exceptions.MessageNotModified:
            return

        # Получение команды запуска бота
        file_path = os.path.dirname(os.path.abspath(__main__.__file__))
        exe = sys.executable
        command = f'{exe} {file_path}'

        # Перезапуск бота
        os.system(command)

        # Выключение бота
        exit(0)


@dp.message_handler(commands=['terminal', 'hwinfo-terminal', 'c', 'term'])
async def terminal(message: types.Message):
    if not await thinker(message):
        return

    if not await admin_thinker(message):
        return

    # Получение команды
    try:
        command = message.text.split(' ', maxsplit=1)[1]
    except (KeyError, IndexError):
        return await message.reply(f'<i>Usage:</i> <code>{message.text.split(" ", maxsplit=1)[0]} [command]</code>',
                                   parse_mode='html')

    # Создание временного сообщения
    temp_message = await message.reply('<i>loading...</i>', parse_mode='html')

    # Выполнение команды
    output = hwinfo.tools.checkOutput(command)

    if output:
        try:
            # Отправка вывода
            return await temp_message.edit_text(f'<b>Output:</b>\n\n<code>{output}</code>',
                                                parse_mode='html')
        except (exceptions.BadRequest, Exception):
            # Загрузка вывода в файл
            file_name = tools.generate_key(16) + '_output.txt'
            await temp_message.edit_text(f'<b>Output:</b>\n\nSending...', parse_mode='html')
            with open(f'{__main__.PATH}/{file_name}', 'w', encoding='utf8') as f:
                f.write(output)

            # Отправка вывода
            await bot.send_document(
                message.from_user.id, open(f'{__main__.PATH}/{file_name}', 'rb')
            )

            # Удаление документы
            os.remove(f'{__main__.PATH}/{file_name}')

            # Обновление временного сообщения
            return await temp_message.edit_text(f'<b>Output:</b>', parse_mode='html')

    else:
        return await message.reply(f'Command <code>{command}</code> command command failed or have not output',
                                   parse_mode='html')


@dp.message_handler(commands=['invite', 'i', 'promote'])
async def invite(message: types.Message):
    if not await thinker(message):
        return

    if not await admin_thinker(message):
        return

    try:
        what = int(message.text.split(' ', maxsplit=1)[1])

    except (IndexError, KeyError):
        text = f'<i>Usage:</i> <code>{message.text.split(" ", maxsplit=1)[0]} [telegram_id]</code>'
        return await message.reply(text, parse_mode='html')

    dump = database.get_user(what)
    ban_status = dump['ban_status']

    database.give_sub(what)

    text = '<b>Донат и приобретение подписки</b>\n\n' \
           f'<b>{dump["full_name"]}</b>, ' \
           f'благодарим Вас за приобретение подписки на наш сервис! ' \
           f'Это поможет мне поддерживать его, добавлять новые сервисы и платить за хостинг. ' \
           f'Теперь вы можете пользоваться ботом в полной мере, ' \
           f'<b>без ограничений!</b>' + ('\n\n<b>Блокировка снята.</b>' if ban_status else str())

    await message.reply('долбоеб повышен')
    return await bot.send_message(what, text, parse_mode='html', reply_markup=start_message.generate_cancel_kb)
