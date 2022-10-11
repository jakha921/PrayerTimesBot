import asyncio
import logging
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.handler import ctx_data
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)

from loguru import logger
from telegram_bot_pagination import InlineKeyboardPaginator

from tgbot.keyboards.inline import choose_language, cd_choose_lang, location, surah, location_callback, surah_callback, \
    pagination, page_callback
from tgbot.keyboards import reply
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.models.models import TGUser
from tgbot.misc.utils import Map, find_button_text
from tgbot.misc.scraping import today_times, tomorrow_times, take_ablution, prayer_order, surah_section
from tgbot.services.database import AsyncSession


async def delete_message(message: Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


async def user_start(m: Message, texts: Map):
    """User start command handler"""
    msg = f"Салом, {m.from_user.full_name}!\nМен Намоз ва Руза вактиларини айтувчи бот ман\n\n"
    msg += "Суралар, Намоз укиш ва Таҳорат "
    await m.reply(msg, reply_markup=await reply.main_menu())


async def user_close_reply_keyboard(m: Message, texts: Map):
    """User close reply keyboard button handler"""
    await m.reply(texts.user.close_reply_keyboard, reply_markup=ReplyKeyboardRemove())


async def user_lang(m: Message, texts: Map):
    """User lang command handler"""
    await m.reply(texts.user.lang, reply_markup=await choose_language(texts))


async def user_today(m: Message, texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User button today handler"""
    msg = await m.answer(f'Жунатилмокда ...')
    user = await TGUser.get_user(db_session, telegram_id=db_user.telegram_id)
    times = await m.answer(f'Бугун :\n{today_times(user.city)}')
    asyncio.create_task(delete_message(msg, (times.message_id - times.message_id)))


async def user_tomorrow(m: Message, texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User button tomorrow handler"""
    user = await TGUser.get_user(db_session, telegram_id=db_user.telegram_id)
    msg = await m.answer(f'Жунатилмокда ...')
    times = await m.answer(f'Ертага :\n{tomorrow_times(user.city)}')
    asyncio.create_task(delete_message(msg, (times.message_id - times.message_id)))


async def get_location_inline_kd(m: Message):
    await m.answer("Mинтақангизни танланг:", reply_markup=await location())
    await m.delete()


# Sub menu
async def get_sub_menu(m: Message):
    await m.answer('Тангланг', reply_markup=await reply.additional_menu())


async def get_ablution(message: Message, page=1):
    """таҳорат олиш"""
    prayer = take_ablution()
    value = prayer.get(page)
    await message.answer_animation(value["img"], caption=f'<b>{value["title"]}</b>\n\n{value["text"]}', \
                                       reply_markup=await pagination(len(prayer), page=page, per_page=1, function_name='get_ablution'))


async def get_prayer_order(message: Message, page=1):
    # logging.info(message)
    prayer = prayer_order()
    value = prayer.get(page)
    animation = f'<b>{value["title"]}</b>\n\n{value["text"]}'
    audio_arabic = f"{value['arabic_text']}"
    audio_text = f"{value['audio_text']}"

    if value['img'] is not None:
        try:
            await message.answer_animation(value["img"], caption=animation, reply_markup=await pagination(len(prayer), page=page, per_page=1, function_name='get_prayer_order'))
        except:
            await message.answer_animation(value["img"])
            await message.answer(animation.strip())

    if value['mp3'] is not None:
        for audio in value['mp3']:
            try:
                await message.answer_voice(audio, caption=f'{audio_arabic}\n {audio_text}')
            except:
                await message.answer_voice(audio, caption=audio_arabic)
                # await message.answer(audio_text)

        # await asyncio.sleep(4)


async def get_surah_inline_kd(m: Message):
    """сурслар кнопкаси"""
    await m.answer("Сура ва дуолар:", reply_markup=await surah())
    await m.delete()


async def get_menu(m: Message):
    await m.answer('Бош менюга', reply_markup=await reply.main_menu())


# Inline kbs
async def user_lang_choosen(cb: CallbackQuery, callback_data: dict,
                            texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User lang choosen handler"""
    code = callback_data.get('lang_code')
    await TGUser.update_user(db_session,
                             telegram_id=db_user.telegram_id,
                             updated_fields={'lang_code': code})

    # manually load translation for user with new lang_code
    texts = await TranslationMiddleware().reload_translations(cb, ctx_data.get(), code)
    btn_text = await find_button_text(cb.message.reply_markup.inline_keyboard, cb.data)
    await cb.message.edit_text(texts.user.lang_choosen.format(lang=btn_text), reply_markup='')


async def get_location_id(cb: CallbackQuery, db_user: TGUser, db_session: AsyncSession):
    data = cb.data.split(':')
    await cb.answer(f'Сизни миткангиз {data[1]} деб танланди!', show_alert=True, cache_time=60)
    await cb.message.delete()

    # save city id on db
    await TGUser.update_user(db_session,
                             telegram_id=db_user.telegram_id,
                             updated_fields={'city': int(data[2])})


async def get_surah_id(cb: CallbackQuery):
    msg_arabic = ''
    msg_text = ''
    data = cb.data.split(':')
    surah = surah_section(int(data[2]))
    await cb.message.delete()
    await cb.message.answer(surah.get('title'))
    await cb.message.answer_audio(surah.get('audio'), surah.get('title'))
    for tx in surah.get('arabic'): msg_arabic += f'{tx}  '
    for tx in surah.get('text'): msg_text += f'{tx}\n'
    await cb.message.answer(msg_arabic)
    await cb.message.answer(msg_text)


async def get_pages(cb: CallbackQuery):
    page, function = int(cb.data.split(':')[1]), cb.data.split(':')[2]
    await cb.message.delete()
    if function == 'get_ablution':
        await get_ablution(cb.message, page=page)
    elif function == 'get_prayer_order':
        await get_prayer_order(cb.message, page=page)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_lang, commands=["lang"], state="*")
    dp.register_message_handler(user_today, text="⏳📅Бугун", state="*")
    dp.register_message_handler(user_tomorrow, text='📆Eрта', state="*")
    dp.register_message_handler(get_location_inline_kd, text='🌏Минтақа', state="*")
    dp.register_message_handler(get_sub_menu, text='🙏Намоз хакида кушимча малумотлар', state="*")
    dp.register_message_handler(get_ablution, text='🛁Таҳорат қилиш тартиби', state="*")
    dp.register_message_handler(get_prayer_order, text='🧎Намоз ўқиш тартиби', state="*")
    dp.register_message_handler(get_surah_inline_kd, text='📖 Суралар', state="*")
    dp.register_message_handler(get_menu, text='🔙Оркага', state="*")
    dp.register_message_handler(user_close_reply_keyboard, is_close_btn=True, state="*")
    # dp.register_message_handler(user_phone_sent, content_types=["contact"], state="*")
    dp.register_callback_query_handler(user_lang_choosen, cd_choose_lang.filter(), state="*")
    dp.register_callback_query_handler(get_location_id, location_callback.filter(), state="*")
    dp.register_callback_query_handler(get_surah_id, surah_callback.filter(), state="*")
    dp.register_callback_query_handler(get_pages, page_callback.filter(), state="*")
