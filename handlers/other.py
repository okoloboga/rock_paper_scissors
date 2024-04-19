from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner

from keyboards.keyboards import play_account_kb

router = Router()


# Unknown messages
@router.message()
async def send_answer(message: Message, state: FSMContext, i18n: TranslatorRunner):
    await message.answer(text=i18n.other.answers(),
                         reply_markup=play_account_kb(i18n))
    await state.clear()

