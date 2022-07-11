from light_telegram_bot import Bot, BotPolling, NextHandler
from config import token

async def main():
    bot = await Bot(token)
    
    polling = BotPolling(bot)

    @polling.handler
    async def echo_messages(update):
        if hasattr(update, "message"):
        	raise NextHandler()
        message = update.message
        await bot.send_message(chat_id=message.from_.id, text=message.text)

    await polling.start()

asyncio.run(main())