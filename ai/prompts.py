"""Prompt template management for AI interactions."""

from config import SUMMARY_CONTENT_MAX_CHARS
from utils.text import truncate_text

def create_article_selection_prompt(links, newsletter_text, max_chars=None):
    """
    Create a prompt for selecting articles.
    
    Args:
        links: List of potential links with context
        newsletter_text: The newsletter content
        max_chars: Maximum characters for newsletter text
        
    Returns:
        A prompt string for article selection
    """
    # Extract URLs and contexts for the prompt
    link_data = []
    for i, link in enumerate(links):
        link_data.append(f"{i+1}. URL: {link['url']}\n   Context: {link['context']}")
    
    links_text = "\n\n".join(link_data)
    
    # Truncate newsletter text if needed
    truncated_text = newsletter_text
    if max_chars:
        truncated_text = truncate_text(newsletter_text, max_chars)
    
    # Construct the prompt
    prompt = f"""
    Find 5-8 relevant articles about AI tech and research from this newsletter:
    {truncated_text}

    Here are the links:
    {links_text}

    Just return the numbers of the best articles (format: "Selected: 1, 3, 5, 7, 8")
    """
    
    return prompt

def create_summary_prompt(newsletter_data, date):
    """
    Create a prompt for newsletter summarization.
    
    Args:
        newsletter_data: Dictionary with newsletter content and links
        date: The newsletter date
        
    Returns:
        A prompt string for summarization
    """
    content = truncate_text(
        newsletter_data['content'], 
        SUMMARY_CONTENT_MAX_CHARS
    )
    
    prompt = f"""
    Сделай краткую новостную сводку по материалам TLDR AI за {date}.

    Пиши полностью на русском языке.

    Главная задача:
    - выбрать 3-5 самых важных новостей;
    - для каждой новости кратко и ясно объяснить, что произошло;
    - для каждой новости кратко объяснить, почему это важно.

    КРИТИЧЕСКИ ВАЖНО:
    - сохраняй конкретику: названия компаний, продуктов, моделей, исследований, даты, цифры и ключевые факты;
    - не превращай новости в абстрактные рассуждения;
    - не добавляй блок с действиями, советами или рекомендациями;
    - не раздувай текст лишним контекстом;
    - если компания или продукт малоизвестны, можно очень кратко пояснить, кто это;
    - не выдумывай детали, которых нет в исходном тексте.

    СТРУКТУРА КАЖДОЙ НОВОСТИ:

    <b>🔹 [Короткий заголовок с названием компании / продукта]</b>

    <b>Что произошло:</b> [Краткое фактическое описание новости с ключевыми деталями]

    <b>Почему это важно:</b> [Кратко объясни значимость новости без лишней аналитики]

    ФОРМАТИРОВАНИЕ:
    - генерируй чистый текст, используя только теги <b> для жирного и <i> для курсива при необходимости
    - начни с заголовка: <b>📰 Краткая AI-сводка - {date}</b>
    - используй эмодзи 🔹 для отдельных новостей
    - разделяй блоки двойным переносом строки, не используй <br> теги
    - общий объём держи в пределах 800 слов, чтобы сообщение помещалось в Telegram
    - сфокусируйся на 3-5 самых важных новостях
    - тон должен быть профессиональным, информативным и понятным
    - не используй HTML-теги, кроме <b> и <i>
    - не используй <p>, <br>, <div>, <h1-h6> и любые другие HTML-теги

    МАТЕРИАЛЫ РАССЫЛКИ:
    {content}
    """
    
    return prompt

def create_qa_prompt(question, newsletter_content, date):
    """
    Create a prompt for Q&A about the newsletter.
    
    Args:
        question: User question
        newsletter_content: The newsletter content
        date: The newsletter date
        
    Returns:
        A prompt string for Q&A
    """
    truncated_content = truncate_text(
        newsletter_content,
        SUMMARY_CONTENT_MAX_CHARS
    )
    
    prompt = f"""
    Ответь на вопрос по выпуску TLDR AI от {date}.
    
    Сначала постарайся ответить, опираясь на материалы рассылки.
    Если в рассылке нет информации для точного ответа, можно использовать общие знания, чтобы дать полезный и корректный ответ.
    
    Пиши по-русски.
    Отвечай кратко, но содержательно.
    
    МАТЕРИАЛЫ РАССЫЛКИ:
    {truncated_content}
    
    ВОПРОС:
    {question}
    """
    
    return prompt
