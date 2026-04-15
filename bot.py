import logging
import os
from pathlib import Path

from telegram import ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "bot_token")
START_FILE = Path(os.getenv("START_FILE", "start.txt"))
USERS_FILE = Path(os.getenv("USERS_FILE", "users.txt"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@your_channel")
MAX_SPOTS = int(os.getenv("MAX_SPOTS", "500"))

# === LOGGING ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def ensure_file_exists(filename: Path) -> None:
    """Create the file if it does not exist yet."""
    filename.touch(exist_ok=True)


def read_file(filename: Path) -> list[str]:
    """Read a text file and return non-empty stripped lines."""
    ensure_file_exists(filename)
    with filename.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def append_to_file(filename: Path, user_id: str) -> None:
    """Append a user ID to the end of a text file."""
    ensure_file_exists(filename)
    with filename.open("a", encoding="utf-8") as file:
        file.write(f"{user_id}\n")


async def is_user_in_channel(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
) -> bool:
    """Check whether a user is a member of the required channel."""
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in {
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
        }
    except Exception as exc:
        logger.warning("Error while checking channel membership: %s", exc)
        return False


def build_membership_keyboard() -> InlineKeyboardMarkup:
    """Create the join/verify keyboard shown to users."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Join Channel",
                    url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}",
                )
            ],
            [InlineKeyboardButton("🔄 Check Again", callback_data="check_membership")],
        ]
    )


async def register_user(user_id: str) -> tuple[bool, int]:
    """Store participation data and return whether the user is new plus total unique users."""
    append_to_file(START_FILE, user_id)

    users = read_file(USERS_FILE)
    is_new_user = user_id not in users

    if is_new_user:
        append_to_file(USERS_FILE, user_id)
        users = read_file(USERS_FILE)

    return is_new_user, len(users)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    if update.effective_user is None or update.message is None:
        return

    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "User"

    is_member = await is_user_in_channel(context, update.effective_user.id)
    if not is_member:
        await update.message.reply_text(
            (
                f"⚠️ Hello {first_name}!\n"
                f"To participate in the giveaway, you must join {CHANNEL_USERNAME}."
            ),
            reply_markup=build_membership_keyboard(),
        )
        return

    users = read_file(USERS_FILE)
    if user_id not in users and len(users) >= MAX_SPOTS:
        await update.message.reply_text(
            "🚫 All giveaway spots are already filled."
        )
        return

    is_new_user, total = await register_user(user_id)

    if is_new_user:
        await update.message.reply_text(
            (
                f"🎉 Hello {first_name}! You are now participating in the giveaway.\n"
                f"Total: *{total}* / {MAX_SPOTS} spots."
            ),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "✅ You are already participating in this giveaway."
        )


async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Re-check membership after the user presses the verification button."""
    query = update.callback_query
    if query is None or query.from_user is None:
        return

    await query.answer()

    user_id = str(query.from_user.id)
    first_name = query.from_user.first_name or "User"

    is_member = await is_user_in_channel(context, query.from_user.id)
    if not is_member:
        await query.edit_message_text(
            (
                f"⚠️ You have not joined {CHANNEL_USERNAME} yet.\n"
                "Join the channel and press *Check Again*."
            ),
            parse_mode="Markdown",
            reply_markup=build_membership_keyboard(),
        )
        return

    users = read_file(USERS_FILE)
    if user_id not in users and len(users) >= MAX_SPOTS:
        await query.edit_message_text("🚫 All giveaway spots are already filled.")
        return

    is_new_user, total = await register_user(user_id)
    if is_new_user:
        await query.edit_message_text(
            (
                f"🎉 Thanks for joining the channel, {first_name}!\n"
                "You are now participating in the giveaway.\n"
                f"Total: *{total}* / {MAX_SPOTS} spots."
            ),
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            "✅ You are already participating in this giveaway.",
            parse_mode="Markdown",
        )


def validate_configuration() -> None:
    """Fail fast if the default placeholder values were not replaced."""
    if BOT_TOKEN == "bot_token":
        raise ValueError("Set the BOT_TOKEN environment variable before starting the bot.")
    if CHANNEL_USERNAME == "@your_channel":
        raise ValueError(
            "Set the CHANNEL_USERNAME environment variable before starting the bot."
        )


def main() -> None:
    """Start the Telegram bot."""
    validate_configuration()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_membership, pattern=r"^check_membership$"))

    print("🤖 Giveaway bot started successfully.")
    app.run_polling()


if __name__ == "__main__":
    main()
