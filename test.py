from light_telegram_bot import Bot, BotPolling, NextHandler
from config import token
import asyncio

async def main():
    bot = await Bot(token)
    
    polling = BotPolling(bot)

    @polling.handler
    async def echo_messages(update):
        if not "message" in update: raise NextHandler()
        message = update["message"]
        await bot.send_message(
            chat_id=message["chat"]["id"], 
            text=message["text"]
            )
    
    @polling.handler
    async def message_edited(update):
        if not "edited_message" in update: raise NextHandler()
        edited_message = update["edited_message"]
        await bot.send_message(
            chat_id=edited_message["chat"]["id"], 
            text="Why did you edit this message??", 
            reply_to_message_id=edited_message["message_id"]
            )

    await polling.start()

asyncio.run(main())