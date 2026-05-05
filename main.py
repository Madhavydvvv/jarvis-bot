import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import asyncio
import logging
import os
import sys

import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ai-pa-bot")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

DEFAULT_MODELS = [
    "google/gemma-3-4b-it:free",
    "google/gemma-3-12b-it:free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]

_models_env = os.environ.get("OPENROUTER_MODEL", "").strip()
MODELS = [m.strip() for m in _models_env.split(",") if m.strip()] or DEFAULT_MODELS

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set.")
    sys.exit(1)
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY is not set.")
    sys.exit(1)


def _try_model(model: str, prompt: str):
    """Return (content, retryable_error_msg). On success content is set; on a
    retryable failure (rate limit / model unavailable / 5xx) returns
    (None, msg). On a hard failure returns (error_message_to_user, None)."""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
    except requests.RequestException as e:
        logger.warning("Network error on %s: %s", model, e)
        return None, f"network error: {e}"

    try:
        data = response.json()
    except ValueError:
        logger.warning(
            "Non-JSON from %s status=%s body=%s",
            model,
            response.status_code,
            response.text[:300],
        )
        return None, f"non-json response (status {response.status_code})"

    logger.info("Model %s status=%s", model, response.status_code)

    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"], None

    err = data.get("error") if isinstance(data, dict) else None
    msg = ""
    if isinstance(err, dict):
        msg = err.get("message", "") or ""

    retryable = response.status_code in (404, 429, 500, 502, 503, 504)
    if retryable:
        logger.warning("Retryable error on %s: %s %s", model, response.status_code, msg)
        return None, f"{response.status_code}: {msg}"

    return f"Error ({response.status_code}): {msg or 'Unknown error.'}", None


def ask_ai(prompt: str) -> str:
    failures = []
    for model in MODELS:
        content, retryable_msg = _try_model(model, prompt)
        if content is not None:
            return content
        failures.append(f"{model} -> {retryable_msg}")
    logger.error("All models failed: %s", " | ".join(failures))
    return (
        "All free models are currently unavailable or rate-limited. "
        "Please try again in a minute."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    logger.info("Message from %s: %s", update.effective_user.id, user_text)

    chat_id = update.effective_chat.id
    stop_typing = asyncio.Event()

    async def keep_typing() -> None:
        while not stop_typing.is_set():
            try:
                await context.bot.send_chat_action(
                    chat_id=chat_id, action=ChatAction.TYPING
                )
            except Exception as e:
                logger.warning("send_chat_action failed: %s", e)
                return
            try:
                await asyncio.wait_for(stop_typing.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                pass

    typing_task = asyncio.create_task(keep_typing())
    try:
        reply = await asyncio.to_thread(ask_ai, user_text)
    finally:
        stop_typing.set()
        await typing_task

    logger.info("Reply: %s", reply[:200])
    await update.message.reply_text(reply)


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
