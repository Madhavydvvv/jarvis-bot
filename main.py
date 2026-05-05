import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 Load environment variables

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🧠 Setup logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

# 🤖 AI function

def ask_ai(prompt):
try:
response = requests.post(
"https://openrouter.ai/api/v1/chat/completions",
headers={
"Authorization": f"Bearer {OPENROUTER_API_KEY}",
"Content-Type": "application/json"
},
json={
"model": "openrouter/auto",
"messages": [
{
"role": "system",
"content": "You are Jarvis, a smart, concise, and confident AI assistant like Iron Man's Jarvis."
},
{"role": "user", "content": prompt}
]
}
)

```
    data = response.json()
    logger.info(f"API Response: {data}")

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return "Error: AI response failed."

except Exception as e:
    return f"Error: {str(e)}"
```

# 💬 Handle messages

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_text = update.message.text
reply = ask_ai(user_text)
await update.message.reply_text(reply)

# 🚀 Start bot

def main():
if not TELEGRAM_BOT_TOKEN:
raise ValueError("TELEGRAM_BOT_TOKEN is not set")

```
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logger.info("🤖 Jarvis is running...")
app.run_polling()
```

if **name** == "**main**":
main()
