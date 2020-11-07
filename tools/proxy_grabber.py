import datetime
import random
import time

import requests

from tools import config
from handlers import text


def grab(logger, database, token):
    if text.active_grabber:
        logger('ProxyGrabber', 'Getting proxys from Proxoid.net')
    else:
        return

    proxys = [proxy for proxy in requests.get(
        "https://proxoid.net/api/getProxy",
        params={
            "key": token,
            "countries": ",".join(["RU", "UA", "UZ", "BY", "DE", "NL", "PH"]),
            "types": ",".join(["https"]),
            "level": ",".join(["transparent", "high", "anonymous"]),
            "speed": 2000,
            "count": 0
        }).text.splitlines()]

    [proxys.append(proxy) for proxy in database.get_proxys()]

    logger('ProxyGrabber', f'Check {len(proxys)} proxys...')

    random.shuffle(proxys)
    live_count = 0
    dead_count = 0
    for proxy in proxys:
        time.sleep(5)
        try:
            timestamp = datetime.datetime.now().timestamp()
            try:
                proxy_url = "http://" + proxy
            except TypeError:
                break

            requests.get('https://ramziv.com/ip', timeout=3,
                         proxies=dict(http=proxy_url,
                                      https=proxy_url))
            ping = round((datetime.datetime.now().timestamp() - timestamp) * 1000)
            if ping < config.max_proxy_ping:
                live_count += 1
                if proxy not in database.get_proxys():
                    database.append_proxy(True, proxy)
                logger('ProxyGrabber', f'Find proxy ({live_count}/{dead_count}): {proxy} with ping {ping}ms')
                continue
            else:
                dead_count += 1
                if proxy in database.get_proxys():
                    database.append_proxy(False, proxy)
                continue

        except (Exception, BaseException, requests.exceptions.ConnectionError):
            dead_count += 1
            if proxy in database.get_proxys():
                database.append_proxy(False, proxy)
            continue
    text.active_grabber = False
    logger('ProxyGrabber', 'Good bye!')
