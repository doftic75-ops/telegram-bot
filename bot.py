from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

import os
TOKEN = os.getenv("TOKEN")

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи свой PUBG ID:")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    pubg_id = update.message.text

    user_data[user_id] = {"pubg_id": pubg_id}

    keyboard = [
        [InlineKeyboardButton("60 UC", callback_data="60")],
        [InlineKeyboardButton("325 UC", callback_data="325")],
        [InlineKeyboardButton("660 UC", callback_data="660")],
        [InlineKeyboardButton("1800 UC", callback_data="1800")],
        [InlineKeyboardButton("3850 UC", callback_data="3850")],
        [InlineKeyboardButton("8100 UC", callback_data="8100")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери количество UC:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    uc = query.data
    pubg_id = user_data[user_id]["pubg_id"]

    await query.edit_message_text(
        f"✅ Заявка принята!\n\nPUBG ID: {pubg_id}\nUC: {uc}"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_id))
app.add_handler(CallbackQueryHandler(button))

print("Бот запущен...")
app.run_polling()
