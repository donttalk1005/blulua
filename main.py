from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup

# Replace this with your actual bot token
token = "7719735480:AAF0NoGSWBjQJiY0y-OBi6FhEWAUd9VkmRo"
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Define your custom keyboard
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton("🖼Yangi post"))
keyboard.add(types.KeyboardButton("✅Tugatdim"))

# Replace this with your actual group chat ID or username
#group_chat_id = -1002225113103
group_chat_id = -1002259552495
# Specified user IDs
allowed_user_ids = [625695297]


class PostState(StatesGroup):
    waiting_for_media = State()
    waiting_for_caption = State()
    waiting_for_price = State()


async def start_command(message: types.Message):
    
    if message.from_user.id in allowed_user_ids:
        await message.reply("😊Salom! Post joylash knopkasini bosing.")
    else:
        await message.reply('Assalomu alaykum!', reply=False)
        await message.reply(text="Admin: @iamnot_dtlk\n Kanal: @kompyuter_savodxonligi_uz")


dp.register_message_handler(start_command, commands=["start"])


async def button_press_handler(msg: types.Message):
    if msg.text == "🖼Yangi post" and msg.from_user.id in allowed_user_ids:
        await post_new_message(msg)


dp.register_message_handler(button_press_handler, lambda msg: msg.text == "🖼Yangi post")


async def post_new_message(msg: types.Message):
    async with dp.current_state(user=msg.from_user.id).proxy() as data:
        data['media'] = []  # Clear the media list
    await msg.answer("Rasm yoki videolarni yuboring, iltimos. Tugatgandan so'ng '✅Tugatdim' knopkasini bosing.")
    await PostState.waiting_for_media.set()


dp.register_message_handler(post_new_message, commands=["post"])


async def receive_media(msg: types.Message, state: FSMContext):
    if msg.from_user.id in allowed_user_ids:
        if msg.content_type in [types.ContentType.PHOTO, types.ContentType.VIDEO]:
            async with state.proxy() as data:
                if msg.content_type == types.ContentType.PHOTO:
                    data['media'].append(types.InputMediaPhoto(msg.photo[-1].file_id))
                elif msg.content_type == types.ContentType.VIDEO:
                    data['media'].append(types.InputMediaVideo(msg.video.file_id))
            await msg.answer("Media qabul qilindi, boshqa media yuboring yoki '✅Tugatdim' knopkasini bosing.")
        elif msg.text.lower() == '✅tugatdim':
            async with state.proxy() as data:
                if 'media' in data and data['media']:
                    await PostState.waiting_for_caption.set()
                    await msg.answer(
                        "Endi media uchun mavzu: .")
                else:
                    await msg.answer(
                        "Hech qanday media topilmadi. Iltimos, media fayl yuboring yoki jarayonni tugating.")


dp.register_message_handler(receive_media, state=PostState.waiting_for_media, content_types=types.ContentType.ANY)


async def receive_caption(msg: types.Message, state: FSMContext):
    if msg.from_user.id in allowed_user_ids:
        async with state.proxy() as data:
            data['caption'] = msg.text
        await PostState.waiting_for_price.set()
        await msg.answer("Endi post matni:")


dp.register_message_handler(receive_caption, state=PostState.waiting_for_caption, content_types=types.ContentType.TEXT)


async def receive_price(msg: types.Message, state: FSMContext):
    if msg.from_user.id in allowed_user_ids:
        async with state.proxy() as data:
            caption_with_price = data['caption'] + f"\n{msg.text}\n\n📢@kompyuter_savodxonligi_uz"
            await msg.answer(
                "😊Barcha media va izoh guruhga muvaffaqqiyatli jo'natildi. Rahmat!\nYana narsa tashlamoqchi bo'lsangiz 🖼Yangi post knopkasini bosing")

            media = data['media']
            media[0].caption = caption_with_price  # Qo'shimcha faqat birinchi media elementiga qo'shiladi
            
            await bot.send_media_group(chat_id=group_chat_id, media=media)
            
            await state.finish()


dp.register_message_handler(receive_price, state=PostState.waiting_for_price, content_types=types.ContentType.TEXT)


async def handle_group_members_join_leave_messages(message: types.Message):
    if message.chat.id == group_chat_id:
        await message.delete()


dp.register_message_handler(handle_group_members_join_leave_messages,
                            content_types=[types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER])

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
