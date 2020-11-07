import asyncio

from aiogram import types

from tools import tools, database, misc
from tools.misc import dp, thinker


@dp.message_handler(commands=['link'])
async def link(message: types.Message):
    if not await thinker(message):
        return

    dump = database.get_user(message.from_user.id)

    if dump['settings']['attached_phone_number'] is not None:
        text = '<i>К сожалению, привязать номер невозможно, т.к. вы уже имеете привязанный номер.' \
               ' Привязать можно только один номер на аккаунт. Если вы случайно ввели некорректный номер, ' \
               'вы можете отвязать его в настройках.</i>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(5)
        await reply_message.delete()
        return await message.delete()

    if not database.get_user(message.from_user.id)['sub_status']:
        text = 'Номер <b>недействителен</b>. ' \
               'Для получения информации об ' \
               'использовании бота, пожалуйста, ' \
               'используйте <b>помощь.</b>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(5)
        await reply_message.delete()
        return await message.delete()

    try:
        temp_phone = message.text.split(' ', maxsplit=1)[1]

    except (IndexError, KeyError):
        text = 'Номер <b>недействителен</b>. ' \
               'Для получения информации об ' \
               'использовании бота, пожалуйста, ' \
               'используйте <b>помощь.</b>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(5)
        await reply_message.delete()
        return await message.delete()

    phone = misc.check_bomber(temp_phone, 1)

    if not phone:
        text = 'Номер <b>недействителен</b>. ' \
               'Для получения информации об ' \
               'использовании бота, пожалуйста, ' \
               'используйте <b>помощь.</b>'

        reply_message = await message.reply(text, parse_mode='html')
        await asyncio.sleep(5)
        await reply_message.delete()
        return await message.delete()

    code = phone['code']
    number = phone['number']
    formatted = phone['formatted']
    full_phone = tools.get_full_number(code, number)

    database.attach_phone_number(message.from_user.id, full_phone)

    text = f'<b>Номер {formatted} успешно привязан.</b>'

    reply_message = await message.reply(text, parse_mode='html')
    await asyncio.sleep(5)
    await reply_message.delete()
    return await message.delete()
