from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, reply_keyboard
from aiogram.utils.callback_data import CallbackData

from telegram_bot_pagination import InlineKeyboardPaginator

from tgbot.misc.utils import Map
from tgbot.misc.scraping import get_location_id, surah

cd_choose_lang = CallbackData("choosen_language", "lang_code")


async def choose_language(texts: Map):
    """Choose language inline keyboard"""
    # get languages from translation texts
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(InlineKeyboardButton(
            v.text, callback_data=cd_choose_lang.new(lang_code=k)))
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )


# callback_data for location
location_callback = CallbackData('location', 'city_name', 'city_id')

locations = get_location_id()


async def location():
    location_menu = InlineKeyboardMarkup(row_width=3)
    for key, value in locations.items():
        location_menu.insert(InlineKeyboardButton(
            text=key, callback_data=location_callback.new(city_name=key, city_id=value)))
    return location_menu


# callback_data for location end


# callback_data for surah
surah_callback = CallbackData('surah', 'surah_name', 'surah_id')

surahs = surah()


async def surah():
    surah_menu = InlineKeyboardMarkup(row_width=2)
    for key, value in surahs.items():
        surah_menu.insert(InlineKeyboardButton(
            text=key, callback_data=surah_callback.new(surah_name=key, surah_id=value)))
    return surah_menu


# callback_data for surah end

# Nodir`s pagination
page_callback = CallbackData('pagination', 'page', 'buttons_for_name')


async def pagination(
        count: int,
        page: int,
        per_page: int,
        function_name: str) -> InlineKeyboardMarkup:
    """
   Generate pagination buttons
   """
    keyboard = []
    btns = []
    if page > 1:
        btns.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=page_callback.new(
                    page=page - 1,
                    buttons_for_name=function_name
                )
            )
        )
    stats = f" {page * per_page} / {count} " if (
                                                        page * per_page) < count else f" {count} / {count} "
    btns.append(
        InlineKeyboardButton(
            text=stats if count > 0 else "Hozircha to'lovlar yo'q 🤷‍♂️",
            callback_data='none'
        )
    )
    if count > (page * per_page):
        btns.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=page_callback.new(
                    page=page + 1,
                    buttons_for_name=function_name
                )
            )
        )
    keyboard.append(btns)
    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
        row_width=len(btns)
    )
