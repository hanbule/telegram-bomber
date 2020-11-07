from aiogram import types

from tools import tools, config
from tools.database import get_users
from tools.misc import dp, thinker, check_channel_sub

from handlers import start_message


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = f"<b>{tools.get_full_name(message)}</b>, приветствую тебя" \
           f" в моем новом <b>приватном</b> SMS Bombere в Telegram!\n\n" \
           f"Ты - мой новый пользователь. " \
           f"Поэтому, предлагаю тебе <b>{config.trial_start_count}</b> бесплатных запусков. " \
           f'Очень надеюсь, что ты останешься с нами! ' \
           f'Информация о снятии ограничений находится во вкладке "Донат".\n\n<b>Выбери действие:</b>' \
           f'' if message.from_user.id not in get_users()['telegram_ids'] else '<b>Выбери действие:</b>'

    if await check_channel_sub(message.from_user.id, True) and message.from_user.id in get_users()['telegram_ids']:
        text += f'\n\nПодпишись на наш канал <b>@{config.channel}</b>, что бы не пропускать самое интересное! ' \
                f'(Это сообщение пропадет после подписки на канал).'

    if not await thinker(message):
        return

    return await message.reply(text, parse_mode='html',
                               reply_markup=start_message.generate_start_kb(message.from_user.username))
