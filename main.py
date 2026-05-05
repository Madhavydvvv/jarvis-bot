import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 Environment variables

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🧠 Logging

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
"content": "You are Jarvis, a smart, concise AI assistant."
},
{
"role": "user",
"content": prompt
}
]
}
)

```
    data = response.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return "Error: No response from AI"

except Exception as e:
    return f"Error: {str(e)}"
```

# 💬 Handle messages

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_text = update.message.text
reply = ask_ai(user_text)
await update.message.reply_text(reply)

# 🚀 Main function

def main():
if not TELEGRAM_BOT_TOKEN:
raise ValueError("TELEGRAM_BOT_TOKEN is not set")

```
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logger.info("Jarvis is running...")
app.run_polling()
```

# ▶️ Run

if **name** == "**main**":
main()
