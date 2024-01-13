import pyrogram
from better_proxy import Proxy
from loguru import logger

from data import config
from database import actions as db_actions

async def create_sessions() -> None:
    while True:
        session_name: str = input('\nنام جلسه را وارد کنید (برای خروج Enter را فشار دهید): ')

        if not session_name:
            return

        while True:
            proxy_str: str = input('پروکسی را وارد کنید (نوع://کاربر:رمز@آدرس:پورت // نوع://آدرس:پورت، برای استفاده بدون '
                                   'پروکسی Enter را فشار دهید): ').replace('https://', 'http://')

            if proxy_str:
                try:
                    proxy: Proxy = Proxy.from_str(
                        proxy=proxy_str
                    )

                    proxy_dict: dict = {
                        'scheme': proxy.protocol,
                        'hostname': proxy.host,
                        'port': proxy.port,
                        'username': proxy.login,
                        'password': proxy.password
                    }

                except ValueError:
                    logger.error(f'پروکسی وارد شده اشتباه است، لطفاً دوباره تلاش کنید')

                else:
                    break

            else:
                proxy: None = None
                proxy_dict: None = None
                break

        session: pyrogram.Client = pyrogram.Client(
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            name=session_name,
            workdir='sessions',
            proxy=proxy_dict
        )

        async with session:
            user_data = await session.get_me()

        logger.success(f'جلسه با موفقیت اضافه شد {user_data.username} | {user_data.first_name} {user_data.last_name}')

        await db_actions.add_session(session_name=session_name,
                                     session_proxy=proxy.as_url if proxy else '')

