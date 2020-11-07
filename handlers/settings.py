from aiogram import types, exceptions

from tools import tools, database
from handlers import start_message

from tools.misc import dp, logger, bot


@dp.callback_query_handler(lambda e: e.data.startswith('settings'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    message_type = callback_query.data.split(' ', maxsplit=2)[1]

    text = "<b>Настройки:</b>"

    if message_type == 'mailing':
        if callback_query.data.split(' ', maxsplit=2)[2] == 'off_from_mailing':
            database.change_mailing_status(callback_query.from_user.id, False)
            try:
                return await callback_query.answer('Настройки рассылки успешно обновлены.', True)
            except exceptions.InvalidQueryID:
                return
        status = True if callback_query.data.split(' ', maxsplit=2)[2] == 'True' else False
        database.change_mailing_status(callback_query.from_user.id, status)

        try:
            await callback_query.answer('Настройки рассылки успешно обновлены.', False)
        except exceptions.InvalidQueryID:
            pass

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    if message_type == 'proxy':
        status = True if callback_query.data.split(' ', maxsplit=2)[2] == 'True' else False
        database.edit_user(callback_query.from_user.id, 'proxy_status', status)

        try:
            await callback_query.answer('Настройки прокси успешно обновлены.', False)
        except exceptions.InvalidQueryID:
            pass

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    if message_type == 'phone':
        database.attach_phone_number(callback_query.from_user.id, None)

        try:
            await callback_query.answer('Телефон успешно отвязан.', False)
        except exceptions.InvalidQueryID:
            pass

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    plus_or_minus = callback_query.data.split(' ', maxsplit=2)[2]

    if message_type == 'pause':
        if database.edit_pause(callback_query.from_user.id, plus_or_minus):
            try:
                await callback_query.answer('Настройки паузы успешно обновлены.', False)
            except exceptions.InvalidQueryID:
                pass
        else:
            try:
                return await callback_query.answer('Вы не можете поставить такую паузу.', True)
            except exceptions.InvalidQueryID:
                return

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    if message_type == 'cycles':
        if database.edit_cycles(callback_query.from_user.id, plus_or_minus):
            try:
                await callback_query.answer('Настройки циклов успешно обновлены.', False)
            except exceptions.InvalidQueryID:
                pass
        else:
            try:
                return await callback_query.answer('Вы не можете поставить такое количество циклов.', True)
            except exceptions.InvalidQueryID:
                return
        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return

    if message_type == 'timeout':
        if database.edit_timeout(callback_query.from_user.id, plus_or_minus):
            try:
                await callback_query.answer('Настройки таймаута успешно обновлены.', False)
            except exceptions.InvalidQueryID:
                pass
        else:
            try:
                return await callback_query.answer('Вы не можете поставить такой таймаут.', True)
            except exceptions.InvalidQueryID:
                return

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_settings_kb
                                               (callback_query.from_user.id))
        except exceptions.MessageNotModified:
            return
