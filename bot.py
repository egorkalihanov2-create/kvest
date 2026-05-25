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
    waiting_step3_button   = State()   # ждём кнопку "да мне ничего не нужно..."
    waiting_item_choice    = State()   # ждём нажатие на газету/журнал/игрушку
    waiting_no_button      = State()   # ждём кнопку "нет, все-таки ничего не надо..."
    waiting_riddle_choice  = State()   # ждём выбор загадки (шаг 6)
    waiting_riddle_answer  = State()   # ждём ответ на загадку
    waiting_final_answer   = State()   # ждём "Амели"

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

async def send_photo_from_github(bot: Bot, chat_id: int, filename: str,
                                  caption: str, caption_entities=None,
                                  reply_markup=None):
    """Отправляет фото, скачивая его с GitHub по URL."""
    url = github_url(filename)
    await bot.send_photo(
        chat_id=chat_id,
        photo=url,
        caption=caption,
        caption_entities=caption_entities,
        reply_markup=reply_markup,
    )

# ── Handlers ─────────────────────────────────────────────────────────────────

async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    chat_id = message.chat.id

    # Сообщение 1 — blockquote + italic
    await message.bot.send_message(
        chat_id,
        "Здраавствуйте, девушка",
        entities=[
            {"offset": 0, "length": 22, "type": "blockquote"},
            {"offset": 0, "length": 22, "type": "italic"},
        ],
    )

    await asyncio.sleep(5)

    # Сообщение 2
    await message.bot.send_message(
        chat_id,
        "Де-евушка!",
        entities=[
            {"offset": 0, "length": 10, "type": "blockquote"},
            {"offset": 0, "length": 10, "type": "italic"},
        ],
    )

    await asyncio.sleep(5)

    # Сообщение 3 — first.png + caption + кнопка reply
    caption3 = (
        "🗝🗝🗝\n"
        "🗝🗝🗝  Не слышите что-ли!\n"
        "🗝🗝🗝\n"
        "газеты, журналы, игрушки… ло-те-ре-йки) вам чего?"
    )
    await send_photo_from_github(
        message.bot, chat_id,
        "first.png",
        caption=caption3,
        reply_markup=kb_nothing(),
    )
    await state.set_state(QuestState.waiting_step3_button)


async def on_nothing_button(message: Message, state: FSMContext):
    """Шаг 4: пользователь нажал 'да мне ничего не нужно...'"""
    chat_id = message.chat.id

    caption4 = (
        "🗝🗝🗝\n"
        "🗝🗝🗝  А вы посмотрите...\n"
        "🗝🗝🗝"
    )
    await send_photo_from_github(
        message.bot, chat_id,
        "second.png",
        caption=caption4,
        reply_markup=kb_items(),
    )
    await state.set_state(QuestState.waiting_item_choice)


async def on_item_callback(callback: CallbackQuery, state: FSMContext):
    """Реакция на нажатие газета/журнал/игрушка."""
    await callback.answer()

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

    await callback.message.answer(texts[callback.data])

    # Показываем кнопку "нет, все-таки ничего не надо..."
    await callback.message.answer(
        ".",
        reply_markup=kb_no_need(),
    )
    await state.set_state(QuestState.waiting_no_button)


async def on_no_need_button(message: Message, state: FSMContext):
    """Шаг 5: пользователь нажал 'нет, все-таки ничего не надо...'"""
    chat_id = message.chat.id

    caption5 = (
        "🗝🗝🗝\n"
        "🗝🗝🗝  Ну ничем не угодишь!\n"
        "🗝🗝🗝\n"
        "хотя знаешь, кое-что у меня наверное есть..."
    )
    await send_photo_from_github(
        message.bot, chat_id,
        "third.png",
        caption=caption5,
        reply_markup=ReplyKeyboardRemove(),
    )

    await asyncio.sleep(5)

    # Шаг 6 — «Ну что, с какого начнешь?»
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
            # Все 4 загадки решены
            await message.answer(
                "Получается А  ЕЛИ... Что же пропущено?",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(QuestState.waiting_final_answer)
        else:
            # Обновляем клавиатуру с галочками и возвращаемся к выбору
            await message.answer(
                "Ну что, с какого начнешь?",
                reply_markup=kb_riddles(set(pressed)),
            )
            await state.set_state(QuestState.waiting_riddle_choice)
    else:
        # Неверный ответ — остаёмся в состоянии ожидания ответа
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

    # Start
    dp.message.register(cmd_start, CommandStart())

    # Шаг 3 → 4: кнопка reply
    dp.message.register(
        on_nothing_button,
        QuestState.waiting_step3_button,
        F.text == "да мне ничего не нужно...",
    )

    # Шаг 4: inline-кнопки товаров
    dp.callback_query.register(
        on_item_callback,
        QuestState.waiting_item_choice,
        F.data.in_({"item_newspaper", "item_magazine", "item_toy"}),
    )

    # Шаг 4 → 5: кнопка reply
    dp.message.register(
        on_no_need_button,
        QuestState.waiting_no_button,
        F.text == "нет, все-таки ничего не надо...",
    )

    # Шаг 6: выбор загадки
    dp.callback_query.register(
        on_riddle_choice,
        QuestState.waiting_riddle_choice,
        F.data.in_({"riddle_lane", "riddle_1s1s", "riddle_please", "riddle_mischief"}),
    )

    # Шаг 6: ответ на загадку
    dp.message.register(on_riddle_answer, QuestState.waiting_riddle_answer)

    # Финальный ответ
    dp.message.register(on_final_answer, QuestState.waiting_final_answer)

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
