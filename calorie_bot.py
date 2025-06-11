import os
import datetime
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# In-memory storage for user data
# {user_id: {'limit': int, 'entries': [(date, calories)]}}
USER_DATA = {}

# Dummy ML calorie estimator. In production, integrate actual API call.
def estimate_calories_from_photo(photo_bytes: bytes) -> int:
    """Return estimated calories from image bytes."""
    # TODO: integrate real ML model/API
    return 100


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Привет! Отправь фото еды, чтобы я оценил калорийность. "
        "Используй /limit <калории> чтобы установить дневной лимит." 
    )


def set_limit(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Использование: /limit <калории в день>")
        return
    limit = int(context.args[0])
    data = USER_DATA.setdefault(update.effective_user.id, {'limit': limit, 'entries': []})
    data['limit'] = limit
    update.message.reply_text(f"Лимит установлен: {limit} калорий в день")


def remaining(update: Update, context: CallbackContext) -> None:
    data = USER_DATA.get(update.effective_user.id)
    if not data or 'limit' not in data:
        update.message.reply_text("Сначала установите лимит через /limit")
        return
    today = datetime.date.today()
    consumed = sum(c for d, c in data['entries'] if d == today)
    remaining = data['limit'] - consumed
    update.message.reply_text(f"Остаток калорий на сегодня: {remaining}")


def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = update.message.photo[-1].get_file()
    photo_bytes = photo_file.download_as_bytearray()
    calories = estimate_calories_from_photo(photo_bytes)

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=f"confirm:{calories}"),
         InlineKeyboardButton("Ввести вручную", callback_data="manual")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"На фото примерно {calories} калорий. Подтвердить?",
        reply_markup=reply_markup
    )


def add_entry(user_id: int, calories: int) -> None:
    data = USER_DATA.setdefault(user_id, {'limit': None, 'entries': []})
    data['entries'].append((datetime.date.today(), calories))


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if query.data.startswith("confirm:"):
        calories = int(query.data.split(":", 1)[1])
        add_entry(user_id, calories)
        query.edit_message_text(f"Добавлено {calories} калорий")
    elif query.data == "manual":
        context.user_data['awaiting_manual'] = True
        query.edit_message_text("Введите калории числом:")


def handle_text(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_manual'):
        if not update.message.text.isdigit():
            update.message.reply_text("Пожалуйста, введите число")
            return
        calories = int(update.message.text)
        add_entry(update.effective_user.id, calories)
        context.user_data['awaiting_manual'] = False
        update.message.reply_text(f"Добавлено {calories} калорий")


def summary(update: Update, context: CallbackContext) -> None:
    data = USER_DATA.get(update.effective_user.id)
    if not data:
        update.message.reply_text("Данные отсутствуют")
        return
    today = datetime.date.today()
    entries = [c for d, c in data['entries'] if d == today]
    text = "Сегодня:\n" + "\n".join(f"{idx+1}. {c} ккал" for idx, c in enumerate(entries))
    consumed = sum(entries)
    limit = data.get('limit')
    if limit:
        text += f"\nВсего {consumed} из {limit} ккал"
    else:
        text += f"\nВсего {consumed} ккал (лимит не установлен)"
    update.message.reply_text(text)


def delete_entry(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Использование: /delete <номер>")
        return
    idx = int(context.args[0]) - 1
    data = USER_DATA.get(update.effective_user.id)
    if not data:
        update.message.reply_text("Данные отсутствуют")
        return
    today = datetime.date.today()
    todays_entries = [i for i, (d, _) in enumerate(data['entries']) if d == today]
    if idx < 0 or idx >= len(todays_entries):
        update.message.reply_text("Неверный номер")
        return
    real_idx = todays_entries[idx]
    removed = data['entries'].pop(real_idx)[1]
    update.message.reply_text(f"Удалено {removed} ккал")


def update_entry(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2 or not context.args[0].isdigit() or not context.args[1].isdigit():
        update.message.reply_text("Использование: /update <номер> <калории>")
        return
    idx = int(context.args[0]) - 1
    new_cal = int(context.args[1])
    data = USER_DATA.get(update.effective_user.id)
    if not data:
        update.message.reply_text("Данные отсутствуют")
        return
    today = datetime.date.today()
    todays_entries = [i for i, (d, _) in enumerate(data['entries']) if d == today]
    if idx < 0 or idx >= len(todays_entries):
        update.message.reply_text("Неверный номер")
        return
    real_idx = todays_entries[idx]
    data['entries'][real_idx] = (today, new_cal)
    update.message.reply_text(f"Запись {idx+1} обновлена: {new_cal} ккал")


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("limit", set_limit))
    dp.add_handler(CommandHandler("remaining", remaining))
    dp.add_handler(CommandHandler("summary", summary))
    dp.add_handler(CommandHandler("delete", delete_entry))
    dp.add_handler(CommandHandler("update", update_entry))

    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
