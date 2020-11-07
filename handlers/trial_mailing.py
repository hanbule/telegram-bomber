import threading
import time

from tools import config, misc

import telebot

from telebot import types

bot = telebot.TeleBot(config.bot_token)


def start_mailing(users: list):
    threading.Thread(target=mailing, args=(users,)).start()


def mailing(users: list):
    misc.logger('Mailing',
                f'Mailing trial_force for {len(users)} users from Thinker '
                f'with id Thinker started')

    text = 'Если вы видите это сообщение, значит вы <b>не владеете</b> подпиской на наш сервис. ' \
           f'<b>Почему?</b> Ведь подписка даёт столько преимуществ, ' \
           f'а стоит <b>всего лишь {config.sub_price} ₽</b> (Единоразовый платеж).\n\n' \
           '<b>Конкретно</b>:\n' \
           ' - неограниченные запуски\n' \
           ' - неограниченные циклы\n' \
           ' - расширенная поддержка\n' \
           ' - возможность привязки своего номера для избежания запусков атак через наш сервис на ваш номер\n' \
           ' - отключение рекламы\n\n' \
           'Помните, что наш сервис, хоть и даёт возможность ' \
           'бесплатного использования, но расскрывается в полной ' \
           'мере он на платной подписке!\n\n' \
           'Оплачивая подписку вы помогаете в развитии нашего сервиса, ' \
           'а также продолжаете его существование, так как хостинг, ' \
           'на котором лежит бот, не бесплатный.\n\n' \
           'Оплата может происходить через: <b>QIWI, карты Visa / MK ' \
           '(в том числе украинские), Тинькофф, WebMoney, Сбербанк, Рокетбанк</b> (сервис DonatePay). ' \
           'Если вы решили приобрести полный доступ, то <b>нажимайте по кнопке ниже.</b>'

    markup = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton('Приобрести полный доступ',
                                               callback_data=f"start_message donate")
    markup.add(switch_button)

    for user in users:
        try:
            bot.send_message(user, text, parse_mode='html', reply_markup=markup)
            time.sleep(5)
        except (Exception, BaseException):
            continue

    misc.logger('Mailing',
                f'Mailing trial_force for {len(users)} users from Thinker '
                f'with id Thinker stopped')
