from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from services.ton_services import check_wallet, check_mnemonics
from tonsdk.utils._exceptions import InvalidAddressError
from tonsdk.crypto.exceptions import InvalidMnemonicsError
from isHex import isHex


# Checking callback from user for [id+space+bet]
class IsEnemy(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        space = callback.data.find(' ')
        return callback.data[0:space].isdigit() and callback.data[space+1:].isdigit()


# Checking message from user for TON-wallet
class IsWallet(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        wallet = message.text
        try:
            await check_wallet(wallet)
            return True
        except InvalidAddressError:
            return False


# Checking message from user for Mnemonics of TON-wallet
class IsMnemonics(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        mnemonics = message.text.split()
        try:
            await check_mnemonics(mnemonics)
            return True
        except InvalidMnemonicsError:
            return False


# Checking callback from user for [import+space+value]
class IsImport(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        text = callback.data
        space = text.find(' ')
        return text[:space] == 'import' and text[space+1:].isdigit()


# Checking callback from user for [export+space+value]
class IsExport(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        text = callback.data
        space = text.find(' ')
        return text[:space] == 'export' and text[space+1:].isdigit()


# Checking message from user for HEX
class IsReferral(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return isHex(message.text[2:])
