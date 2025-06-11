import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Simple product catalog
PRODUCTS = {
    1: {"name": "Product A", "price": 10},
    2: {"name": "Product B", "price": 20},
    3: {"name": "Product C", "price": 30},
}

async def start_cmd(message: types.Message):
    await message.answer(
        "Welcome to the Sales Bot! Use /products to see available items."
    )

async def list_products_cmd(message: types.Message):
    text = "Available products:\n"
    for pid, data in PRODUCTS.items():
        text += f"{pid}. {data['name']} - ${data['price']}\n"
    text += "\nUse /buy <id> to purchase."
    await message.answer(text)

async def buy_cmd(message: types.Message):
    args = message.get_args()
    if not args or not args.isdigit():
        await message.answer("Usage: /buy <product_id>")
        return
    pid = int(args)
    product = PRODUCTS.get(pid)
    if not product:
        await message.answer("Unknown product ID")
        return
    await message.answer(
        f"You purchased {product['name']} for ${product['price']}. Thank you!"
    )

def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    bot = Bot(token=token)
    dp = Dispatcher(bot)

    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(list_products_cmd, commands=["products"])
    dp.register_message_handler(buy_cmd, commands=["buy"])

    executor.start_polling(dp)

if __name__ == "__main__":
    main()
