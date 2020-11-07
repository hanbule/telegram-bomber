import asyncio
import datetime
import json

import requests
import handlers.admin_panel
from aiogram import types, exceptions

from tools import tools, config, database

from tools.misc import dp, logger, bot, check_channel_sub


def generate_start_kb(user_name: (str, None)):
    kb = types.InlineKeyboardMarkup()
    profile = types.InlineKeyboardButton(
        "Профиль 📖",
        callback_data="start_message profile"
    )
    help_ = types.InlineKeyboardButton(
        "Помощь 🚑",
        callback_data="start_message help"
    )
    settings = types.InlineKeyboardButton(
        "Настройки ⚙",
        callback_data="start_message settings"
    )
    stats = types.InlineKeyboardButton(
        "Статистика 🧻",
        callback_data="start_message stats"
    )
    ads = types.InlineKeyboardButton(
        "Реклама 🎉",
        callback_data="start_message ads"
    )
    donate = types.InlineKeyboardButton(
        "Донат 💰",
        callback_data="start_message donate"
    )
    about = types.InlineKeyboardButton(
        "О боте 😎",
        callback_data="start_message about"
    )
    admin = types.InlineKeyboardButton(
        "ОПЕР УПАЛ НАМОЧЕННЫЙ",
        callback_data="start_message admin"
    )

    kb.row(profile, help_, settings)
    kb.row(ads, donate, stats)

    if user_name in config.creators or user_name == config.support:
        kb.row(admin, about)
    else:
        kb.row(about)

    return kb


def generate_help_back_kb():
    kb = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message help"
    )
    kb.row(cancel)
    return kb


def generate_donate_kb(sub=False):
    kb = types.InlineKeyboardMarkup()
    pay = types.InlineKeyboardButton(
        "Страница оплаты 💰",
        url=config.buy_link
    )
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )

    if not sub:
        check = types.InlineKeyboardButton(
            "Проверить платеж 💰",
            callback_data="donate_check"
        )
        kb.row(pay, check)
    else:
        kb.row(pay)

    kb.row(cancel)

    return kb


def generate_help_kb():
    kb = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(
        'Запуск бомбера 💣',
        callback_data="help launch_bomber"
    )

    button2 = types.InlineKeyboardButton(
        'Отключение новостных рассылок 💰',
        callback_data="help disable_mailing"
    )

    button4 = types.InlineKeyboardButton(
        'Остановка предыдущих атак 🦠',
        callback_data="help stop_attack"
    )

    button5 = types.InlineKeyboardButton(
        'Донат и приобретение подписки 💸',
        callback_data="start_message donate"
    )

    button6 = types.InlineKeyboardButton(
        'Привязка номера 🧲',
        callback_data="help number_binding"
    )

    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )

    kb.row(button1)
    kb.row(button2)
    kb.row(button4)
    kb.row(button5)
    kb.row(button6)
    kb.row(cancel)

    return kb


def generate_settings_kb(telegram_id: int):
    dump = database.get_user(telegram_id)

    kb = types.InlineKeyboardMarkup()

    mailing = types.InlineKeyboardButton(
        f"Новостная рассылка {'✅' if dump['settings']['mailing_status'] else '❌'}",
        callback_data=f"settings mailing {True if not dump['settings']['mailing_status'] else False}"
    )

    proxy = types.InlineKeyboardButton(
        f"Proxy {'✅' if dump['settings']['proxy_status'] else '❌'}",
        callback_data=f"settings proxy {True if not dump['settings']['proxy_status'] else False}"
    )

    time_out_title = types.InlineKeyboardButton(
        f"Тайм-аут: {int(dump['settings']['timeout'])}s",
        callback_data="passed"
    )
    time_out_append = types.InlineKeyboardButton(
        "➕",
        callback_data="settings timeout +"
    )
    time_out_remove = types.InlineKeyboardButton(
        "➖",
        callback_data="settings timeout -"
    )

    pause_title = types.InlineKeyboardButton(
        f"Пауза между СМС: {int(dump['settings']['pause'])}s",
        callback_data="passed"
    )
    pause_append = types.InlineKeyboardButton(
        "➕",
        callback_data="settings pause +"
    )
    pause_remove = types.InlineKeyboardButton(
        "➖",
        callback_data="settings pause -"
    )

    cycles_title = types.InlineKeyboardButton(
        f"Стандартное количество циклов: {int(dump['settings']['default_cycles'])}",
        callback_data="passed"
    )
    cycles_append = types.InlineKeyboardButton(
        "➕",
        callback_data="settings cycles +"
    )
    cycles_remove = types.InlineKeyboardButton(
        "➖",
        callback_data="settings cycles -"
    )

    phone = types.InlineKeyboardButton(
        "Удалить привязанный телефон ❌",
        callback_data="settings phone"
    )

    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )

    kb.row(mailing)
    kb.row(proxy)
    kb.row(time_out_title)
    kb.row(time_out_remove, time_out_append)
    kb.row(pause_title)
    kb.row(pause_remove, pause_append)
    kb.row(cycles_title)
    kb.row(cycles_remove, cycles_append)
    if dump['settings']['attached_phone_number'] is not None:
        kb.row(phone)
    kb.row(cancel)

    return kb


def generate_cancel_kb():
    kb = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )
    kb.row(cancel)

    return kb


def generate_profile_text(user: int):
    dump = database.get_user(user)

    sub = 'TRIAL' if not dump['sub_status'] else 'FULL'
    cycles = config.trial_cycles_count if not dump['sub_status'] else config.sub_cycles_count
    starts = dump["trial_start_count"] if not dump['sub_status'] else "∞"
    admin = user in database.get_users()['admin_ids']
    admin_status = 'YES' if admin else 'NO'
    ban_status = 'YES' if dump['ban_status'] else 'NO'
    user_name = dump['user_name']
    attached_phone_number = dump['settings']['attached_phone_number']
    reg_time = None
    buy_time = None

    try:
        reg_time = datetime.datetime.fromtimestamp(dump['reg_time']).strftime('%d.%m.%Y %H:%M:%S') + ' MSK'
        buy_time = datetime.datetime.fromtimestamp(dump['buy_time']).strftime('%d.%m.%Y %H:%M:%S') + ' MSK'
    except (AttributeError, TypeError):
        pass

    text = f'<b>{dump["full_name"]}</b> <i>({dump["telegram_id"]})</i>\n\n'
    text += f'<b>Юзернейм:</b> @{user_name}\n\n' if user_name is not None else str()
    text += f'<b>Подписка:</b> {sub}\n'
    text += f'<b>Количество доступных циклов:</b> {cycles}\n'
    text += f'<b>Количество доступных запусков:</b> {starts}\n\n'
    text += f'<b>Статус администратора:</b> {admin_status}\n'
    text += f'<b>Статус блокировки:</b> {ban_status}\n\n'
    text += f'<b>Время регистрации:</b> {reg_time}\n' if reg_time is not None else str()
    text += f'<b>Время покупки:</b> {buy_time}\n' if buy_time is not None else str()
    text += f'\n<b>Привязанный телефон:</b> {attached_phone_number}' if attached_phone_number is not None else str()

    return text


@dp.callback_query_handler(lambda e: e.data.startswith('start_message'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        await callback_query.answer(str(), False)
    except exceptions.InvalidQueryID:
        pass

    message_type = callback_query.data.split(' ', maxsplit=1)[1]

    if message_type == 'help':
        text = '<b>Выбери действие:</b>'

        if await check_channel_sub(callback_query.from_user.id, True):
            text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                    f'(Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=generate_help_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'donate':
        if callback_query.from_user.id in database.get_users()['sub_ids']:
            text = '<b>Донат и приобретение подписки</b>\n\n' \
                   f'<b>{tools.get_full_name(callback_query)}</b>, ' \
                   f'вы уже владеете подпиской на наш бомбер! Тем не ' \
                   f'менее, если вы желаете безвозмездно поддержать ' \
                   f'наш проект, то ссылку для оплаты вы можете найти ниже 😉. '

            try:
                return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                                   message_id=callback_query.message.message_id,
                                                   text=text, parse_mode='html',
                                                   reply_markup=generate_donate_kb(
                                                       callback_query.from_user.id in database.get_users()['sub_ids'])
                                                   )
            except exceptions.MessageNotModified:
                return

        telegram_id = callback_query.from_user.id

        text = '<b>Донат и приобретение подписки</b>\n\n' \
               'Наш сервис является приватным. Полный доступ есть не у всех. ' \
               f'Но, вы можете поддержать наш проект и при донате от <b>{config.sub_price} ₽</b> ' \
               '(Единоразовый платеж) на вашем аккаунте активируется полный доступ.\n\n' \
               'Оплата происходит через сервис <b>DonatePay</b>, в котором ' \
               'присутствуют следующие платежные системы: QIWI, Apple Pay, ' \
               'Google Pay, Visa, MC, WebMoney, Яндекс.Деньги, BTC и т. д. ' \
               'Украинские и Белорусские карты <b>также обслуживаются</b> сервисом.\n\n' \
               f'В поле "Ваше имя" необходимо ввести ваш персональный код - <b>{telegram_id}</b> ' \
               'и после оплаты нажать кнопку "Проверить платеж". ' \
               'Если вы все сделали верно - полный доступ автоматически ' \
               'активируется. В другом случае - вам стоит обратиться в тех. ' \
               'поддержку для ручной активации.\n\nПолный доступ дает вам:\n' \
               '1.<b> Неограниченное количество запусков</b>\n' \
               f'2.<b>До {config.sub_cycles_count} циклов</b>\n' \
               '3.<b> Более быстрые прокси</b> (Влияет на количество приходимых SMS и скорость отправки)\n' \
               '4.<b> Полное отключение рекламы, как рекламу наших партнеров, так и рекламу нашего канала.</b>'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=generate_donate_kb(
                                                   callback_query.from_user.id in database.get_users()['sub_ids'])
                                               )
        except exceptions.MessageNotModified:
            return

    if message_type == 'ads':
        kb = types.InlineKeyboardMarkup()
        support = types.InlineKeyboardButton(
            "Обратиться в тех. поддержку",
            url=f'https://t.me/{config.support}'
        )
        cancel = types.InlineKeyboardButton(
            "Назад 🔙",
            callback_data="start_message start"
        )
        kb.row(support)
        kb.row(cancel)

        text = '<b>Покупка рекламы в рассылках</b>\n\n' \
               'С последним крупным обновлением наш бот ' \
               'получил возможность <b>рассылки таргетированной ' \
               'рекламы</b>. В данный момент, количество ' \
               'пользователей бота составляет более ' \
               f'{int(round(len(database.get_users()["telegram_ids"]) * config.users_multiplier, -1))} ' \
               f'и их количество растет с каждый ' \
               'днем.\n\n<b>Почему стоит купить рассылку?</b>\n\n1. ' \
               'Пользователи нашего бота заинтересованы в довольно ' \
               'узком направлении\n2. Даже с учетом 1-го пункта, ' \
               'количество наших пользователей довольно велико\n3. ' \
               'Цена за услугу, которую мы вам предоставляем мала ' \
               'в данной области\n4. Мы имеем возможность рассылки ' \
               'сообщений, персональных для каждого пользователя (С ' \
               'обращением по имени, никнейму), а также добавление в ' \
               'сообщение URL кнопок вплоть до 9-ти штук и фото.\n\nЦена ' \
               f'одной рассылки составит <b>{config.smm_price} ₽</b>.' \
               '\n\nМы понимаем, что мы должны заслужить ваше доверие ' \
               'и окупить вам данную рассылку, поэтому на первые три ' \
               'рассылки <b>действует скидка - 50%</b>. На массовые ' \
               'рассылки (Более 3х рассылок за раз) также действуют ' \
               'скидки.\n\nРассылки проводятся не более 1-й штуки в ' \
               'день. Есть возможность отложенной рассылки. Если день ' \
               'забронирован, придется перенести рассылку.\n\nЕсли ' \
               'вы заинтересовались в покупке рассылки, оставьте ' \
               'заявку, написав нам в тех. поддержку. Мы обязательно с вами свяжемся.'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            return

    if message_type == 'profile':
        text = generate_profile_text(callback_query.from_user.id)

        if await check_channel_sub(callback_query.from_user.id, True):
            text += f'\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                    f'(Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=generate_cancel_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'stats':
        dump_get_users = database.get_users()
        user_name = callback_query.from_user.username

        users_quantity = round(len(dump_get_users["telegram_ids"]) * config.users_multiplier)
        subs_quantity = len(dump_get_users["sub_ids"])
        mailing_quantity = len(dump_get_users["mailing_ids"])
        ban_quantity = len(dump_get_users["banned_ids"])
        proxy_quantity = len(database.get_proxys())
        services_quantity = round(len(tools.load_services()) * config.services_multiplier)

        text = f'<b>Статистика</b>\n\n' \
               f'<b>Количество пользователей:</b> {users_quantity}\n' \
               f'<b>Количество подписчиков:</b> {subs_quantity}\n' \
               f'<b>Количество подписчиков на рассылку:</b> {mailing_quantity}\n' \
               f'<b>Количество забаненых пользователей:</b> {ban_quantity}\n' \
               f'<b>Количество сервисов:</b> {services_quantity}\n' \
               f'<b>Количество Proxy:</b> {proxy_quantity}'

        if user_name in config.creators or user_name == config.support:
            kb = types.InlineKeyboardMarkup()
            kb.row(types.InlineKeyboardButton(
                "Wait... 🔙",
                callback_data="passed"
            ))
            text = f'<b>Статистика</b>\n\n' \
                   f'<b>Количество пользователей:</b> {users_quantity}\n' \
                   f'<b>Количество подписчиков:</b> {subs_quantity}\n' \
                   f'<b>Количество подписчиков на рассылку:</b> {mailing_quantity}\n' \
                   f'<b>Количество забаненых пользователей:</b> {ban_quantity}\n' \
                   f'<b>Количество сервисов:</b> {services_quantity}\n' \
                   f'<b>Количество Proxy:</b> {proxy_quantity}\n\n' \
                   f'<b>Баланс DonatePay:</b> Выполняется запрос к DonatePay...\n' \
                   f'<b>Общий доход с бота:</b> Выполняется запрос к DonatePay...'

            try:
                await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            text=text, parse_mode='html', reply_markup=kb)
            except exceptions.MessageNotModified:
                pass

            latest_balance = json.loads(requests.get('https://donatepay.ru/api/v1/user',
                                                     params={
                                                         "access_token": config.dp_token}
                                                     ).text)

            while latest_balance['status'] == 'error':
                await asyncio.sleep(3)
                latest_balance = json.loads(requests.get('https://donatepay.ru/api/v1/user',
                                                         params={
                                                             "access_token": config.dp_token}
                                                         ).text)
            balance = latest_balance['data']['balance']
            total_cashout = latest_balance['data']['cashout_sum']

            text = f'<b>Статистика</b>\n\n' \
                   f'<b>Количество пользователей:</b> {users_quantity}\n' \
                   f'<b>Количество подписчиков:</b> {subs_quantity}\n' \
                   f'<b>Количество подписчиков на рассылку:</b> {mailing_quantity}\n' \
                   f'<b>Количество забаненых пользователей:</b> {ban_quantity}\n' \
                   f'<b>Количество сервисов:</b> {services_quantity}\n' \
                   f'<b>Количество Proxy:</b> {proxy_quantity}\n\n' \
                   f'<b>Баланс DonatePay:</b> {balance} ₽\n' \
                   f'<b>Общий доход с бота:</b> {balance + total_cashout} ₽'

        else:
            if await check_channel_sub(callback_query.from_user.id, True):
                text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы ' \
                        f'не пропускать самое интересное! (Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=generate_cancel_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'start':
        text = '<b>Выбери действие:</b>'

        if await check_channel_sub(callback_query.from_user.id, True):
            text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                    f'(Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=generate_start_kb(callback_query.from_user.username))
        except exceptions.MessageNotModified:
            return

    if message_type == 'about':
        me = await bot.get_me()

        text = f'<b>{me["first_name"]} v{config.version}</b>\n\n' \
               f'<b>Поддержка:</b> @{config.support}\n' \
               f'<b>Канал с обновлениями:</b> @{config.channel}'

        if await check_channel_sub(callback_query.from_user.id, True):
            text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                    f'(Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=generate_cancel_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'settings':
        text = "<b>Настройки:</b>"

        if await check_channel_sub(callback_query.from_user.id, True):
            text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                    f'(Это сообщение пропадет после подписки на канал).'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=generate_settings_kb(callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    if message_type == 'admin':
        text = '<b>АУЕ</b><a href="https://baltnews.ee/images/101779/83/1017798349.jpg">&#8204;</a>'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=handlers.admin_panel.generate_admin_kb())
        except exceptions.MessageNotModified:
            return
