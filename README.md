# 🤖 Public Channel Auto-Forward Bot

A Telegram bot for automatically forwarding messages between public channels with optional caption editing.

## 🚀 Features

- **Auto-forward** messages between public channels
- **Caption editing** - find and replace text in captions
- **No download/re-upload** - direct forwarding
- **Progress tracking** with real-time updates
- **Batch processing** with configurable limits
- **Bot token only** - no user session required

## 📋 Commands

- `/start` - Show help menu
- `/forward` - Start auto-forward between channels
- `/forward_edit` - Forward with caption editing
- `/status` - Check bot status
- `/stop` - Stop active forwarding

## ⚡ Quick Setup

1. **Create Bot** via @BotFather
2. **Get API credentials** from https://my.telegram.org
3. **Add bot as admin** in destination channel
4. **Deploy to Render** (one-click below)
5. **Start forwarding** with `/forward`

## 🛠️ Environment Variables

```bash
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id_from_telegram
API_HASH=your_api_hash_from_telegram