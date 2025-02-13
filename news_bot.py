import logging
import requests
import feedparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio
nest_asyncio.apply()
import asyncio

WEATHER_API_KEY = "84fbcdc3421939e452c3b9c3af6f2473"
NEWS_RSS_FEED = "https://news.ycombinator.com/rss" # Пример RSS-ленты

# Устанавливаем базовую настройку логирования
logging.basicConfig(format="%(asctime)s - %(name)s %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        feed = feedparser.parse(NEWS_RSS_FEED)
        news_item = feed.entries[:5]
        response = "\n\n".join([f"{i+1}. {item.title}\n{item.link}" for i, item in enumerate(news_item)])
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Не удалось загрузить новости. Попробуйте снова позже.")
        logger.error(f"Error fetching news: {e}")

# Функция для обработки команды /weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "Бишкек"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            await update.message.reply_text("Не удалось получить данные о погоде для {city}. Проверьте название города.")
        else:
            temp = response["main"]["temp"]
            description = response["weather"][0]["description"]
            await update.message.reply_text(f"Погода в {city}:\nТемпература: {temp}°C\nОписание: {description}")
    except Exception as e:
        await update.message.reply_text("Не удалось получить данные о погоде. Попробуйте снова позже.")
        logger.error(f"Error fetching weather: {e}")

# Главная функция
async def main():
    """Запуск бота"""

    TELEGRAM_API_TOKEN = "7780144810:AAEcZN1xs7Sqk67chJu2ozinejnCsP8zKZg"

    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("weather", weather))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())