import aiosqlite

async def add_session(session_name: str, session_proxy: str = '') -> None:
    # برقراری اتصال به پایگاه داده
    async with aiosqlite.connect(database='database/sessions.db') as db:
        # اجرای دستور SQL برای افزودن جلسه به جدول
        await db.execute(sql='INSERT INTO sessions (session_name, session_proxy) VALUES (?, ?)',
                         parameters=(session_name, session_proxy))
        # ذخیره تغییرات در پایگاه داده
        await db.commit()

async def get_session_proxy_by_name(session_name: str) -> str | None:
    # برقراری اتصال به پایگاه داده
    async with aiosqlite.connect(database='database/sessions.db') as db:
        # اجرای دستور SQL برای دریافت پروکسی جلسه بر اساس نام جلسه
        async with db.execute(sql='SELECT session_proxy FROM sessions WHERE session_name = ?',
                              parameters=(session_name,)) as cursor:
            # دریافت نتیجه از کرسور
            result = await cursor.fetchone()
            # اگر نتیجه وجود داشته باشد، پروکسی را برگردان؛ در غیر این صورت None
            return result[0] if result else None
