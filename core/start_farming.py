import asyncio
from base64 import b64decode
from math import floor
from pathlib import Path
from random import randint
from time import time
from urllib.parse import unquote

import aiohttp
from TGConvertor.manager.exceptions import ValidationError
from TGConvertor.manager.manager import SessionManager
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from loguru import logger
from opentele.exception import TFileNotFound, OpenTeleException
from pyuseragents import random as random_useragent
from telethon import TelegramClient
from telethon import functions
from telethon.sessions import StringSession

from data import config
from database import actions as db_actions
from exceptions import InvalidSession, TurboExpired
from utils import eval_js, read_session_json_file
from .headers import headers


class Farming:
    def __init__(self, session_name: str):
        self.session_name: str = session_name

    async def get_access_token(self, client: aiohttp.ClientSession, tg_web_data: str) -> str:
        r: None = None

        while True:
            try:
                r: aiohttp.ClientResponse = await client.post(url='https://clicker-api.joincommunity.xyz/auth/'
                                                                  'webapp-session',
                                                              json={
                                                                  'webAppData': tg_web_data
                                                              },
                                                              verify_ssl=False)

                return (await r.json(content_type=None))['data']['accessToken']

            except Exception as error:
                if r:
                    logger.error(f'{self.session_name} | خطای ناشناخته در دریافت توکن دسترسی: {error}, '
                                 f'پاسخ: {await r.text()}')
                else:
                    logger.error(f'{self.session_name} | خطای ناشناخته در دریافت توکن دسترسی: {error}')

    async def get_tg_web_data(self, session_proxy: str | None) -> str | None:
        while True:
            try:
                if session_proxy:
                    try:
                        proxy: Proxy = Proxy.from_str(
                            proxy=session_proxy
                        )

                        proxy_dict: dict = {
                            'proxy_type': proxy.protocol,
                            'addr': proxy.host,
                            'port': proxy.port,
                            'username': proxy.login,
                            'password': proxy.password
                        }

                    except ValueError:
                        proxy_dict: None = None

                else:
                    proxy_dict: None = None

                session: any = None

                try:
                    session = SessionManager.from_tdata_folder(folder=Path(f'sessions/{self.session_name}'))

                except (ValidationError, FileNotFoundError, TFileNotFound, OpenTeleException):
                    pass

                if not session:
                    for action in [SessionManager.from_pyrogram_file, SessionManager.from_telethon_file]:
                        try:
                            session = await action(file=Path(f'sessions/{self.session_name}.session'))

                        except (ValidationError, FileNotFoundError, TFileNotFound, OpenTeleException):
                            pass

                        else:
                            break

                if not session:
                    raise InvalidSession(self.session_name)

                telethon_string: str = session.to_telethon_string()
                platform_data: dict = await read_session_json_file(session_name=self.session_name)

                client = TelegramClient(session=StringSession(string=telethon_string),
                                        api_id=platform_data.get('api_id', config.API_ID),
                                        api_hash=platform_data.get('api_hash', config.API_HASH),
                                        device_model=platform_data.get('device_model', None),
                                        system_version=platform_data.get('system_version', None),
                                        app_version=platform_data.get('app_version', None),
                                        lang_code=platform_data.get('lang_code', 'en'),
                                        system_lang_code=platform_data.get('system_lang_code', 'en'),
                                        proxy=proxy_dict)

                try:
                    await client.connect()

                    if not await client.is_user_authorized():
                        raise InvalidSession(self.session_name)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    raise error

                finally:
                    await client.disconnect()

                async with TelegramClient(session=StringSession(string=telethon_string),
                                          api_id=platform_data.get('api_id', config.API_ID),
                                          api_hash=platform_data.get('api_hash', config.API_HASH),
                                          device_model=platform_data.get('device_model', None),
                                          system_version=platform_data.get('system_version', None),
                                          app_version=platform_data.get('app_version', None),
                                          lang_code=platform_data.get('lang_code', 'en'),
                                          system_lang_code=platform_data.get('system_lang_code', 'en'),
                                          proxy=proxy_dict) as client:
                    #await client.send_message(entity='notcoin_bot',
                    #                          message='/start r_577441_3319074')
                    # noinspection PyTypeChecker
                    result = await client(functions.messages.RequestWebViewRequest(
                        peer='notcoin_bot',
                        bot='notcoin_bot',
                        platform='android',
                        from_bot_menu=False,
                        url='https://clicker.joincommunity.xyz/clicker',
                    ))
                    auth_url: str = result.url

                    tg_web_data: str = unquote(string=unquote(
                        string=auth_url.split(sep='tgWebAppData=',
                                              maxsplit=1)[1].split(sep='&tgWebAppVersion',
                                                                   maxsplit=1)[0]
                    ))

                return tg_web_data

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f'{self.session_name} | خطای ناشناخته در فرآیند احراز هویت: {error}')

    async def get_profile_data(self, client: aiohttp.ClientSession) -> dict:
        while True:
            try:
                r: aiohttp.ClientResponse = await client.get(
                    url='https://clicker-api.joincommunity.xyz/clicker/profile',
                    verify_ssl=False)

                if not (await r.json(content_type=None)).get('ok'):
                    logger.error(f'{self.session_name} | پاسخ ناشناخته در دریافت داده‌های پروفایل، '
                                 f'پاسخ: {await r.text()}')
                    continue

                return await r.json(content_type=None)

            except Exception as error:
                logger.error(f'{self.session_name} | خطای ناشناخته در دریافت داده‌های پروفایل: {error}')

    async def send_clicks(self, client: aiohttp.ClientSession, clicks_count: int, tg_web_data: str,
                          balance: int, total_coins: str | int, click_hash: str | None = None,
                          turbo: bool | None = None) -> tuple[int | None, str | None, bool | None]:
        while True:
            try:
                json_data: dict = {
                    'count': clicks_count,
                    'webAppData': tg_web_data
                }

                if click_hash:
                    json_data['hash']: str = click_hash

                if turbo:
                    json_data['turbo']: bool = True

                r: aiohttp.ClientResponse = await client.post(
                    url='https://clicker-api.joincommunity.xyz/clicker/core/click',
                    json=json_data,
                    verify_ssl=False)

                if (await r.json(content_type=None)).get('data') \
                        and isinstance((await r.json(content_type=None))['data'], dict) \
                        and (await r.json(content_type=None))['data'].get('message', '') == 'Turbo mode is expired':
                    raise TurboExpired()

                if (await r.json(content_type=None)).get('data') \
                        and isinstance((await r.json(content_type=None))['data'], dict) \
                        and (await r.json(content_type=None))['data'].get('message', '') == 'Try later':
                    await asyncio.sleep(delay=1)
                    continue

                if (await r.json(content_type=None)).get('ok'):
                    logger.success(f'{self.session_name} | Click با موفقیت انجام شد | موجودی: '
                                   f'{balance + clicks_count} (+{clicks_count}) | تعداد کل سکه‌ها: {total_coins}')

                    next_hash: str | None = eval_js(
                        function=b64decode(s=(await r.json())['data'][0]['hash'][0]).decode())

                    return balance + clicks_count, next_hash, (await r.json())['data'][0]['turboTimes'] > 0

                logger.error(f'{self.session_name} | Click با موفقیت انجام نشد، پاسخ: {await r.text()}')
                return None, None, None

            except Exception as error:
                logger.error(f'{self.session_name} | خطای ناشناخته در تلاش برای انجام Click: {error}')

    async def get_merged_list(self, client: aiohttp.ClientSession) -> dict | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.get(
                url='https://clicker-api.joincommunity.xyz/clicker/store/merged')

            if (await r.json(content_type=None)).get('ok'):
                return await r.json(content_type=None)

            logger.error(f'{self.session_name} | دریافت لیست محصولات با شکست مواجه شد، پاسخ: {await r.text()}')

            return

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | خطای ناشناخته در دریافت لیست محصولات: {error}, '
                             f'پاسخ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | خطای ناشناخته در دریافت لیست محصولات: {error}')

            return

    async def buy_item(self, client: aiohttp.ClientSession, item_id: int | str) -> bool:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/store/'
                                                              f'buy/{item_id}',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            if (await r.json(content_type=None)).get('ok'):
                return True

            logger.error(f'{self.session_name} | پاسخ ناشناخته در فرآیند خرید: {await r.text()}')

            return False

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | خطای ناشناخته در فرآیند خرید: {error}, '
                             f'پاسخ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | خطای ناشناخته در فرآیند خرید: {error}')

            return False

    async def activate_turbo(self, client: aiohttp.ClientSession) -> int | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/core/'
                                                              'active-turbo',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            return (await r.json(content_type=None))['data'][0].get('multiple', 1)

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | خطای ناشناخته در فعال‌سازی Turbo: {error}, '
                             f'پاسخ: {await r.text()}')

            else:

                logger.error(f'{self.session_name} | خطای ناشناخته در فعال‌سازی Turbo: {error}')

            return

    async def activate_task(self,
                            client: aiohttp.ClientSession,
                            task_id: int | str) -> bool | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/task/'
                                                              f'{task_id}',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            if (await r.json(content_type=None)).get('ok'):
                return True

            logger.error(f'{self.session_name} | پاسخ ناشناخته در فعال‌سازی Task {task_id}: {await r.text()}')

            return False

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | خطای ناشناخته در فعال‌سازی Task {task_id}: {error}, '
                             f'پاسخ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | خطای ناشناخته در فعال‌سازی Task {task_id}: {error}')

            return False

    async def get_free_buffs_data(self,
                                  client: aiohttp.ClientSession) -> tuple[bool, bool]:
        r: None = None
        max_turbo_times: int = 3
        max_full_energy_times: int = 3

        turbo_times_count: int = 0
        full_energy_times_count: int = 0

        try:
            r: aiohttp.ClientResponse = await client.get(url=f'https://clicker-api.joincommunity.xyz/clicker/task/'
                                                             'combine-completed')

            for current_buff in (await r.json(content_type=None))['data']:
                match current_buff['taskId']:
                    case 3:
                        max_turbo_times: int = current_buff['task']['max']

                        if current_buff['task']['status'] == 'active':
                            turbo_times_count += 1

                    case 2:
                        max_full_energy_times: int = current_buff['task']['max']

                        if current_buff['task']['status'] == 'active':
                            full_energy_times_count += 1

            return max_turbo_times > turbo_times_count, max_full_energy_times > full_energy_times_count

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | خطای ناشناخته در دریافت وضعیت بوف‌های رایگان: '
                             f'{error}, پاسخ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | خطای ناشناخته در دریافت وضعیت بوف‌های رایگان: '
                             f'{error}')

            return False, False

    async def start_farming(self,
                            proxy: str | None = None):
        session_proxy: str = await db_actions.get_session_proxy_by_name(session_name=self.session_name)

        if not session_proxy and config.USE_PROXY_FROM_FILE:
            session_proxy: str = proxy

        access_token_created_time: float = 0
        click_hash: None | str = None
        active_turbo: bool = False
        turbo_multiplier: int = 1

        while True:
            try:
                async with aiohttp.ClientSession(
                        connector=ProxyConnector.from_url(url=session_proxy) if session_proxy else None,
                        headers={
                            **headers,
                            'user-agent': random_useragent()
                        }) as client:
                    while True:
                        try:
                            if time() - access_token_created_time >= 1800:
                                tg_web_data: str = await self.get_tg_web_data(session_proxy=session_proxy)

                                access_token: str = await self.get_access_token(client=client,
                                                                                tg_web_data=tg_web_data)
                                client.headers['Authorization']: str = f'Bearer {access_token}'
                                access_token_created_time: float = time()

                            profile_data: dict = await self.get_profile_data(client=client)

                            if not active_turbo:
                                if config.MIN_CLICKS_COUNT > floor(profile_data['data'][0]['availableCoins'] \
                                                                   / profile_data['data'][0]['multipleClicks']):
                                    logger.info(f'{self.session_name} | موجودی کافی برای کلیک نیست')
                                    continue

                            if floor(profile_data['data'][0]['availableCoins'] \
                                     / profile_data['data'][0]['multipleClicks']) < 160:
                                max_clicks_count: int = floor(profile_data['data'][0]['availableCoins'] \
                                                              / profile_data['data'][0]['multipleClicks'])

                            else:
                                max_clicks_count: int = 160

                            clicks_count: int = randint(a=config.MIN_CLICKS_COUNT,
                                                        b=max_clicks_count) \
                                                * profile_data['data'][0]['multipleClicks'] * turbo_multiplier

                            try:
                                new_balance, click_hash, have_turbo = await self.send_clicks(client=client,
                                                                                             clicks_count=clicks_count,
                                                                                             tg_web_data=tg_web_data,
                                                                                             balance=
                                                                                             profile_data['data'][0][
                                                                                                 'balanceCoins'],
                                                                                             total_coins=
                                                                                             profile_data['data'][0][
                                                                                                 'totalCoins'],
                                                                                             click_hash=click_hash,
                                                                                             turbo=active_turbo)

                            except TurboExpired:
                                active_turbo: bool = False
                                turbo_multiplier: int = 1
                                continue

                            if have_turbo:
                                random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_TURBO[0],
                                                                 b=config.SLEEP_BEFORE_ACTIVATE_TURBO[1])

                                logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} '
                                            f'ثانیه قبل از فعال‌سازی Turbo')

                                await asyncio.sleep(delay=random_sleep_time)

                                turbo_multiplier: int | None = await self.activate_turbo(client=client)

                                if turbo_multiplier:
                                    logger.success(f'{self.session_name} | Turbo با موفقیت فعال شد: '
                                                   f'x{turbo_multiplier}')
                                    active_turbo: bool = True
                                    continue

                                else:
                                    turbo_multiplier: int = 1

                            if new_balance:
                                merged_data: dict | None = await self.get_merged_list(client=client)

                                if merged_data:
                                    for current_merge in merged_data['data']:
                                        match current_merge['id']:
                                            case 1:
                                                if not config.AUTO_BUY_ENERGY_BOOST:
                                                    continue

                                                energy_price: int | None = current_merge['price']

                                                if new_balance >= energy_price \
                                                        and current_merge['max'] > current_merge['count']:
                                                    sleep_before_buy_merge: int = randint(
                                                        a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                        b=config.SLEEP_BEFORE_BUY_MERGE[1]
                                                    )
                                                    logger.info(f'{self.session_name} | خواب به مدت {sleep_before_buy_merge} '
                                                                f'ثانیه قبل از خرید Energy Boost')

                                                    await asyncio.sleep(delay=sleep_before_buy_merge)

                                                    if await self.buy_item(client=client,
                                                                           item_id=1):
                                                        logger.success(f'{self.session_name} | Energy Boost با موفقیت خریداری شد')
                                                        continue

                                            case 2:
                                                if not config.AUTO_BUY_SPEED_BOOST:
                                                    continue

                                                speed_price: int | None = current_merge['price']

                                                if new_balance >= speed_price \
                                                        and current_merge['max'] > current_merge['count']:
                                                    sleep_before_buy_merge: int = randint(
                                                        a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                        b=config.SLEEP_BEFORE_BUY_MERGE[1]
                                                    )
                                                    logger.info(f'{self.session_name} | خواب به مدت {sleep_before_buy_merge} '
                                                                f'ثانیه قبل از خرید Speed Boost')

                                                    await asyncio.sleep(delay=sleep_before_buy_merge)

                                                    if await self.buy_item(client=client,
                                                                           item_id=2):
                                                        logger.success(
                                                            f'{self.session_name} | Speed Boost با موفقیت خریداری شد')
                                                        continue

                                            case 3:
                                                if not config.AUTO_BUY_CLICK_BOOST:
                                                    continue

                                                click_price: int | None = current_merge['price']

                                                if new_balance >= click_price \
                                                        and current_merge['max'] > current_merge['count']:
                                                    sleep_before_buy_merge: int = randint(
                                                        a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                        b=config.SLEEP_BEFORE_BUY_MERGE[1])
                                                    logger.info(
                                                        f'{self.session_name} | خواب به مدت {sleep_before_buy_merge} ثانیه '
                                                        f'قبل از خرید Speed Boost')

                                                    await asyncio.sleep(delay=sleep_before_buy_merge)

                                                    if await self.buy_item(client=client,
                                                                           item_id=3):
                                                        logger.success(
                                                            f'{self.session_name} | Click Boost با موفقیت خریداری شد')
                                                        continue

                                            case 4:
                                                pass

                            free_daily_turbo, free_daily_full_energy = await self.get_free_buffs_data(client=client)

                            if free_daily_turbo:
                                random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[0],
                                                                 b=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[1])

                                logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} '
                                            f'ثانیه قبل از درخواست Turbo روزانه')

                                await asyncio.sleep(delay=random_sleep_time)

                                if await self.activate_task(client=client,
                                                            task_id=3):
                                    logger.success(f'{self.session_name} | Turbo روزانه با موفقیت درخواست شد')

                                    random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_TURBO[0],
                                                                     b=config.SLEEP_BEFORE_ACTIVATE_TURBO[1])

                                    logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} '
                                                f'ثانیه قبل از فعال‌سازی Turbo')

                                    await asyncio.sleep(delay=random_sleep_time)

                                    turbo_multiplier: int | None = await self.activate_turbo(client=client)

                                    if turbo_multiplier:
                                        logger.success(f'{self.session_name} | Turbo با موفقیت فعال شد: '
                                                       f'x{turbo_multiplier}')
                                        active_turbo: bool = True
                                        continue

                                    else:
                                        turbo_multiplier: int = 1

                            elif free_daily_full_energy:
                                random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[0],
                                                                 b=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[1])

                                logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} '
                                            f'ثانیه قبل از فعال‌سازی Full Energy روزانه')

                                await asyncio.sleep(delay=random_sleep_time)

                                if await self.activate_task(client=client,
                                                            task_id=2):
                                    logger.success(f'{self.session_name} | Full Energy روزانه با موفقیت درخواست شد')

                        except InvalidSession as error:
                            raise error

                        except Exception as error:
                            logger.error(f'{self.session_name} | خطای ناشناخته: {error}')

                            random_sleep_time: int = randint(a=config.SLEEP_BETWEEN_CLICK[0],
                                                             b=config.SLEEP_BETWEEN_CLICK[1])

                            logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} ثانیه')
                            await asyncio.sleep(delay=random_sleep_time)

                        else:
                            random_sleep_time: int = randint(a=config.SLEEP_BETWEEN_CLICK[0],
                                                             b=config.SLEEP_BETWEEN_CLICK[1])

                            logger.info(f'{self.session_name} | در حال خواب به مدت {random_sleep_time} ثانیه')
                            await asyncio.sleep(delay=random_sleep_time)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f'{self.session_name} | خطای ناشناخته: {error}')


async def start_farming(session_name: str,
                        proxy: str | None = None) -> None:
    try:
        await Farming(session_name=session_name).start_farming(proxy=proxy)

    except InvalidSession:
        logger.error(f'{session_name} | جلسه نامعتبر است')
