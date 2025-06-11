# Sales Telegram Bot

This repository contains a simple Telegram bot written in Python for showcasing products and taking orders.

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

## Calorie Tracker Bot
This bot helps track daily calories via photos in Telegram.

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set `TELEGRAM_TOKEN` environment variable with your bot token.
3. Run the bot:
   ```bash
   python calorie_bot.py
   ```

### Usage
- Send a food photo to estimate calories.
- `/limit <calories>` – set daily limit.
- `/remaining` – show remaining calories today.
- `/summary` – show today's entries.
- `/delete <n>` – delete entry n.
- `/update <n> <calories>` – update entry n.
