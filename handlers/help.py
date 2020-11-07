from aiogram import types, exceptions

from tools import tools, database
from handlers import start_message
from tools.misc import dp, logger, bot


@dp.callback_query_handler(lambda e: e.data.startswith('help'))
async def start_callback(callback_query: types.CallbackQuery):
    logger('Button', f'{tools.get_full_name(callback_query)} with id {callback_query.from_user.id} '
                     f'press button {callback_query.data}')

    try:
        await callback_query.answer(str(), False)
    except exceptions.InvalidQueryID:
        pass

    message_type = callback_query.data.split(' ', maxsplit=2)[1]
    dump = database.get_user(callback_query.from_user.id)

    if message_type == 'launch_bomber':
        text = "<b>Запуск атак</b>\n\n" \
               "Чтобы запустить спам, введите номер, и, опционально, количество " \
               "циклов после запятой. Скобки, тире, плюс и пробел игнорируются " \
               "(Можно вводить номера как с ними, так и без них). Если аргумент с " \
               f"количеством циклов отсутствует, то его значение равно " \
               f"{dump['settings']['default_cycles']} (Это значение можно поменять " \
               f"в настройках).\n\nПример: <b>+7 123 456 78 90; 81234567890</b>"
        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_help_back_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'disable_mailing':
        text = '<b>Отключение новостных рассылок</b>\n\n' \
               'Стоит понимать, что если вы владеете подпиской ' \
               'на наш сервис, то реклама посредством новостной ' \
               'рассылки <b>не отправляется.</b> Тем не менее, ' \
               'если вы не имеете подписку или не желаете получать ' \
               'информацию об обновлениях бота, для отключения ' \
               'новостной рассылки необходимо перейти в настройки ' \
               'и нажать на кнопку <b>"Новостная рассылка"</b>. ' \
               'Также отключить новостную рассылку можно по кнопке ' \
               'под каждым новым сообщением из рассылки.'
        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_help_back_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'stop_attack':
        text = "<b>Остановка предыдущих атак</b>\n\n" \
               "<b>Остановить атаку можно введя команду " \
               "/stop или нажав кнопку под сообщением бота " \
               "о начатой атаке.</b>\n\nПомните:\n1. За попытки " \
               "абуза нашего сервиса <b>вы получите блокировку.</b>\n2. " \
               "Остановка атаки обычно занимает какое-то время. Не " \
               "смотря на то, что бот отписал, что атака закончена - " \
               "она может продолжаться в ближайшую минуту.\n3. Если вы " \
               "столкнулись с какой-то проблемой в остановке атаки, то " \
               'следует обратиться в техническую поддержку. (Контакты во ' \
               'вкладке <b>"О боте"</b> стартового сообщения)'

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_help_back_kb())
        except exceptions.MessageNotModified:
            return

    if message_type == 'number_binding':
        text = "<b>Привязка номера</b>\n\n" \
               "Наш бот умеет фильтровать атаки, запущенные " \
               "на номера, которыми владеют подписчики нашего " \
               "бота. Что бы бот так же фильтровал атаки, " \
               "запущенные на ваш номер - необходимо его " \
               "привязать. Для привязки номера используйте " \
               "/link [phone]. Пробелы, тире, плюс и скобки " \
               "игнорируются.\n\nПример: /link <b>+7 123 456 78 90; " \
               "/link +7 (123) 456-78-90</b>"

        try:
            return await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id,
                                               text=text, parse_mode='html',
                                               reply_markup=start_message.generate_help_back_kb())
        except exceptions.MessageNotModified:
            return
