import logging
import asyncio
import random
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- ضعي التوكن الخاص بكِ هنا بين علامتي التنصيص ---
TOKEN = '8355856932:AAG47FU2fp5v8iak4j0oaLBRhnzU813RLA8'

# إعدادات الذاكرة ومنع التكرار
seen_messages = {}
enabled_chats = set()

# قائمة الأدعية والردود لـ "ادعولي"
prayers = [
    "الله يفرّج همك ويحقق لك كل اللي في بالك 🤍\nنصيحة: خلك قريب من ربك، ترى الفرج يجي من حيث ما تتوقع\nآية: “وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا”",
    "الله يكتب لك الخير وين ما كان ويرضيك فيه\nنصيحة: لا تستعجل، كل شيء مكتوب لك بيجي في وقتة المناسب\nآية: “وَعَسَىٰ أَن تَكْرَهُوا شَيْئًا وَهُوَ خَيْرٌ لَّكُمْ”",
    "ربي يسعدك ويشرح صدرك وييسر أمرك\nنصيحة: فضفض لربك دائمًا، الدعاء يخفف كل شيء\nآية: “أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ”"
]

async def send_athkar(app, type):
    if type == "morning":
        text = (
            "🤍 أذكار الصباح | نُور لِيومك 🤍\n\n"
            "🌿 \"أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ\"\n\n"
            "سبحان الله وبحمده عدد خلقه ورضا نفسه وزِنةَ عرشه ومداد كلماته\n\n"
            "✨ \"🌤️ يومكم مليء بالتوفيق والسعادة.\"\n\n"
            "آية الكرسي + المعوذات (٣ مرات) 🌿✅"
        )
    else:
        text = (
            "🤎 أذكار المساء | طُمأنينة لِقلبك 🤎\n\n"
            "🌿 \"أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ\"\n\n"
            "✨ \"أَعُوذُ بِكَلِمَاتِ اللهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ\"\n(٣ مرات)\n\n"
            "آية الكرسي + المعوذات (٣ مرات) 🌿✅"
        )
    
    for chat_id in enabled_chats:
        try:
            await app.bot.send_message(chat_id=chat_id, text=text)
        except: pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.message.chat_id
    text = update.message.text
    now = datetime.now()

    # منع التكرار (حذف فوري وصامت)
    key = f"{chat_id}:{text}"
    if key in seen_messages:
        last_time = seen_messages[key]
        if (now - last_time).total_seconds() < 30:
            try:
                await update.message.delete()
                return
            except: pass
    seen_messages[key] = now

    # الرد على "ادعولي"
    if "ادعولي" in text:
        await update.message.reply_text(random.choice(prayers))

async def enable_athkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    enabled_chats.add(update.message.chat_id)
    await update.message.reply_text("✅ تم تفعيل الأذكار التلقائية في هذا القروب!")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # الجدولة بتوقيت الرياض
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Riyadh'))
    scheduler.add_job(send_athkar, 'cron', hour=5, minute=0, args=[app, "morning"])
    scheduler.add_job(send_athkar, 'cron', hour=16, minute=30, args=[app, "evening"])
    scheduler.start()

    app.add_handler(CommandHandler("enable_athkar", enable_athkar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
