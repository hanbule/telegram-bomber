import psycopg2

from tools.config import db_settings, trial_start_count as config_trial_start_count, creators, support
from tools.tools import get_time
from tools.misc import logger

conn = psycopg2.connect(**db_settings)
conn.set_session(autocommit=True)
cursor = conn.cursor()


def edit_user(telegram_id: int, what_to_edit: str, variable, what_to_edit2: str = None, variable2=None,
              what_to_edit3: str = None, variable3=None, what_to_edit4: str = None, variable4=None):
    cursor.execute(f"UPDATE users SET {what_to_edit} = {variable} WHERE telegram_id = {telegram_id}")
    if what_to_edit2 is not None and variable2 is not None:
        cursor.execute(f"UPDATE users SET {what_to_edit2} = {variable2} WHERE telegram_id = {telegram_id}")
    if what_to_edit3 is not None and variable3 is not None:
        cursor.execute(f"UPDATE users SET {what_to_edit3} = {variable3} WHERE telegram_id = {telegram_id}")
    if what_to_edit4 is not None and variable4 is not None:
        cursor.execute(f"UPDATE users SET {what_to_edit4} = {variable4} WHERE telegram_id = {telegram_id}")


def create_user(telegram_id: int, full_name: str, user_name: str, reg_time: int):
    cursor.execute(f"INSERT INTO users (telegram_id, full_name, user_name, reg_time, trial_start_count)"
                   f"VALUES ({telegram_id}, '{full_name}', '{user_name}', {reg_time}, {config_trial_start_count})")


def get_users():
    try:
        # Все айди
        cursor.execute("SELECT telegram_id FROM users")
        telegram_ids = [user[0] for user in cursor.fetchall()]
        # Крутые с подпиской
        cursor.execute("SELECT telegram_id FROM users WHERE sub_status = true")
        sub_ids = [user[0] for user in cursor.fetchall()]
        # Нищие без подписки
        cursor.execute("SELECT telegram_id FROM users WHERE sub_status = false")
        trial_ids = [user[0] for user in cursor.fetchall()]
        # Крутые с рассылкой
        cursor.execute("SELECT telegram_id FROM users WHERE mailing_status = true")
        mailing_ids = [user[0] for user in cursor.fetchall()]
        # Номерочки
        cursor.execute("SELECT attached_number FROM users WHERE attached_number IS NOT NULL")
        attached_phone_numbers = [user[0] for user in cursor.fetchall()]
        # Забаненные пидорасы!
        cursor.execute("SELECT telegram_id FROM users WHERE ban_status = true ")
        banned_ids = [user[0] for user in cursor.fetchall()]
        # админы - пидорасы!
        admin_ids = list()
        [admin_ids.append(user) if (
            get_user(user)['user_name'] in creators or get_user(user)['user_name'] == support
        ) else str() for user in telegram_ids]

        output = {
            "telegram_ids": telegram_ids,
            "sub_ids": sub_ids,
            "trial_ids": trial_ids,
            "mailing_ids": mailing_ids,
            "attached_phone_numbers": attached_phone_numbers,
            "banned_ids": banned_ids,
            "admin_ids": admin_ids
        }

        return output

    except (psycopg2.ProgrammingError, IndexError):
        return get_users()


def get_user(telegram_id: int):
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = '{telegram_id}'")
    x = cursor.fetchall()

    telegram_id = [user[6] for user in x]
    full_name = [user[0] for user in x]
    user_name = [user[7] for user in x]
    reg_time = [user[1] for user in x]
    buy_time = [user[2] for user in x]
    sub_status = [user[3] for user in x]
    ban_status = [user[4] for user in x]
    trial_start_count = [user[5] for user in x]
    proxy_status = [user[8] for user in x]
    mailing_status = [user[9] for user in x]
    timeout = [user[10] for user in x]
    pause = [user[11] for user in x]
    attached_phone_number = [user[12] for user in x]
    default_cycles = [user[13] for user in x]

    output = {
        "telegram_id": telegram_id[0],
        "full_name": full_name[0],
        "user_name": user_name[0] if user_name[0] != 'None' else None,
        "reg_time": reg_time[0],
        "buy_time": buy_time[0],
        "sub_status": sub_status[0],
        "ban_status": ban_status[0],
        "trial_start_count": trial_start_count[0],
        "settings": {
            "proxy_status": proxy_status[0],
            "mailing_status": mailing_status[0],
            "timeout": timeout[0],
            "pause": pause[0],
            "attached_phone_number": attached_phone_number[0],
            "default_cycles": default_cycles[0]
        }
    }

    return output


def get_proxys():
    cursor.execute("SELECT proxy FROM proxys")
    proxys = [proxy[0] for proxy in cursor.fetchall()]
    return proxys


def delete_user(telegram_id: int):
    cursor.execute(f"DELETE FROM users WHERE telegram_id = {telegram_id}")


def ban_user(telegram_id: int):
    # cursor.execute(f"UPDATE users SET ban_status = true, sub_status = false, "
    #               f"trial_start_count = 0 WHERE telegram_id = {telegram_id}")

    edit_user(telegram_id, 'ban_status', 'true', 'sub_status', 'false', 'trial_start_count', '0')


def unban_user(telegram_id: int):
    # cursor.execute(f"UPDATE users SET ban_status = false, sub_status = false, "
    #               f"trial_start_count = {config_trial_start_count} WHERE telegram_id = {telegram_id}")

    edit_user(telegram_id, 'ban_status', 'false', 'sub_status', 'false', 'trial_start_count', config_trial_start_count)


def give_sub(telegram_id: int):
    # cursor.execute(f"UPDATE users SET sub_status = true, trial_start_count = 0,"
    #               f"buy_time = {get_time()} WHERE telegram_id = {telegram_id}")

    edit_user(telegram_id, 'sub_status', 'true',
              'trial_start_count', '0', 'buy_time',
              get_time(), 'ban_status', 'false')


def update_user(telegram_id: int, full_name: str, user_name: (str, None)):
    cursor.execute(f"UPDATE users SET full_name = '{full_name}', user_name = '{user_name}' "
                   f"WHERE telegram_id = '{telegram_id}'")

    # edit_user(telegram_id, 'full_name', full_name, 'user_name', user_name)


def change_mailing_status(telegram_id: int, status: bool):
    edit_user(telegram_id, 'mailing_status', "true" if status else "false")


def change_timeout(telegram_id: int, timeout: int):
    edit_user(telegram_id, 'timeout', timeout)


def change_pause(telegram_id: int, pause: int):
    edit_user(telegram_id, 'pause', pause)


def attach_phone_number(telegram_id: int, phone_number: (int, None)):
    if phone_number is None:
        phone_number = 'null'
    edit_user(telegram_id, 'attached_number', phone_number)


def change_cycles(telegram_id: int, cycles: int):
    edit_user(telegram_id, 'default_cycles', cycles)


def edit_pause(telegram_id: int, edit: str):
    current_pause = get_user(telegram_id)['settings']['pause']
    if edit == "+":
        current_pause += 1
    else:
        current_pause -= 1

    if -1 < current_pause < 11:
        cursor.execute(f"UPDATE users SET pause = pause {edit} 1 WHERE telegram_id = {telegram_id}")
        return True
    else:
        return False


def edit_cycles(telegram_id: int, edit: str):
    current_cycles = get_user(telegram_id)['settings']['default_cycles']

    if current_cycles == 1 and edit == '+':
        cursor.execute(
            f"UPDATE users SET default_cycles = default_cycles {edit} 4 WHERE telegram_id = {telegram_id}"
        )
        return True
    elif edit == '+':
        current_cycles += 5
    else:
        current_cycles -= 5

    if current_cycles < 1 and edit == "-":
        cursor.execute(f"UPDATE users SET default_cycles = 1 WHERE telegram_id = {telegram_id}")
        return False

    if -4 < current_cycles <= 100:
        cursor.execute(
            f"UPDATE users SET default_cycles = default_cycles {edit} 5 WHERE telegram_id = {telegram_id}"
        )
        return True
    else:
        return False


def edit_timeout(telegram_id: int, edit: int):
    current_timeout = get_user(telegram_id)['settings']['timeout']

    if edit == "+":
        current_timeout += 3
    else:
        current_timeout -= 3

    if 0 < current_timeout <= 15:
        cursor.execute(f"UPDATE users SET timeout = timeout {edit} 3 WHERE telegram_id = {telegram_id}")
        return True
    else:
        return False


def close_connection(dispatcher):
    str(dispatcher)
    logger('Database', 'Connection closed')
    conn.close()


def minus_attack(telegram_id):
    current_attacks = get_user(telegram_id)['trial_start_count']

    if current_attacks > 0:
        cursor.execute(f"UPDATE users SET trial_start_count = trial_start_count - 1 WHERE telegram_id = {telegram_id}")
    else:
        pass


def append_proxy(live: bool, proxy: str):
    if live:
        cursor.execute(f"INSERT INTO proxys (proxy) VALUES ('{proxy}')")
    if not live:
        cursor.execute(f"DELETE FROM proxys WHERE proxy = '{proxy}'")
