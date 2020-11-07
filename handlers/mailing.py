import asyncio
import datetime
import random

from aiogram import types, exceptions

from tools import tools, database
from tools.misc import dp, admin_thinker, thinker, bot, logger


@dp.message_handler(commands=['send'])
async def link(message: types.Message):
    if not await thinker(message):
        return

    if not await admin_thinker(message):
        return

    types_mailing = ['all', 'all_force', 'trial_force', 'sub_force', 'admin_force', 'ban_force', 'self']

    try:
        atr = message.text.split(' ')[1]

        if atr not in types_mailing:
            atr = 'all'

    except (KeyError, IndexError):
        return await message.reply(
            f'Необходимо указать тип рассылки через пробел: {" / ".join(types_mailing)}.')

    try:
        text = message.text.split(' ', maxsplit=2)[2]

    except (KeyError, IndexError):
        return await message.reply('Необходимо указать текст рассылки через пробел.', parse_mode='html')

    users = 'mailing_ids'

    if atr == 'all':
        users = 'mailing_ids'

    if atr == 'all_force':
        users = 'telegram_ids'

    if atr == 'trial_force':
        users = 'trial_ids'

    if atr == 'sub_force':
        users = 'sub_ids'

    if atr == 'admin_force':
        users = 'admin_ids'

    if atr == 'ban_force':
        users = 'banned_ids'

    users = database.get_users()[users]

    if atr == 'self':
        users = [message.from_user.id]

    random.shuffle(users)

    i = 0
    j = 0

    latest_edited_message = datetime.datetime.timestamp(datetime.datetime.now())

    msg = await message.reply('<b>Статус:</b> Выполняется\n'
                              f'<b>Количество пользователей, '
                              f'попадающих под рассылку:</b> {len(users)}\n'
                              f'<b>Тип рассылки:</b> {atr}\n'
                              f'<b>Количество отправленных сообщений:</b> {i}\n'
                              f'<b>Количество удаленных пользователей:</b> {j}\n\n'
                              f'<b>{"░" * 20} (0 %)</b>', parse_mode='html')

    if len(users) > 0:
        text_new = list()

        buttons = list()
        images = list()

        for line in text.splitlines():
            if line.startswith('<button>') and line.endswith('</button>'):
                buttons.append(types.InlineKeyboardButton(
                    line.split('<button>', maxsplit=1)[1].split('|', maxsplit=1)[0],
                    url=line.split('|', maxsplit=1)[1].split('</button>', maxsplit=1)[0]
                ))

            elif line.startswith('<image>') and line.endswith('</image>'):
                images.append(
                    f'<a href="{line.split("<image>", maxsplit=1)[1].split("</image>", maxsplit=1)[0]}">&#8204;</a>'
                )

            else:
                text_new.append(line)

        text = '\n'.join(text_new).replace('\nKSTL', str()).replace('KSTL', '&#13;')

        for image in images:
            text += image

        logger('Mailing',
               f'Mailing {atr} for {len(users)} users from {tools.get_full_name(message)} '
               f'with id {message.from_user.id} started')

        for user_id in users:
            try:
                await asyncio.sleep(3)

                kb = types.InlineKeyboardMarkup()

                for button in buttons:
                    kb.row(button)

                if atr != 'force':
                    kb.row(types.InlineKeyboardButton(
                        'Отключить рассылку',
                        callback_data="settings mailing off_from_mailing"
                    ))

                try:
                    if atr != 'all' and len(buttons) <= 0:
                        await bot.send_message(int(user_id),
                                               text.replace(
                                                   '<full_name>', database.get_user(int(user_id))['full_name']),
                                               parse_mode='html')
                    else:
                        await bot.send_message(int(user_id),
                                               text.replace(
                                                   '<full_name>', database.get_user(int(user_id))['full_name']),
                                               reply_markup=kb,
                                               parse_mode='html')
                    i += 1

                except (exceptions.BotKicked, exceptions.BotBlocked,
                        exceptions.UserDeactivated,
                        exceptions.CantInitiateConversation,
                        exceptions.CantTalkWithBots,
                        exceptions.ChatNotFound):
                    j += 1

                    if not database.get_user(int(user_id))['ban_status']:
                        database.delete_user(int(user_id))

                    continue

                if (datetime.datetime.timestamp(
                        datetime.datetime.now()) - latest_edited_message) >= 9:
                    latest_edited_message = datetime.datetime.timestamp(
                        datetime.datetime.now()
                    )
                    try:
                        progressbar = tools.generate_progressbar((i + j), len(users))

                        await msg.edit_text('<b>Статус:</b> Выполняется\n'
                                            f'<b>Количество пользователей, '
                                            f'попадающих под рассылку:</b> {len(users)}\n'
                                            f'<b>Тип рассылки:</b> {atr}\n'
                                            f'<b>Количество отправленных сообщений:</b> {i}\n'
                                            f'<b>Количество удаленных пользователей:</b> {j}\n\n'
                                            f'<b>{progressbar}</b>', parse_mode='html')

                        continue

                    except exceptions.MessageNotModified:
                        continue

            except (BaseException, Exception):
                j += 1
                continue

        await msg.edit_text('<b>Статус:</b> Выполнено\n'
                            f'<b>Количество пользователей, '
                            f'попадающих под рассылку:</b> {len(users)}\n'
                            f'<b>Тип рассылки:</b> {atr}\n'
                            f'<b>Количество отправленных сообщений:</b> {i}\n'
                            f'<b>Количество удаленных пользователей:</b> {j}\n\n'
                            f'<b>{"▓" * 20} (100 %)</b>', parse_mode='html')

        logger('Mailing',
               f'Mailing {atr} for {len(users)} users from {tools.get_full_name(message)} '
               f'with id {message.from_user.id} stopped')

    else:
        return await msg.edit_text(f'<b>Статус:</b> ERROR (Caused by ZeroUsers error)\n'
                                   f'<b>Количество пользователей, '
                                   f'попадающих под рассылку:</b> {len(users)}\n'
                                   f'<b>Тип рассылки:</b> {atr}\n'
                                   f'<b>Количество отправленных сообщений:</b> {i}\n'
                                   f'<b>Количество удаленных пользователей:</b> {j}\n\n'
                                   f'<b>{"X" * 20} (X %)</b>', parse_mode='html')
