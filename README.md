# Telegram Giveaway Bot

A simple Telegram bot that only lets users join a giveaway after they join a required channel.

## Features

- Checks whether the user joined your Telegram channel
- Saves every `/start` attempt to `start.txt`
- Saves unique participant IDs to `users.txt`
- Prevents duplicate giveaway entries
- Supports a maximum number of giveaway spots
- Uses inline buttons for join and verification

## Project Structure

```text
telegram_giveaway_bot/
├── bot.py
├── requirements.txt
├── .gitignore
├── .env.example
├── instructions.mb
└── README.md
```

## Requirements

- Python 3.10+
- A Telegram bot token from BotFather
- A public Telegram channel or a channel where the bot has permission to inspect members

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` and define your values.

Environment variables used by the bot:

- `BOT_TOKEN` = your Telegram bot token
- `CHANNEL_USERNAME` = your channel username, for example `@my_channel`
- `START_FILE` = file that stores all `/start` attempts
- `USERS_FILE` = file that stores unique users
- `MAX_SPOTS` = maximum number of giveaway participants

### Windows PowerShell example

```powershell
$env:BOT_TOKEN="YOUR_BOT_TOKEN"
$env:CHANNEL_USERNAME="@your_channel"
$env:START_FILE="start.txt"
$env:USERS_FILE="users.txt"
$env:MAX_SPOTS="500"
python bot.py
```

### Linux/macOS example

```bash
export BOT_TOKEN="YOUR_BOT_TOKEN"
export CHANNEL_USERNAME="@your_channel"
export START_FILE="start.txt"
export USERS_FILE="users.txt"
export MAX_SPOTS="500"
python bot.py
```

## How it works

1. The user sends `/start`
2. The bot checks whether the user is in the required channel
3. If the user is not a member, the bot shows:
   - `Join Channel`
   - `Check Again`
4. If the user is a member:
   - their ID is appended to `start.txt`
   - if they are new, their ID is added to `users.txt`
   - the bot confirms participation

## Notes

- `start.txt` can contain repeated IDs by design
- `users.txt` stores only unique giveaway participants
- This bot uses plain text files, so it is simple but not ideal for large scale use
- For production, consider switching to SQLite or PostgreSQL

## GitHub Setup

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## License

You can add your preferred license before publishing.
