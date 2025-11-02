# DeepSeek Telegram Bot

A Telegram bot integrated with DeepSeek AI API, deployed on Render Worker for 24/7 operation.

## Features
- AI-powered responses using DeepSeek API
- User permission system
- Admin controls for user management
- 24/7 always-on deployment on Render

## Deployment on Render

1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Create new Worker Service
4. Connect your GitHub repository
5. Add environment variables
6. Deploy

## Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token
- `DEEPSEEK_API_KEY`: Your DeepSeek API Key
- `ADMIN_ID`: Your Telegram User ID

## Commands
- `/start` - Start the bot
- `/help` - Show help
- `/ask [question]` - Ask AI
- `/stats` - Show bot statistics
