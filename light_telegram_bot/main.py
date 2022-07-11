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
                response_object = _BotObject(response_data)
                if response_object.ok:
                    return response_object.result
                else:
                    raise bot.get_http_exception(response_object.error_code)(response_object.description)

        function.__name__ = attr
        function.__qualname__ = self.__class__.__qualname__ + "." + attr
        method = MethodType(function, self)
        self.cache[attr] = method
        return method

    def get_http_exception(self, number:int):
        if number in self._http_exceptions:
            return self._http_exceptions[number]
        else:
            obj = type(f"TelegramError{number}", (TelegramError,), {})
            self._http_exceptions[number] = obj
            return obj


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
                    self._offset = updates[-1].update_id+1
                for update in updates:
                    for handler in self._handlers:
                        try:
                            await handler(update)
                        except NextHandler:
                            pass
                        else:
                            break
        except Exception:
            raise LightTelegramBotPollingError()
                
    def handler(self, f):
        self._handlers.append(f)
    
class _BotObject:
    def __init__(self, scheme: Union[dict, list]):
        self._scheme = scheme
        self._cache = {}

    @classmethod
    def create_new_object(cls, value):
        if isinstance(value, (dict, list)):
            new_object = cls(value)
        else:
            new_object = value
        return new_object
    
    def __str__(self):
        return str(self._scheme)

    def __getattr__(self, attr: str):
        if attr.endswith("_"):
            attr = attr[:-1]
        if attr in self._cache:
            return self._cache[attr]
        try:
            value = self._scheme[attr]
        except KeyError:
            return super().__getattribute__(attr)

        new_object = self.create_new_object(value)
        self._cache[attr] = new_object
        return new_object

    def __getitem__(self, item: int):
        if not isinstance(item, int):
            raise TypeError()

        if item in self._cache:
            return self._cache[item]

        value = self._scheme[item]

        new_object = self.create_new_object(value)
        self._cache[item] = new_object
        return new_object
    
    def __bool__(self):
        return bool(self._scheme)