import asyncio
import telegram
from telegram.constants import ParseMode
import httpx

async def send_message(user_id: int, message_text: str, bot_token: str):
    """
    Sends a message to a Telegram user.

    Args:
        user_id: The user's Telegram ID.
        message_text: The message to send.
        bot_token: The Telegram bot token.
    """
    async with httpx.AsyncClient() as http_client:
        bot = telegram.Bot(token=bot_token, request=telegram.request.HTTPXRequest(http_client=http_client))  # type: ignore
        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode=ParseMode.HTML
        )

if __name__ == '__main__':
    # Example usage (for testing purposes)
    # You would need to replace 'YOUR_BOT_TOKEN' and 'YOUR_USER_ID'
    # with your actual bot token and user ID.
    # Also, this needs to be run in an async context.
    async def main():
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            user_id = os.getenv("TELEGRAM_USER_IDS")
            if bot_token and user_id:
                await send_message(int(user_id.split(',')[0]), "<b>Hello</b>, world!", bot_token)
                print("Message sent successfully!")
            else:
                print("TELEGRAM_BOT_TOKEN and TELEGRAM_USER_IDS must be set in .env file")
        except Exception as e:
            print(f"Error sending message: {e}")

    asyncio.run(main())