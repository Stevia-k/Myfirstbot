import logging
import asyncio
import random
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# --- ضعي التوكن الخاص بكِ هنا ---
TOKEN = '8355856932:AAG47FU2fp5v8iak4j0oaLBRhnzU813RLA8'

seen_messages = {}
enabled_chats = set()

prayers = [
    "الله يفرّج همك ويحقق لك كل اللي في بالك 🤍",
    "الله يكتب لك الخير وين ما كان ويرضيك فيه 🌿",
    "ربي يسعدك ويشرح صدرك وييسر أمرك ✨"
]

async def send_athkar(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    type = job.data
    text = "🤍 أذكار الصباح" if type == "morning" else "🤎 أذكار المساء"
    # يمكنك إضافة نص الأذكار كاملاً هنا لاحقاً
    for chat_id in list(enabled_chats):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except: pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_id, text, now = update.message.chat_id, update.message.text, datetime.now()
    key = f"{chat_id}:{text}"
    if key in seen_messages and (now - seen_messages[key]).total_seconds() < 30:
        try:
            await update.message.delete()
            return
        except: pass
    seen_messages[key] = now
    if "ادعولي" in text:
        await update.message.reply_text(random.choice(prayers))

async def enable_athkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    enabled_chats.add(update.message.chat_id)
    await update.message.reply_text("✅ تم تفعيل الأذكار التلقائية!")

def main():
    application = Application.builder().token(TOKEN).build()
    job_queue = application.job_queue

    # توقيت الرياض
    tz = pytz.timezone('Asia/Riyadh')
    job_queue.run_daily(send_athkar, time=datetime.strptime("05:00", "%H:%M").time().replace(tzinfo=tz), data="morning")
    job_queue.run_daily(send_athkar, time=datetime.strptime("16:30", "%H:%M").time().replace(tzinfo=tz), data="evening")

    application.add_handler(CommandHandler("enable_athkar", enable_athkar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()
