import feedparser
import asyncio
import schedule
import time
import os
import json
from telegram import Bot
from deep_translator import GoogleTranslator
from config import TOKEN, CHAT_ID, FEEDS, KEYWORDS

bot = Bot(token=TOKEN)

# 📁 file باش نحفظو الأخبار اللي تصيفطات
sent_links_file = os.path.join(os.getcwd(), 'sent_links.json')
sent_links = set()

# تحميل links القديمة
if os.path.exists(sent_links_file):
    try:
        with open(sent_links_file, 'r') as f:
            sent_links = set(json.load(f))
    except:
        sent_links = set()

# 🌍 ترجمة
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='ar').translate(text)
    except:
        return text

# 🎯 فلترة
def is_relevant(title):
    return any(word.lower() in title.lower() for word in KEYWORDS)

# 🚀 إرسال أفضل خبر
async def send_trends():
    print("Checking tech trends...")
    best_article = None
    best_score = 0

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            if entry.link in sent_links:
                continue

            if not is_relevant(entry.title):
                continue

            # scoring (اختيار الأفضل)
            score = len(entry.title)

            if score > best_score:
                best_score = score
                best_article = entry

    # ❌ ما كاين حتى خبر
    if not best_article:
        print("No new relevant articles found")
        return

    # ✅ تجهيز message
    title = translate_text(best_article.title)

    summary = ""
    if hasattr(best_article, "summary"):
        summary = translate_text(best_article.summary[:200])

    message = f"""🚀 *Tech Trend*

📰 *{title}*

📄 {summary}...

🔗 {best_article.link}
"""

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )

        # حفظ link
        sent_links.add(best_article.link)
        with open(sent_links_file, 'w') as f:
            json.dump(list(sent_links), f)

        print("Sent ✔")

    except Exception as e:
        print("Error:", e)

# 🔄 تشغيل async
def run_async():
    asyncio.run(send_trends())

# ⏰ 3 مرات فالنهار
schedule.every().day.at("11:00").do(run_async)
schedule.every().day.at("15:00").do(run_async)
schedule.every().day.at("21:00").do(run_async)

print("Bot is running...")

# 🔁 loop
while True:
    schedule.run_pending()
    time.sleep(30)