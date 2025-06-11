import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Simple product catalog
PRODUCTS = {
    1: {"name": "Product A", "price": 10},
    2: {"name": "Product B", "price": 20},
    3: {"name": "Product C", "price": 30},
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Sales Bot! Use /products to see available items."
    )

def list_products(update: Update, context: CallbackContext) -> None:
    text = "Available products:\n"
    for pid, data in PRODUCTS.items():
        text += f"{pid}. {data['name']} - ${data['price']}\n"
    text += "\nUse /buy <id> to purchase."
    update.message.reply_text(text)

def buy(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Usage: /buy <product_id>")
        return
    pid = int(context.args[0])
    product = PRODUCTS.get(pid)
    if not product:
        update.message.reply_text("Unknown product ID")
        return
    text = f"You purchased {product['name']} for ${product['price']}. Thank you!"
    update.message.reply_text(text)

def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("products", list_products))
    dp.add_handler(CommandHandler("buy", buy))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
