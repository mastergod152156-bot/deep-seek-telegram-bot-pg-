import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import time

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7606367267'))

# Validate environment variables
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable is required")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store authorized users
authorized_users = {ADMIN_ID}

# Bot statistics
bot_stats = {
    'start_time': time.time(),
    'total_questions': 0,
    'active_users': set()
}

class DeepSeekBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def ask_deepseek(self, question, user_id):
        """Send question to DeepSeek API and return response"""
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that provides clear and concise responses in Burmese language."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "stream": False,
                "max_tokens": 2000
            }
            
            logger.info(f"Sending request to DeepSeek API for user {user_id}")
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"DeepSeek API response received for user {user_id}")
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API timeout")
            return "❌ တုံ့ပြန်မှုရယူရန် အချိန်ကြာမြင့်နေပါသည်။ ကျေးဇူးပြု၍ နောက်မှထပ်ကြိုးစားပါ။"
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API error: {e}")
            return "❌ ဆက်သွယ်ရေးအမှား ဖြစ်နေပါတယ်။ ကျေးဇူးပြု၍ နောက်မှထပ်ကြိုးစားပါ။"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "❌ တုံ့ပြန်မှုရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်။"

# Initialize DeepSeek bot
deepseek_bot = DeepSeekBot(DEEPSEEK_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when the command /start is issued."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Update stats
    bot_stats['active_users'].add(user_id)
    
    welcome_text = f"""
🤖 **မင်္ဂလာပါ {user_name}!**

DeepSeek AI Bot မှကြိုဆိုပါတယ်။

**အသုံးပြုနည်းများ:**
• မေးခွန်းတစ်ခုခုမေးပါ၊ ကျွန်တော်ဖြေပေးပါမယ်
• /help - အကူအညီရယူရန်
• /stats - Bot စာရင်းဇယားကြည့်ရန်

**Admin Commands:**
/authorize [user_id] - အသုံးပြုခွင့်ပေးရန်
/unauthorize [user_id] - အသုံးပြုခွင့်ရုပ်သိမ်းရန်
/list_users - အသုံးပြုခွင့်ရှိသူများစာရင်း

မေးခွန်းမေးရန်:
/ask [မေးခွန်း]
သို့မဟုတ် ရိုးရိုးစာသားပို့ပါ

🌐 **Hosted on Render (24/7)**
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')
    logger.info(f"User {user_id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when the command /help is issued."""
    help_text = """
🆘 **အသုံးပြုနည်းလမ်းညွှန်**

**User Commands:**
/start - Bot ကိုစတင်ရန်
/help - အကူအညီရယူရန်
/stats - Bot စာရင်းဇယားကြည့်ရန်
/ask [မေးခွန်း] - DeepSeek AI ကိုမေးမြန်းရန်

**Admin Commands:**
/authorize [user_id] - အသုံးပြုခွင့်ပေးရန်
/unauthorize [user_id] - အသုံးပြုခွင့်ရုပ်သိမ်းရန်
/list_users - အသုံးပြုခွင့်ရှိသူများစာရင်း

**ဥပမာများ:**
/ask Python programming ကိုဘယ်လိုစသင်မလဲ?
သို့မဟုတ်
ရိုးရိုးစာသားအဖြစ် "Hello" ဟုရိုက်ပို့ပါ

**မှတ်ချက်:** ဤ bot သည် DeepSeek AI နှင့်ချိတ်ဆက်ထားပြီး Render cloud ပေါ်တွင် 24/7 အလုပ်လုပ်နေပါသည်။
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    user_id = update.effective_user.id
    
    uptime = time.time() - bot_stats['start_time']
    days = int(uptime // 86400)
    hours = int((uptime % 86400) // 3600)
    minutes = int((uptime % 3600) // 60)
    
    stats_text = f"""
📊 **Bot စာရင်းဇယား**

⏰ **Uptime:** {days} ရက်, {hours} နာရီ, {minutes} မိနစ်
❓ **မေးခွန်းစုစုပေါင်း:** {bot_stats['total_questions']}
👥 **အသုံးပြုသူများ:** {len(bot_stats['active_users'])}
✅ **ခွင့်ပြုထားသောအသုံးပြုသူများ:** {len(authorized_users)}
🌐 **Server:** Render Worker (24/7 Always-on)
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command with inline question"""
    user_id = update.effective_user.id
    
    # Check authorization
    if user_id not in authorized_users:
        await update.message.reply_text("❌ သင့်တွင် အသုံးပြုခွင့်မရှိပါ။ Admin ထံမှ ခွင့်ပြုချက်ရယူပါ။")
        return
    
    if not context.args:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ မေးခွန်းတစ်ခုထည့်ပါ။\nဥပမာ: /ask Python ကိုဘယ်လိုသင်ယူမလဲ?")
        return
    
    question = ' '.join(context.args)
    await send_to_deepseek(update, question, user_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check authorization
    if user_id not in authorized_users:
        await update.message.reply_text("❌ သင့်တွင် အသုံးပြုခွင့်မရှိပါ။ Admin ထံမှ ခွင့်ပြုချက်ရယူပါ။")
        return
    
    # Ignore messages that are commands
    if message_text.startswith('/'):
        return
    
    await send_to_deepseek(update, message_text, user_id)

async def send_to_deepseek(update: Update, question: str, user_id: int):
    """Send question to DeepSeek and handle response"""
    # Update stats
    bot_stats['total_questions'] += 1
    bot_stats['active_users'].add(user_id)
    
    # Send typing action
    await update.message.chat.send_action(action="typing")
    
    try:
        logger.info(f"Processing question from user {user_id}: {question[:100]}...")
        response = deepseek_bot.ask_deepseek(question, user_id)
        
        # Split long messages (Telegram has 4096 character limit)
        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, chunk in enumerate(chunks):
                await update.message.reply_text(f"*အပိုင်း {i+1}:*\n{chunk}", parse_mode='Markdown')
        else:
            await update.message.reply_text(response)
            
        logger.info(f"Response sent to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error in send_to_deepseek: {e}")
        await update.message.reply_text("❌ တုံ့ပြန်မှုပေးရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်။")

# Admin commands
async def authorize_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Authorize a user to use the bot"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ ဤ command ကိုအသုံးပြုရန် ခွင့်မရှိပါ။")
        return
    
    if not context.args:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ user ID ထည့်ပါ။\nဥပမာ: /authorize 123456789")
        return
    
    try:
        target_user_id = int(context.args[0])
        authorized_users.add(target_user_id)
        await update.message.reply_text(f"✅ User {target_user_id} အား အသုံးပြုခွင့်ပေးလိုက်သည်။")
        logger.info(f"Admin {user_id} authorized user {target_user_id}")
    except ValueError:
        await update.message.reply_text("❌ User ID သည် ဂဏန်းတစ်ခုဖြစ်ရပါမည်။")

async def unauthorize_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unauthorized a user from using the bot"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ ဤ command ကိုအသုံးပြုရန် ခွင့်မရှိပါ။")
        return
    
    if not context.args:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ user ID ထည့်ပါ။\nဥပမာ: /unauthorize 123456789")
        return
    
    try:
        target_user_id = int(context.args[0])
        if target_user_id in authorized_users:
            authorized_users.remove(target_user_id)
            await update.message.reply_text(f"✅ User {target_user_id} ၏ အသုံးပြုခွင့်ကို ရုပ်သိမ်းလိုက်သည်။")
            logger.info(f"Admin {user_id} unauthorized user {target_user_id}")
        else:
            await update.message.reply_text(f"❌ User {target_user_id} သည် အသုံးပြုခွင့်စာရင်းတွင်မရှိပါ။")
    except ValueError:
        await update.message.reply_text("❌ User ID သည် ဂဏန်းတစ်ခုဖြစ်ရပါမည်။")

async def list_authorized_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all authorized users"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ ဤ command ကိုအသုံးပြုရန် ခွင့်မရှိပါ။")
        return
    
    if not authorized_users:
        await update.message.reply_text("❌ အသုံးပြုခွင့်ရှိသူ မရှိသေးပါ။")
        return
    
    users_list = "\n".join([f"• {user_id}" for user_id in authorized_users])
    await update.message.reply_text(f"**အသုံးပြုခွင့်ရှိသူများ:**\n{users_list}", parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    logger.info("🚀 Starting DeepSeek Telegram Bot on Render...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("ask", ask_question))
    application.add_handler(CommandHandler("authorize", authorize_user))
    application.add_handler(CommandHandler("unauthorize", unauthorize_user))
    application.add_handler(CommandHandler("list_users", list_authorized_users))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("✅ Bot is running on Render Worker (24/7 Always-on)...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
