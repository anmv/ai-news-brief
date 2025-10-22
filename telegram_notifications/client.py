import asyncio
import re

from telegram.constants import ParseMode

import telegram

# Telegram message length limit
MAX_MESSAGE_LENGTH = 4096


def clean_html_for_telegram(text: str) -> str:
    """
    Cleans HTML to only include Telegram-supported tags.

    Supported tags: b, strong, i, em, u, ins, s, strike, del, code, pre, a, tg-spoiler

    Args:
        text: HTML text to clean

    Returns:
        Cleaned text with only supported tags
    """
    # Replace <br>, <br/>, <br /> with newline
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Normalize tags - use consistent variants
    text = re.sub(r'<strong>', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'</strong>', '</b>', text, flags=re.IGNORECASE)
    text = re.sub(r'<em>', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'</em>', '</i>', text, flags=re.IGNORECASE)

    # Remove unsupported tags but keep their content
    # List of unsupported tags to remove
    unsupported_tags = [
        'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
        'img', 'video', 'audio', 'iframe', 'script', 'style', 'head', 'html', 'body'
    ]

    # Replace block-level tags with newlines to preserve spacing
    block_tags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']
    for tag in block_tags:
        # Replace closing tags with newline
        text = re.sub(f'</{tag}>', '\n', text, flags=re.IGNORECASE)
        # Remove opening tags
        text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)

    # Remove inline tags (keep content, no newline)
    inline_tags = ['span', 'ul', 'ol', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
                   'img', 'video', 'audio', 'iframe', 'script', 'style', 'head', 'html', 'body']
    for tag in inline_tags:
        text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(f'</{tag}>', '', text, flags=re.IGNORECASE)

    # Clean up multiple consecutive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    return text.strip()


def split_message_smart(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Splits a long message into smaller chunks intelligently.

    Tries to split by:
    1. Double line breaks (between news items)
    2. Single line breaks (between paragraphs)
    3. Sentences
    4. Words

    Args:
        text: The text to split.
        max_length: Maximum length of each chunk.

    Returns:
        List of message chunks.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    # Split by double line breaks first (news items separator)
    sections = re.split(r'\n\n+', text)

    for section in sections:
        # If adding this section would exceed the limit
        if len(current_chunk) + len(section) + 2 > max_length:
            # If current chunk has content, save it
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # If the section itself is too long, split it further
            if len(section) > max_length:
                # Try splitting by single line breaks
                lines = section.split('\n')
                for line in lines:
                    if len(current_chunk) + len(line) + 1 > max_length:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""

                        # If even a single line is too long, split by sentences
                        if len(line) > max_length:
                            sentences = re.split(r'([.!?]+\s+)', line)
                            temp_sentence = ""
                            for i in range(0, len(sentences), 2):
                                sentence = sentences[i]
                                separator = sentences[i + 1] if i + 1 < len(sentences) else ""

                                if len(temp_sentence) + len(sentence) + len(separator) > max_length:
                                    if temp_sentence:
                                        chunks.append(temp_sentence.strip())
                                        temp_sentence = ""

                                    # If a single sentence is still too long, split by words
                                    if len(sentence) > max_length:
                                        words = sentence.split()
                                        temp_word_chunk = ""
                                        for word in words:
                                            if len(temp_word_chunk) + len(word) + 1 > max_length:
                                                if temp_word_chunk:
                                                    chunks.append(temp_word_chunk.strip())
                                                temp_word_chunk = word
                                            else:
                                                temp_word_chunk += (" " if temp_word_chunk else "") + word
                                        if temp_word_chunk:
                                            current_chunk = temp_word_chunk
                                    else:
                                        temp_sentence = sentence + separator
                                else:
                                    temp_sentence += sentence + separator

                            if temp_sentence:
                                current_chunk = temp_sentence
                        else:
                            current_chunk = line
                    else:
                        current_chunk += ("\n" if current_chunk else "") + line
            else:
                current_chunk = section
        else:
            current_chunk += ("\n\n" if current_chunk else "") + section

    # Add any remaining content
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def send_message(user_id: int, message_text: str, bot_token: str):
    """
    Sends a message to a Telegram user.
    Automatically cleans HTML and splits long messages into multiple parts.

    Args:
        user_id: The user's Telegram ID.
        message_text: The message to send (can be longer than Telegram's limit).
        bot_token: The Telegram bot token.
    """
    # Clean HTML to only include supported tags
    cleaned_text = clean_html_for_telegram(message_text)

    # Split message if it's too long
    message_chunks = split_message_smart(cleaned_text)

    request = telegram.request.HTTPXRequest()
    async with telegram.Bot(token=bot_token, request=request) as bot:
        for i, chunk in enumerate(message_chunks):
            # Add part indicator if message was split
            if len(message_chunks) > 1:
                part_info = f"\n\n<i>Часть {i + 1} из {len(message_chunks)}</i>"
                chunk_with_info = chunk + part_info
            else:
                chunk_with_info = chunk

            await bot.send_message(
                chat_id=user_id,
                text=chunk_with_info,
                parse_mode=ParseMode.HTML
            )

            # Small delay between messages to avoid rate limits
            if i < len(message_chunks) - 1:
                await asyncio.sleep(0.5)

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
