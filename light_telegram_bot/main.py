from traceback import print_exc
import aiohttp
from typing import Union
from types import MethodType

url = "https://api.telegram.org"

def snake_case_to_camel_case(shake_case_str:str):
    return "".join((symb.capitalize() for symb in shake_case_str.split("_")))

class TelegramError(Exception): pass

class LightTelegramBotError(Exception):
    def __init__(self):
        self.args = ("Inner light_telegram_bot error",)

class LightTelegramBotPollingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = (*self.args, "Polling error")

class NextHandler(Exception):
    def __init__(self):
        self.args = ("don't use this error outside of light_telegram_bot handler",)

class Bot:
    def __init__(self, token: str):
        self._http_exceptions = {}
        self._token = token
        self.cache = {}

    async def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._session = aiohttp.ClientSession(url)
        obj.__init__(*args, **kwargs)
        return obj

    def __getattr__(self, attr: str):
        if attr in self.cache:
            return self.cache[attr]

        url = "/bot"+self._token+"/"+snake_case_to_camel_case(attr)
        async def function(bot, **kwargs):
            async with bot._session.get(url, params=kwargs) as response:
                response_data = await response.json()
                if response_data["ok"]:
                    return response_data["result"]
                else:
                    raise bot.get_http_exception(response_data["error_code"])(
                    response_data["description"]
                    )

        function.__name__ = attr
        function.__qualname__ = self.__class__.__qualname__ + "." + attr
        method = MethodType(function, self)
        self.cache[attr] = method
        return method

    def get_http_exception(self, number:int):
        if number in self._http_exceptions:
            return self._http_exceptions[number]
        else:
            HttpException = type(f"TelegramError{number}", (TelegramError,), {})
            self._http_exceptions[number] = HttpException
            return HttpException


class BotPolling:
    def __init__(self, bot, start_offset=0):
        self._handlers = []
        self._bot = bot
        self._offset = start_offset

    async def start(self, timeout=60, **kwargs):
        try:
            while 1:
                updates = await self._bot.get_updates(timeout=timeout, offset=self._offset, **kwargs)
                if updates:
                    self._offset = updates[-1]["update_id"]+1
                for update in updates:
                    for handler in self._handlers:
                        try:
                            await handler(update)
                        except NextHandler:
                            pass
                        else:
                            break
        except Exception:
            print_exc()
            raise LightTelegramBotPollingError()
                
    def handler(self, f):
        self._handlers.append(f)
    