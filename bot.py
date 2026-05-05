import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = os.getenv("8701793432:AAF90QvPPFF8rWhfD4X3x-kltcWD09l13Zw")
ADMIN_ID = 1881920128

bot = Bot(token=TOKEN)
dp = Dispatcher()

orders = {}
waiting_for_id = {}

# 💎 UC паки
uc_packs = {
    "60 UC": "💎 60 UC — 90₽",
    "120 UC": "💎 120 UC — 180₽",
    "325 UC": "💎 325 UC — 450₽",
    "660 UC": "💎 660 UC — 900₽",
    "1800 UC": "💎 1800 UC — 2250₽",
    "3850 UC": "💎 3850 UC — 4500₽",
    "8100 UC": "💎 8100 UC — 9000₽"
}

order_history = []

# 🚀 Старт
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Магазин", callback_data="shop")]
    ])

    await message.answer("👋 Добро пожаловать в UC магазин!", reply_markup=kb)

# 🛒 Магазин
@dp.callback_query(lambda c: c.data == "shop")
async def shop(callback: types.CallbackQuery):
    buttons = []

    for name, text in uc_packs.items():
        buttons.append([
            InlineKeyboardButton(text=text, callback_data=f"buy_{name}")
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text("💎 Выбери пакет UC:", reply_markup=kb)

# 💳 Покупка → оплата
@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    pack = callback.data.split("_")[1]

    orders[callback.from_user.id] = {"pack": pack}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]
    ])

    await callback.message.answer(
        f"🧾 Ты выбрал: 💎 {pack}\n\n"
        f"💳 Оплати по реквизитам:\n"
        f"💰 2200 7012 0371 1848\n\n"
        f"После оплаты нажми кнопку ниже 👇",
        reply_markup=kb
    )

# ✅ Нажал "Я оплатил"
@dp.callback_query(lambda c: c.data == "paid")
async def paid(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in orders:
        await callback.answer("Сначала выбери пакет ❗")
        return

    waiting_for_id[user_id] = True

    await callback.message.answer("🎮 Отправь свой PUBG ID:")

# 🎮 Получение PUBG ID
@dp.message()
async def get_pubg_id(message: types.Message):
    user_id = message.from_user.id

    if waiting_for_id.get(user_id):
        pubg_id = message.text
        pack = orders[user_id]["pack"]

        waiting_for_id[user_id] = False

        # 📜 история
        order_history.append({
            "user": message.from_user.full_name,
            "user_id": user_id,
            "pack": pack,
            "pubg_id": pubg_id,
            "status": "⏳ Ожидает"
        })

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{user_id}")
            ]
        ])

        await bot.send_message(
            ADMIN_ID,
            f"🛒 Новый заказ!\n\n"
            f"👤 {message.from_user.full_name}\n"
            f"💎 {pack}\n"
            f"🎮 PUBG ID: {pubg_id}",
            reply_markup=kb
        )

        await message.answer("⏳ Заявка отправлена! Ожидай подтверждения 😊")

# ✅ Подтверждение
@dp.callback_query(lambda c: c.data.startswith("accept_"))
async def accept(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    for order in order_history:
        if order["user_id"] == user_id and order["status"] == "⏳ Ожидает":
            order["status"] = "✅ Подтвержден"

    await bot.send_message(
        user_id,
        "✅ Платеж подтвержден!\n💎 UC скоро зачислятся 🎉"
    )

    await callback.message.edit_text("✅ Заказ подтвержден")

# ❌ Отклонение
@dp.callback_query(lambda c: c.data.startswith("decline_"))
async def decline(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    for order in order_history:
        if order["user_id"] == user_id and order["status"] == "⏳ Ожидает":
            order["status"] = "❌ Отклонен"

    await bot.send_message(
        user_id,
        "❌ Платеж отклонен 😔"
    )

    await callback.message.edit_text("❌ Заказ отклонен")

# 📜 История заказов (только админ)
@dp.message(Command("orders"))
async def show_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not order_history:
        await message.answer("📭 История заказов пуста")
        return

    text = "📜 История заказов:\n\n"

    for o in order_history:
        text += (
            f"👤 {o['user']}\n"
            f"🆔 {o['user_id']}\n"
            f"💎 {o['pack']}\n"
            f"🎮 {o['pubg_id']}\n"
            f"{o['status']}\n\n"
        )

    await message.answer(text)

# ▶️ запуск
async def main():
    print("Бот запущен ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
