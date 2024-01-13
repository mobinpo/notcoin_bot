[![Telegram channel](https://img.shields.io/endpoint?url=https://runkit.io/damiankrawczyk/telegram-badge/branches/master?url=https://t.me/n4z4v0d)](https://t.me/n4z4v0d)
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/better-automation.svg)](https://www.python.org/downloads/release/python-3116/)
[![works badge](https://cdn.jsdelivr.net/gh/nikku/works-on-my-machine@v0.2.0/badge.svg)](https://github.com/nikku/works-on-my-machine)  

![alt text](https://i.imgur.com/PDYwSJ9.png)

### Functionality
+ _Multithreading_
+ _Proxy binding to the session_
+ _Auto-purchase items when there is enough money (energy boost, speed boost, click boost)_
+ _Random sleep time between clicks_
+ _Random number of clicks per request_
+ _Support for tdata / pyrogram .session / telethon .session_

### data/config.py  
_**API_ID / API_HASH** - Platform data to launch a Telegram session (default - Android)  
**MIN_CLICKS_COUNT** - Minimum number of clicks per request (calculated without a multiplier, e.g., with a x9 multiplier: 1 click equals 9 coins, not one)  
**AUTO_BUY_ENERGY_BOOST** - Automatically buy Energy Boost when the balance is reached (True / False)  
**AUTO_BUY_SPEED_BOOST** - Automatically buy Speed Boost when the balance is reached (True / False)  
**AUTO_BUY_CLICK_BOOST** - Automatically buy Click Boost when the balance is reached (True / False)  
**USE_PROXY_FROM_FILE** - Whether to use proxies from the file data/proxies.txt for accounts not tied to proxies (True / False)  
**SLEEP_BETWEEN_CLICK** - Delay range between clicks (in seconds)
**SLEEP_BEFORE_BUY_MERGE** - Delay range before buying boosts (in seconds)
**SLEEP_BEFORE_ACTIVATE_FREE_BUFFS** - Delay range before activating daily boosts (in seconds)
**SLEEP_BEFORE_ACTIVATE_TURBO** - Delay range before activating Turbo (in seconds)_  

# DONATE (_any evm_) - 0xDEADf12DE9A24b47Da0a43E1bA70B8972F5296F2
# DONATE (_sol_) - 2Fw2wh1pN77ELg6sWnn5cZrTDCK5ibfnKymTuCXL8sPX
