from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.misc.utils import Map


async def phone_number(texts: Map):
    """Phone number inline keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.user.kb.reply.phone,
                            request_contact=True)],
            [KeyboardButton(text=texts.user.kb.reply.close)],
        ],
        resize_keyboard=True,
    )
    return keyboard


async def main_menu():
    """Menu reply keyboard"""
    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='⏳📅Бугун'),
                KeyboardButton(text='📆Eрта'),
            ],
            [
                # KeyboardButton(text='🤲 Саҳарлик & Ифторлик'),
                KeyboardButton(text='🌏Минтақа'),
            ],
            [
                KeyboardButton(text='🙏Намоз хакида кушимча малумотлар'),
            ],
        ],
        resize_keyboard=True,
    )
    return main_menu


async def additional_menu():
    sub_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    sub_menu.add(KeyboardButton(text='🛁Таҳорат қилиш тартиби'))
    sub_menu.add(KeyboardButton(text='🧎Намоз ўқиш тартиби'))
    sub_menu.add(KeyboardButton(text='📖 Суралар'))
    sub_menu.add(KeyboardButton(text='🔙Оркага'))
    return sub_menu
