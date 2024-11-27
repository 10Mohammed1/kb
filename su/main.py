from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# وظيفة البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أنا البوت الخاص بك. كيف يمكنني مساعدتك؟")

# وظيفة بسيطة للرد على الأوامر
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هذه قائمة بالأوامر:\n/start - لبدء البوت\n/help - للحصول على المساعدة")

if __name__ == "__main__":
    # التوكن الخاص بالبوت
    TOKEN = "7711679494:AAFM6Qd89RF04AQSyUBq43u60z4lyfbovUI"

    # إعداد التطبيق
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة أوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # تشغيل البوت
    app.run_polling()