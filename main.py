from itertools import cycle
from better_proxy import Proxy
from os.path import isdir
import asyncio
from os import listdir
from os import mkdir
from os.path import exists
from sys import stderr

from loguru import logger

from core import create_sessions, start_farming
from database import on_startup_database
from utils import monkeypatching

logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')

async def main() -> None:
    await on_startup_database()

    match user_action:
        case 1:
            await create_sessions()

            logger.success('نشست‌ها با موفقیت اضافه شدند')

        case 2:
            tasks: list = [
                asyncio.create_task(coro=start_farming(session_name=current_session_name,
                                                       proxy=next(proxies_cycled) if proxies_cycled else None))
                for current_session_name in session_files
            ]

            await asyncio.gather(*tasks)

        case _:
            logger.error('عملیات انتخاب شده نادرست است')

if __name__ == '__main__':
    if not exists(path='sessions'):
        mkdir(path='sessions')

    with open(file='data/proxies.txt',
              mode='r',
              encoding='utf-8-sig') as file:
        proxies: list[str] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]

    if proxies:
        proxies_cycled: cycle = cycle(proxies)

    else:
        proxies_cycled: None = None

    session_files: list[str] = [current_file[:-8] if current_file.endswith('.session')
                                else current_file for current_file in listdir(path='sessions')
                                if current_file.endswith('.session') or isdir(s=f'sessions/{current_file}')]

    logger.info(f'تعداد {len(session_files)} نشست / {len(proxies)} پراکسی شناسایی شد')

    user_action: int = int(input('\n1. ایجاد نشست'
                                 '\n2. اجرای ربات با نشست‌های موجود'
                                 '\nعملیات خود را انتخاب کنید: '))
    print()

    try:
        import uvloop

        uvloop.run(main())

    except ModuleNotFoundError:
        asyncio.run(main())

    input('\n\nPress Enter to Exit..')
