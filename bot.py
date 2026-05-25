import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8855692651:AAE-0VBYhUduwhv2W8xEpzHr8yhi9lyJnuQ")
GITHUB_RAW = "https://raw.githubusercontent.com/egorkalihanov2-create/kvest/main/"

# ── FSM ──────────────────────────────────────────────────────────────────────

class QuestState(StatesGroup):
    waiting_step3_button   = State()
    waiting_item_choice    = State()
    waiting_no_button      = State()
    waiting_riddle_choice  = State()
    waiting_riddle_answer  = State()
    waiting_final_answer   = State()

# ── Keyboards ────────────────────────────────────────────────────────────────

def kb_nothing() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="да мне ничего не нужно...")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def kb_items() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="газета",  callback_data="item_newspaper"),
            InlineKeyboardButton(text="журнал",  callback_data="item_magazine"),
            InlineKeyboardButton(text="игрушка", callback_data="item_toy"),
        ]
    ])

def kb_no_need() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="нет, все-таки ничего не надо...")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def kb_riddles(pressed: set) -> InlineKeyboardMarkup:
    labels = {
        "riddle_lane":   "Защитник Лэйн",
        "riddle_1s1s":   "1 с 1 с - спасаться",
        "riddle_please": "Пожалуйста, загадку",
        "riddle_mischief":"Толкает на пакость",
    }
    rows = []
    for cb, label in labels.items():
        check = " ✅" if cb in pressed else ""
        rows.append([InlineKeyboardButton(text=label + check, callback_data=cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Helpers ──────────────────────────────────────────────────────────────────

def github_url(filename: str) -> str:
    return GITHUB_RAW + filename

def get_keys_grid(mid_text=""):
    """
    Генерирует сетку кастомных эмодзи в формате HTML.
    Используются ваши custom_emoji_id.
    """
    e1 = '<tg-emoji emoji-id="5233552606638413980">🗝</tg-emoji>'
    e2 = '<tg-emoji emoji-id="5235974190804278599">🗝</tg-emoji>'
    e3 = '<tg-emoji emoji-id="5235523090389182893">🗝</tg-emoji>'
    
    e4 = '<tg-emoji emoji-id="5233267614083488173">🗝</tg-emoji>'
    e5 = '<tg-emoji emoji-id="5233679372598155360">🗝</tg-emoji>'
    e6 = '<tg-emoji emoji-id="5235548198767992433">🗝</tg-emoji>'
    
    e7 = '<tg-emoji emoji-id="5233639502416745558">🗝</tg-emoji>'
    e8 = '<tg-emoji emoji-id="5233372183652243957">🗝</tg-emoji>'
    e9 = '<tg-emoji emoji-id="5235492243934057368">🗝</tg-emoji>'

    row1 = f"{e1}{e2}{e3}"
    row2 = f"{e4}{e5}{e6}" + (f"  {mid_text}" if mid_text else "")
    row3 = f"{e7}{e8}{e9}"
    
    return f"{row1}\n{row2}\n{row3}"

async def send_photo_from_github(bot: Bot, chat_id: int, filename: str,
                                  caption: str, caption_entities=None,
                                  reply_markup=None, parse_mode=None):
    url = github_url(filename)
    await bot.send_photo(
        chat_id=chat_id,
        photo=url,
        caption=caption,
        caption_entities=caption_entities,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )

# ── Handlers ─────────────────────────────────────────────────────────────────

async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    chat_id = message.chat.id

    await message.bot.send_message(
        chat_id,
        "Здраавствуйте, девушка",
        entities=[
            {"offset": 0, "length": 22, "type": "blockquote"},
            {"offset": 0, "length": 22, "type": "italic"},
        ],
    )

    await asyncio.sleep(5)

    await message.bot.send_message(
        chat_id,
        "Де-евушка!",
        entities=[
            {"offset": 0, "length": 10, "type": "blockquote"},
            {"offset": 0, "length": 10, "type": "italic"},
        ],
    )

    await asyncio.sleep(5)

    caption3 = (
        f"{get_keys_grid('Не слышите что-ли!')}\n\n"
        f"газеты, журналы, игрушки… ло-те-ре-йки) вам чего?"
    )
    await send_photo_from_github(
        message.bot, chat_id,
        "first.png",
        caption=caption3,
        parse_mode="HTML",
        reply_markup=kb_nothing(),
    )
    await state.set_state(QuestState.waiting_step3_button)


async def on_nothing_button(message: Message, state: FSMContext):
    chat_id = message.chat.id

    caption4 = get_keys_grid('А вы посмотрите...')
    
    await send_photo_from_github(
        message.bot, chat_id,
        "second.png",
        caption=caption4,
        parse_mode="HTML",
        reply_markup=kb_items(),
    )
    await state.set_state(QuestState.waiting_item_choice)


async def on_item_callback(callback: CallbackQuery, state: FSMContext):
    texts = {
        "item_newspaper": (
            'Перед вами газета "САРАТОВСКИЙ СПЛЕТНИК".\n\n'
            'На второй странице: "ВОПРОС НА МИЛЛИОН: как простая девушка из саратова '
            'МЕСЯЦАМИ обманывала крупнейшую франшизу…", на 3 странице: "СЕКСА НЕТ — '
            'НЕ ДАМ ВАМ ЖИЗНИ: девушки города сходят с ума в тоске по х**м!", на 4 '
            'странице: "ОН ВОНЯЕТ, КАК СВИНЬЯ, НО Я НЕ МОГУ ЕГО БРОСИТЬ: квиз про ******"'
        ),
        "item_magazine": (
            'Продавщица достает (почти) новую книжонку, покрытую глянцем. на обложке '
            'красуется название «ЭСКВАЙР 64». Аккурат под ним — красивая девушка с '
            'неприятным взглядом и лаконичной подписью: «блоггер, маркетолог, UGC '
            'креатор, владелица своего креативного агентства, та, благодаря которой '
            'весь саратов знает о магазине спутник, лекторша, пиарщица, молодец, красавица»'
        ),
        "item_toy": (
            'На прилавке, кажется, есть всё. глазами, вы находите засохший слайм, '
            'когда-то растекшийся на выпуск «Комсомольской Правды», спиннеры, поросшие '
            'многолетней патиной, и, конечно, конструкторы майнкрафт (старая цена '
            'перечеркнута маркером, новая надпись: 57 рублей. ценообразованием здесь '
            'заведует продавщица'
        ),
    }

    alert_text = texts[callback.data]
    
    # Лимит Telegram для show_alert = 200 символов. 
    # Обрезаем текст, чтобы бот не выдавал ошибку Bad Request.
    if len(alert_text) > 200:
        alert_text = alert_text[:197] + "..."

    await callback.answer(text=alert_text, show_alert=True)

    await callback.message.answer(
        ".",
        reply_markup=kb_no_need(),
    )
    await state.set_state(QuestState.waiting_no_button)


async def on_no_need_button(message: Message, state: FSMContext):
    chat_id = message.chat.id

    caption5 = (
        f"{get_keys_grid('Ну ничем не угодишь!')}\n\n"
        f"хотя знаешь, кое-что у меня наверное есть..."
    )
    await send_photo_from_github(
        message.bot, chat_id,
        "third.png",
        caption=caption5,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    await asyncio.sleep(5)

    await state.update_data(pressed=[], current_riddle=None)
    await message.bot.send_message(
        chat_id,
        "Ну что, с какого начнешь?",
        reply_markup=kb_riddles(set()),
    )
    await state.set_state(QuestState.waiting_riddle_choice)


# ── Загадки ──────────────────────────────────────────────────────────────────

RIDDLE_PROMPTS = {
    "riddle_lane":    "Защитник Лэйн, 4 буквы, идеи?",
    "riddle_1s1s":    "Поняла, о чем речь?",
    "riddle_please":  "Идеи?",
    "riddle_mischief":"Чо думаешь?",
}

RIDDLE_ANSWERS = {
    "riddle_lane":    (["каин", "каен", "каэн"], "Молодец! Откройте букву А"),
    "riddle_1s1s":    (["отродье"],               "Молодец! Откройте букву Е"),
    "riddle_please":  (["квизплиз", "квиз плиз"], "Молодец! Откройте букву Л"),
    "riddle_mischief":(["обида"],                 "Молодец! Откройте букву И"),
}


async def on_riddle_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    pressed: list = data.get("pressed", [])

    riddle_key = callback.data
    await callback.message.answer(RIDDLE_PROMPTS[riddle_key])
    await state.update_data(current_riddle=riddle_key, pressed=pressed)
    await state.set_state(QuestState.waiting_riddle_answer)


async def on_riddle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current_riddle = data.get("current_riddle")
    pressed: list  = data.get("pressed", [])

    if not current_riddle:
        return

    correct_answers, success_text = RIDDLE_ANSWERS[current_riddle]
    user_text = message.text.strip().lower()

    if user_text in correct_answers:
        await message.answer(success_text)

        if current_riddle not in pressed:
            pressed.append(current_riddle)
        await state.update_data(pressed=pressed, current_riddle=None)

        if len(pressed) == 4:
            await message.answer(
                "Получается А  ЕЛИ... Что же пропущено?",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(QuestState.waiting_final_answer)
        else:
            await message.answer(
                "Ну что, с какого начнешь?",
                reply_markup=kb_riddles(set(pressed)),
            )
            await state.set_state(QuestState.waiting_riddle_choice)
    else:
        pass


async def on_final_answer(message: Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "амели":
        await message.answer("Да! Приходи на кухню!")
        await state.clear()


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN env variable is not set!")

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.message.register(cmd_start, CommandStart())

    dp.message.register(
        on_nothing_button,
        QuestState.waiting_step3_button,
        F.text == "да мне ничего не нужно...",
    )

    dp.callback_query.register(
        on_item_callback,
        QuestState.waiting_item_choice,
        F.data.in_({"item_newspaper", "item_magazine", "item_toy"}),
    )

    dp.message.register(
        on_no_need_button,
        QuestState.waiting_no_button,
        F.text == "нет, все-таки ничего не надо...",
    )

    dp.callback_query.register(
        on_riddle_choice,
        QuestState.waiting_riddle_choice,
        F.data.in_({"riddle_lane", "riddle_1s1s", "riddle_please", "riddle_mischief"}),
    )

    dp.message.register(on_riddle_answer, QuestState.waiting_riddle_answer)
    dp.message.register(on_final_answer, QuestState.waiting_final_answer)

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
