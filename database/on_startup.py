import aiosqlite

async def on_startup_database() -> None:
    # برقراری اتصال به پایگاه داده
    async with aiosqlite.connect(database='database/sessions.db') as db:
        # اجرای دستور SQL برای ایجاد جدول در صورت عدم وجود
        await db.execute(sql="""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            session_name TEXT,
            session_proxy TEXT
        );
        """)
        # ذخیره تغییرات در پایگاه داده
        await db.commit()
