import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Стан гри "Вгадай число"
user_games = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " **Ласкаво просимо до GameBot!**\nОберіть гру з меню нижче:"
    keyboard = [
        [InlineKeyboardButton("🪨✂️📄 Цу-е-фа", callback_data="game_rps")],
        [InlineKeyboardButton("🎲 Кинути кості", callback_data="game_dice")],
        [InlineKeyboardButton("🔢 Вгадай число", callback_data="game_guess")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "game_dice":
        await query.message.reply_dice(emoji="🎲")

    elif query.data == "game_rps":
        keyboard = [
            [
                InlineKeyboardButton("🪨 Камінь", callback_data="rps_rock"),
                InlineKeyboardButton("✂️ Ножиці", callback_data="rps_scissors"),
                InlineKeyboardButton("📄 Папір", callback_data="rps_paper")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Обери свій хід:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("rps_"):
        user_choice = query.data.split("_")[1]
        choices = ["rock", "scissors", "paper"]
        bot_choice = random.choice(choices)

        names = {"rock": "Камінь 🪨", "scissors": "Ножиці ✂️", "paper": "Папір 📄"}

        if user_choice == bot_choice:
            res = "Нічия! 🤝"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
                (user_choice == "scissors" and bot_choice == "paper") or \
                (user_choice == "paper" and bot_choice == "rock"):
            res = "Ти переміг! 🎉"
        else:
            res = "Бот переміг! 🤖"

        await query.edit_message_text(
            f"Твій вибір: {names[user_choice]}\nВибір бота: {names[bot_choice]}\n\n**{res}**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Грати знову", callback_data="game_rps")]])
        )

    elif query.data == "game_guess":
        user_id = query.from_user.id
        user_games[user_id] = random.randint(1, 100)
        await query.edit_message_text("Я загадав число від 1 до 100. Напиши свій варіант у чат!")

    elif query.data == "main_menu":
        await start(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_games:
        try:
            guess = int(update.message.text)
            target = user_games[user_id]
            if guess < target:
                await update.message.reply_text("Більше! ⬆️")
            elif guess > target:
                await update.message.reply_text("Менше! ⬇️")
            else:
                await update.message.reply_text("🎉 Вітаю! Ти вгадав число!")
                del user_games[user_id]
        except ValueError:
            await update.message.reply_text("Будь ласка, введи ціле число.")


import asyncio  # Переконайтеся, що asyncio імпортовано на початку файлу


async def main_async():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Використовуємо ініціалізацію та запуск через асинхронний контекстний менеджер
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # Чекаємо на зупинку (Ctrl+C)
        stop_signal = asyncio.Event()
        try:
            await stop_signal.wait()
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()