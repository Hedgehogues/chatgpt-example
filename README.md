# Sales Telegram Bot

This repository contains a simple Telegram bot written in Python using
[`aiogram`](https://docs.aiogram.dev/) for showcasing products and taking orders.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `TELEGRAM_TOKEN` environment variable with your bot token.
3. Run the bot:
   ```bash
   python sales_bot.py
   ```

## Usage
- `/start` – greeting message.
- `/products` – list available products.
- `/buy <id>` – purchase a product by ID.
