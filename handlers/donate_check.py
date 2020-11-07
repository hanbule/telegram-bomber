import asyncio
import json
from aiogram import types

import requests
from aiogram.utils import exceptions

from tools import tools, config, database
from tools.misc import dp, bot, logger


async def log(callback_query: types.CallbackQuery, dump, summ, comment, user_ip, region):
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

    text = f'<b>NEW PAYMENT</b>\n\n' \
           f'<a href="tg://user?id={dump["telegram_id"]}">{dump["full_name"]}</a> ' \
           f'<i>({dump["telegram_id"]})</i>\n\n' \
           f'<b>SUMM:</b> {summ} RUB (SUB - {config.sub_price} RUB)\n' \
           f'<b>COMMENT:</b> {comment}\n' \
           f'<b>IP:</b> {user_ip}\n' \
           f'<b>REGION:</b> {region}\n' \
           f'<b>BALANCE:</b> {balance} RUB\n' \
           f'<b>TOTAL CASHOUT:</b> {total_cashout + balance} RUB'

    logger('Donate', f'NEW PAYMENT\n\n'
                     f'{dump["full_name"]} '
                     f'({dump["telegram_id"]})\n\n'
                     f'SUMM: {summ} RUB (SUB - {config.sub_price} RUB)\n'
                     f'COMMENT: {comment}\n'
                     f'IP: {user_ip}\n'
                     f'REGION: {region}\n'
                     f'BALANCE: {balance} RUB\n'
                     f'TOTAL CASHOUT: {total_cashout + balance} RUB')

    kb = types.InlineKeyboardMarkup()
    profile = types.InlineKeyboardButton(
        "Профиль",
        url=f'https://t.me/{callback_query.from_user.username}'
    )
    kb.row(profile)

    if callback_query.from_user.username is not None:
        await bot.send_message(config.payments_logs, text, parse_mode='html', reply_markup=kb)
    else:
        await bot.send_message(config.payments_logs, text, parse_mode='html')


@dp.callback_query_handler(lambda e: e.data.startswith('donate_check'))
async def donate_check_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        await callback_query.answer(str(), False)
    except exceptions.InvalidQueryID:
        pass

    if callback_query.from_user.id in database.get_users()['sub_ids']:
        kb = types.InlineKeyboardMarkup()
        pay = types.InlineKeyboardButton(
            "Страница оплаты 💰",
            url=config.buy_link
        )
        cancel = types.InlineKeyboardButton(
            "Назад 🔙",
            callback_data="start_message start"
        )
        kb.row(pay)
        kb.row(cancel)

        text = '<b>Донат и приобретение подписки</b>\n\n' \
               f'<b>{tools.get_full_name(callback_query)}</b>, ' \
               f'вы уже владеете подпиской на наш бомбер! Тем не ' \
               f'менее, если вы желаете безвозмездно поддержать ' \
               f'наш проект, то ссылку для оплаты вы можете найти ниже 😉. '

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            return

    kb = types.InlineKeyboardMarkup()
    pay = types.InlineKeyboardButton(
        "Страница оплаты 💰",
        url=config.buy_link
    )
    check = types.InlineKeyboardButton(
        "Проверить платеж 💰",
        callback_data="donate_check"
    )
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )
    kb.row(pay, check)
    kb.row(cancel)

    full_name = tools.get_full_name(callback_query)
    latest_donate = json.loads(requests.get('https://donatepay.ru/api/v1/transactions',
                                            params={
                                                "access_token": config.dp_token,
                                                "limit": 1,
                                                "type": "donation"
                                            }).text)

    if latest_donate['status'] == 'error':
        text = '<b>Донат и приобретение подписки</b>\n\n' \
               f'{full_name}, данную операцию можно выполнять только <b>раз в 20 секунд</b>. ' \
               'Повторите попытку позднее. В случае возникновения проблем, ' \
               'пожалуйста, <b>обратитесь в тех. поддержку</b>.'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            return

    what = latest_donate['data'][0]['what']
    summ = int(float(latest_donate['data'][0]['sum']))
    comment = str(latest_donate['data'][0]['comment'])
    user_ip = str(latest_donate['data'][0]['vars']['user_ip'])

    if user_ip is not None:
        region = json.loads(requests.get('http://www.geoplugin.net/json.gp',
                                         params={
                                             "ip": user_ip
                                         }).text)
        if (region["geoplugin_regionName"] and region["geoplugin_city"]) != str():
            region = f'{region["geoplugin_countryName"]}, {region["geoplugin_regionName"]}, {region["geoplugin_city"]}'
        else:
            region = region["geoplugin_countryName"]
    else:
        region = 'Unknown'

    try:
        what = int(what)
    except (IndexError, ValueError):
        pass

    if not what == callback_query.from_user.id:
        text = '<b>Донат и приобретение подписки</b>\n\n' \
               f'{full_name}, к сожалению, мы не можем выдать Вам подписку, ' \
               'так как автоматическая система проверки платежей ' \
               '<b>не нашла Ваш платеж</b>. ' \
               'Пожалуйста, <b>обратитесь в тех. поддержку.</b>'
        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            return

    if summ < config.sub_price:
        text = '<b>Донат и приобретение подписки</b>\n\n' \
               f'{full_name}, к сожалению, мы не можем выдать Вам подписку, ' \
               'так как Вы заплатили менее установленных ' \
               f'<b>{config.sub_price} ₽</b>. ' \
               'Пожалуйста, <b>обратитесь в тех. поддержку.</b>'
        try:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=text, parse_mode='html', reply_markup=kb)
        except exceptions.MessageNotModified:
            pass

        dump = database.get_user(what)

        return await log(callback_query, dump, summ, comment, user_ip, region)

    ban_status = database.get_user(what)['ban_status']

    database.give_sub(what)

    kb = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(
        "Назад 🔙",
        callback_data="start_message start"
    )
    kb.row(cancel)

    text = '<b>Донат и приобретение подписки</b>\n\n' \
           f'<b>{tools.get_full_name(callback_query)}</b>, ' \
           f'благодарим Вас за приобретение подписки на наш сервис! ' \
           f'Это поможет мне поддерживать его, добавлять новые сервисы и платить за хостинг. ' \
           f'Теперь вы можете пользоваться ботом в полной мере, ' \
           f'<b>без ограничений!</b>' + ('\n\n<b>Блокировка снята.</b>' if ban_status else str())

    try:
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text, parse_mode='html', reply_markup=kb)
    except exceptions.MessageNotModified:
        pass

    dump = database.get_user(what)

    return await log(callback_query, dump, summ, comment, user_ip, region)
