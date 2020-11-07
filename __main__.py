import logging

import handlers

from aiogram import executor

from tools.misc import database, logger, tools, dp, PATH, startup_task

str(handlers)

logging.basicConfig(filename=f'{PATH}/latest.log',
                    format='\nFUCKING ERROR: \n\n%(message)s\n\n ',
                    level=logging.ERROR
                    )

logger('Bot', f'Loaded {len(tools.load_services())} services')

if __name__ == '__main__':
    executor.start_polling(
        dp, skip_updates=True,
        on_startup=startup_task,
        on_shutdown=database.close_connection
    )
