import logging
import asyncio
import random
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = '8355856932:AAG47FU2fp5v8iak4j0oaLBRhnzU813RLA8'

# ذاكرة لتخزين وقت آخر رسالة لكل مستخدم
user_last_msg_time = {}
enabled_chats = set()

prayers = [
    "الله يفرّج همك ويحقق لك كل اللي في بالك 🤍",
    "الله يكتب لك الخير وين ما كان ويرضيك فيه 🌿",
    "ربي يسعدك ويشرح صدرك وييسر أمرك ✨"
]

async def send_athkar(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    text = "🤍 أذكار الصباح" if job.data == "morning" else "🤎 أذكار المساء"
    for chat_id in list(enabled_chats):
        try: await context.bot.send_message(chat_id=chat_id, text=text)
        except: pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    
    user_id = update.message.from_user.id
    now = datetime.now()

    # --- نظام الحماية من الرسايل السريعة (حتى لو مختلفة) ---
    if user_id in user_last_msg_time:
        last_time = user_last_msg_time[user_id]
        # إذا كانت الفترة بين الرسالة الحالية والسابقة أقل من 3 ثوانٍ
        if (now - last_time).total_seconds() < 3:
            try:
                await update.message.delete()
                return # يخرج ولا يكمل معالجة الرسالة
            except: pass
    
    # تحديث وقت آخر رسالة للمستخدم
    user_last_msg_time[user_id] = now

    # الرد على كلمة "ادعولي"
    if update.message.text and "ادعولي" in update.message.text:
        await update.message.reply_text(random.choice(prayers))

async def enable_athkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    enabled_chats.add(update.message.chat_id)
    await update.message.reply_text("✅ تم تفعيل الحماية القصوى والأذكار!")

def main():
    application = Application.builder().token(TOKEN).build()
    job_queue = application.job_queue
    tz = pytz.timezone('Asia/Riyadh')
    
    job_queue.run_daily(send_athkar, time=datetime.strptime("05:00", "%H:%M").time().replace(tzinfo=tz), data="morning")
    job_queue.run_daily(send_athkar, time=datetime.strptime("16:30", "%H:%M").time().replace(tzinfo=tz), data="evening")

    application.add_handler(CommandHandler("enable_athkar", enable_athkar))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()
