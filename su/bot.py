import time
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# إعدادات البوت
TOKEN = '7801589670:AAEF9UsLE015WkQWaKFO6H4G6aGsHGVD988'
admin_ids = [7585290211]  # معرفات المسؤولين
email_list = ['gfkfgthfhskfjfj2@gmail.com', 'jnvhkbjggjn@gmail.com', 'djdjjjn913@gmail.com', 'jejejrjrnnb@outlook.sa', 'rkkrmmnbb@outlook.sa']  # الإيميلات المدخلة يدويًا
email_index = 0
start_time = time.time()  # وقت بدء الإرسال
total_sent_count = 0  # عداد الرسائل المرسلة

# إعداد تسجيل الأخطاء
logging.basicConfig(
    filename='bot_errors.log',  # تخزين الأخطاء في ملف
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء البوت
bot = Bot(token=TOKEN)

# إرسال طلب دعم (محاكاة)
def send_support_request(message, email, phone):
    # محاكاة نجاح الإرسال
    return True  # إذا كان الطلب ناجحًا

# تدوير الإيميلات
def rotate_emails(emails):
    emails.append(emails.pop(0))  # نقل الإيميل الأول إلى آخر القائمة

# وظيفة إرسال البلاغات
async def start_sending(chat_id, message, emails, phone, context):
    global email_index, start_time, total_sent_count

    while True:  # استمر في إرسال الإيميلات بشكل دائم
        try:
            # تغيير الإيميلات كل 30 دقيقة
            if (time.time() - start_time) >= 1800:
                rotate_emails(emails)
                start_time = time.time()

            current_email = emails[email_index]
            email_num = email_index + 1  # رقم الإيميل الحالي

            if send_support_request(message, current_email, phone):
                total_sent_count += 1  # زيادة العداد عند الإرسال الناجح
                await context.bot.send_message(chat_id, f"✅ تم إرسال الإيميل {email_num} بنجاح باستخدام الإيميل: {current_email}\n🔢 إجمالي الرسائل المرسلة: {total_sent_count}")
            else:
                await context.bot.send_message(chat_id, f"❌ فشل في إرسال الإيميل {email_num} باستخدام الإيميل: {current_email}\n🔢 إجمالي الرسائل المرسلة: {total_sent_count}")

            # إرسال زر حالة "أونلاين" مع عدد الرسائل المرسلة
            await send_online_status(chat_id, total_sent_count)

            # التبديل إلى الإيميل التالي
            email_index = (email_index + 1) % len(emails)  # التبديل بين الإيميلات بشكل دائري

            # تقليل التأخير بين كل رسالة
            await asyncio.sleep(0.6)  # تأخير 0.6 ثانية بين كل رسالة
        except Exception as e:
            logger.error(f"Error during sending emails: {str(e)}")
            await context.bot.send_message(chat_id, "❌ حدث خطأ أثناء الإرسال. سيتم إعادة المحاولة قريبًا.")

# إرسال زر "أونلاين" مع عدد الرسائل المرسلة
async def send_online_status(chat_id, total_sent_count):
    # إنشاء زر حالة أونلاين مع عدد الرسائل المرسلة
    keyboard = [
        [InlineKeyboardButton(f"📤 تم إرسال {total_sent_count} رسالة", callback_data='online_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id, "📱 حالة أونلاين:", reply_markup=reply_markup)

# بدء التفاعل مع البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # استجابة لبدء المحادثة
    await update.message.reply_text("مرحبًا! 👋 الرسائل ستبدأ الآن باستخدام الإيميلات المدخلة يدويًا.")
    context.user_data['step'] = 'message'  # تحديد الخطوة الأولى

# استقبال الرسالة من المستخدم
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    step = context.user_data.get('step', '')

    try:
        # تحقق من المرحلة الحالية وتحديثها بناءً على المدخلات
        if step == 'message':
            context.user_data['message'] = text  # تخزين الرسالة
            context.user_data['step'] = 'phone'  # الانتقال للمرحلة التالية
            await update.message.reply_text("شكراً! ✨ الآن، من فضلك أرسل رقم الهاتف.")
        
        elif step == 'phone':
            context.user_data['phone'] = text  # تخزين رقم الهاتف
            await update.message.reply_text("🔄 بدء إرسال البلاغات...")
            message_text = context.user_data['message']
            emails = email_list  # استخدام الإيميلات المدخلة يدويًا
            phone = context.user_data['phone']

            await start_sending(chat_id, message_text, emails, phone, context)
        
        else:
            # إذا كانت الخطوة غير معرفة أو في حالة أي خطأ، نعيد الطلب من المستخدم
            await update.message.reply_text("❓ حدث خطأ في التفاعل. يرجى المحاولة من جديد باستخدام /start.")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ غير متوقع. حاول مرة أخرى.")

# تشغيل البوت
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()