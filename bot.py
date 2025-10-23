import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PublicAutoForwardBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        
        # Validate required environment variables
        if not all([self.bot_token, self.api_id, self.api_hash]):
            raise ValueError("Missing required environment variables")
        
        self.app = Client(
            "public_autoforward_bot",
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.bot_token
        )
        
        self.is_forwarding = False
        self.user_states = {}  # For multi-step conversations
        self.setup_handlers()
        
        logger.info("🤖 Public Auto-Forward Bot Initialized!")

    def setup_handlers(self):
        """Setup all message handlers"""
        
        @self.app.on_message(filters.command("start"))
        async def start_handler(client, message):
            await self.handle_start(message)

        @self.app.on_message(filters.command("forward"))
        async def forward_handler(client, message):
            await self.handle_forward(message)

        @self.app.on_message(filters.command("forward_edit"))
        async def forward_edit_handler(client, message):
            await self.handle_forward_edit(message)

        @self.app.on_message(filters.command("status"))
        async def status_handler(client, message):
            await self.handle_status(message)

        @self.app.on_message(filters.command("stop"))
        async def stop_handler(client, message):
            await self.handle_stop(message)

        @self.app.on_message(filters.private & filters.text)
        async def conversation_handler(client, message):
            await self.handle_conversation(message)

    async def handle_start(self, message: Message):
        """Handle /start command"""
        help_text = """
🤖 **Public Channel Auto-Forward Bot**

🚀 **Features:**
• Auto-forward messages between public channels
• Edit captions while forwarding
• No download/re-upload - direct forwarding
• Batch processing with progress updates

📋 **Commands:**
`/forward` - Auto-forward between channels
`/forward_edit` - Forward with caption editing
`/status` - Check bot status
`/stop` - Stop active forwarding

⚡ **How to use:**
1. Add bot as admin in destination channel
2. Use commands and follow the steps
3. Bot will handle everything automatically

🔒 **Security:** Bot token only - no user session required!
        """
        await message.reply(help_text)

    async def handle_forward(self, message: Message):
        """Start simple forward process"""
        try:
            await message.reply(
                "🔄 **Auto-Forward Setup**\n\n"
                "📥 **Step 1:** Send the **source channel**\n"
                "• Username: `@channel_username`\n"
                "• Public link: `https://t.me/channel_username`\n\n"
                "I'll read from this public channel."
            )
            self.user_states[message.from_user.id] = {
                'mode': 'simple_forward', 
                'step': 'waiting_source',
                'chat_id': message.chat.id
            }
            
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")
            logger.error(f"Start forward error: {e}")

    async def handle_forward_edit(self, message: Message):
        """Start forward with caption editing"""
        try:
            await message.reply(
                "🔧 **Auto-Forward with Caption Editing**\n\n"
                "📥 **Step 1:** Send the **source channel**\n"
                "• Username: `@channel_username`\n"
                "• Public link: `https://t.me/channel_username`\n\n"
                "I'll read from this public channel."
            )
            self.user_states[message.from_user.id] = {
                'mode': 'edit_forward', 
                'step': 'waiting_source',
                'chat_id': message.chat.id
            }
            
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")
            logger.error(f"Start forward_edit error: {e}")

    async def handle_status(self, message: Message):
        """Check bot status"""
        status = "🔄 **Forwarding in Progress**" if self.is_forwarding else "✅ **Ready & Idle**"
        active_users = len(self.user_states)
        
        status_text = f"""
{status}

📊 **Stats:**
• Active conversations: {active_users}
• Forwarding: {'Yes' if self.is_forwarding else 'No'}

💡 Use `/forward` to start auto-forwarding!
        """
        await message.reply(status_text)

    async def handle_stop(self, message: Message):
        """Stop active forwarding"""
        if self.is_forwarding:
            self.is_forwarding = False
            await message.reply("🛑 **Forwarding stopped!**")
            logger.info("Forwarding stopped by user")
        else:
            await message.reply("ℹ️ **No active forwarding to stop.**")

    async def handle_conversation(self, message: Message):
        """Handle multi-step conversation"""
        try:
            user_id = message.from_user.id
            if user_id not in self.user_states:
                return

            user_data = self.user_states[user_id]
            current_step = user_data['step']
            user_text = message.text.strip()

            if current_step == 'waiting_source':
                await self._handle_source_step(user_data, user_text, message)
                
            elif current_step == 'waiting_destination':
                await self._handle_destination_step(user_data, user_text, message)
                
            elif current_step == 'waiting_find_text':
                await self._handle_find_text_step(user_data, user_text, message)
                
            elif current_step == 'waiting_replace_text':
                await self._handle_replace_text_step(user_data, user_text, message)
                
            elif current_step == 'waiting_limits':
                await self._handle_limits_step(user_data, user_text, message)

        except Exception as e:
            await message.reply(f"❌ **Error in conversation:** {str(e)}")
            logger.error(f"Conversation error: {e}")
            if user_id in self.user_states:
                del self.user_states[user_id]

    async def _handle_source_step(self, user_data, user_text, message):
        """Handle source channel input"""
        user_data['source'] = user_text
        user_data['step'] = 'waiting_destination'
        
        await message.reply(
            "✅ **Source channel saved!**\n\n"
            "📤 **Step 2:** Send the **destination channel**\n"
            "• Username: `@channel_username`\n"
            "• Channel ID: `-1001234567890`\n\n"
            "⚠️ **Important:** Bot must be admin in destination channel!"
        )

    async def _handle_destination_step(self, user_data, user_text, message):
        """Handle destination channel input"""
        user_data['destination'] = user_text
        
        if user_data['mode'] == 'edit_forward':
            user_data['step'] = 'waiting_find_text'
            await message.reply(
                "✅ **Destination saved!**\n\n"
                "🔍 **Step 3:** What text should I **find** in captions?\n"
                "**Examples:**\n"
                "• `@Username`\n"
                "• `unwanted text`\n"
                "• `HaRsHiT2027`"
            )
        else:
            user_data['step'] = 'waiting_limits'
            await message.reply(
                "✅ **Destination saved!**\n\n"
                "📊 **Step 3:** Set forwarding limits\n"
                "Send message count or `-` for no limit:\n"
                "**Examples:**\n"
                "• `100` - Forward 100 messages\n"
                "• `500` - Forward 500 messages\n"
                "• `-` - No limit (forward all)"
            )

    async def _handle_find_text_step(self, user_data, user_text, message):
        """Handle find text input"""
        user_data['find_text'] = user_text
        user_data['step'] = 'waiting_replace_text'
        
        await message.reply(
            "✅ **Find text saved!**\n\n"
            "✏️ **Step 4:** What should I **replace it with**?\n"
            "Send replacement text or `-` to remove:\n"
            "**Examples:**\n"
            "• `physics wallah` - Replace with this text\n"
            "• `-` - Remove completely\n"
            "• ` ` - Replace with space"
        )

    async def _handle_replace_text_step(self, user_data, user_text, message):
        """Handle replace text input"""
        user_data['replace_text'] = "" if user_text == "-" else user_text
        user_data['step'] = 'waiting_limits'
        
        action = "remove" if user_text == "-" else f"replace with '{user_text}'"
        await message.reply(
            f"✅ **Replace text saved!** (Will {action})\n\n"
            "📊 **Step 5:** Set forwarding limits\n"
            "Send message count or `-` for no limit:\n"
            "**Examples:**\n"
            "• `100` - Forward 100 messages\n"
            "• `-` - No limit (forward all)"
        )

    async def _handle_limits_step(self, user_data, user_text, message):
        """Handle limits input and start forwarding"""
        # Parse limits
        limit = None
        if user_text != "-" and user_text.isdigit():
            limit = int(user_text)
            if limit <= 0:
                await message.reply("❌ Limit must be greater than 0")
                return

        # Get all collected data
        source = user_data['source']
        destination = user_data['destination']
        mode = user_data['mode']

        # Clean up user state
        user_id = message.from_user.id
        del self.user_states[user_id]

        # Check if already forwarding
        if self.is_forwarding:
            await message.reply("❌ **Another forwarding job is running!** Use `/stop` first.")
            return

        await message.reply("🚀 **Starting auto-forward...**")

        # Start the appropriate forwarding process
        if mode == 'edit_forward':
            find_text = user_data['find_text']
            replace_text = user_data['replace_text']
            asyncio.create_task(
                self.execute_edit_forward(message, source, destination, find_text, replace_text, limit)
            )
        else:
            asyncio.create_task(
                self.execute_simple_forward(message, source, destination, limit)
            )

    async def execute_simple_forward(self, message, source, destination, limit):
        """Execute simple forward without editing"""
        try:
            self.is_forwarding = True
            forwarded_count = 0
            
            # Clean source input
            if source.startswith('https://t.me/'):
                source = source.split('/')[-1].lstrip('@')
            source = source.lstrip('@')
            
            # Send initial status
            status_msg = await message.reply(
                f"🚀 **Auto-Forward Started**\n"
                f"**Source:** `{source}`\n"
                f"**Destination:** `{destination}`\n"
                f"**Limit:** {limit or 'No limit'}\n"
                f"**Status:** Starting...\n"
                f"**Progress:** 0 messages"
            )
            
            logger.info(f"Starting simple forward: {source} -> {destination}, limit: {limit}")
            
            # Start forwarding
            async for msg in self.app.get_chat_history(source, limit=limit):
                if not self.is_forwarding:
                    break
                    
                try:
                    await msg.forward(destination)
                    forwarded_count += 1
                    
                    # Update progress every 20 messages
                    if forwarded_count % 20 == 0:
                        await status_msg.edit(
                            f"🚀 **Auto-Forward Progress**\n"
                            f"**Source:** `{source}`\n"
                            f"**Destination:** `{destination}`\n"
                            f"**Status:** Running...\n"
                            f"**Progress:** {forwarded_count} messages forwarded"
                        )
                        logger.info(f"Progress: {forwarded_count} messages forwarded")
                    
                    # Rate limiting
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"Failed to forward message {msg.id}: {e}")
                    continue
            
            # Completion message
            completion_text = (
                f"✅ **Auto-Forward Completed!**\n"
                f"**Source:** `{source}`\n"
                f"**Destination:** `{destination}`\n"
                f"**Total Forwarded:** {forwarded_count} messages\n"
                f"**Status:** Successfully finished!"
            )
            await status_msg.edit(completion_text)
            await message.reply("🎉 **Job completed successfully!**")
            
            logger.info(f"Simple forward completed: {forwarded_count} messages")
            
        except Exception as e:
            error_msg = f"❌ **Forwarding failed:** {str(e)}"
            await message.reply(error_msg)
            logger.error(f"Simple forward error: {e}")
        finally:
            self.is_forwarding = False

    async def execute_edit_forward(self, message, source, destination, find_text, replace_text, limit):
        """Execute forward with caption editing"""
        try:
            self.is_forwarding = True
            forwarded_count = 0
            edited_count = 0
            
            # Clean source input
            if source.startswith('https://t.me/'):
                source = source.split('/')[-1].lstrip('@')
            source = source.lstrip('@')
            
            action = "removed" if replace_text == "" else f"replaced with '{replace_text}'"
            
            # Send initial status
            status_msg = await message.reply(
                f"🔧 **Edit-Forward Started**\n"
                f"**Source:** `{source}`\n"
                f"**Destination:** `{destination}`\n"
                f"**Editing:** {action} '{find_text}'\n"
                f"**Limit:** {limit or 'No limit'}\n"
                f"**Status:** Starting...\n"
                f"**Progress:** 0 messages (0 edited)"
            )
            
            logger.info(f"Starting edit forward: {source} -> {destination}, find: '{find_text}', replace: '{replace_text}'")
            
            # Start forwarding with editing
            async for msg in self.app.get_chat_history(source, limit=limit):
                if not self.is_forwarding:
                    break
                    
                try:
                    # Check if caption needs editing
                    if msg.caption and find_text in msg.caption:
                        new_caption = msg.caption.replace(find_text, replace_text)
                        await msg.copy(destination, caption=new_caption)
                        edited_count += 1
                    else:
                        await msg.forward(destination)
                    
                    forwarded_count += 1
                    
                    # Update progress every 20 messages
                    if forwarded_count % 20 == 0:
                        await status_msg.edit(
                            f"🔧 **Edit-Forward Progress**\n"
                            f"**Source:** `{source}`\n"
                            f"**Destination:** `{destination}`\n"
                            f"**Status:** Running...\n"
                            f"**Progress:** {forwarded_count} messages forwarded\n"
                            f"**Edited:** {edited_count} captions"
                        )
                        logger.info(f"Edit progress: {forwarded_count} forwarded, {edited_count} edited")
                    
                    # Rate limiting
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"Failed to process message {msg.id}: {e}")
                    continue
            
            # Completion message
            completion_text = (
                f"✅ **Edit-Forward Completed!**\n"
                f"**Source:** `{source}`\n"
                f"**Destination:** `{destination}`\n"
                f"**Total Forwarded:** {forwarded_count} messages\n"
                f"**Captions Edited:** {edited_count}\n"
                f"**Action:** {action} '{find_text}'\n"
                f"**Status:** Successfully finished!"
            )
            await status_msg.edit(completion_text)
            await message.reply("🎉 **Job completed successfully!**")
            
            logger.info(f"Edit forward completed: {forwarded_count} forwarded, {edited_count} edited")
            
        except Exception as e:
            error_msg = f"❌ **Edit-forwarding failed:** {str(e)}"
            await message.reply(error_msg)
            logger.error(f"Edit forward error: {e}")
        finally:
            self.is_forwarding = False

    async def run(self):
        """Start the bot"""
        try:
            await self.app.start()
            me = await self.app.get_me()
            logger.info(f"🤖 Bot started successfully: @{me.username}")
            logger.info("🚀 Public Auto-Forward Bot is running...")
            
            # Keep the bot running
            await asyncio.Future()
            
        except Exception as e:
            logger.error(f"Bot startup error: {e}")
            raise
        finally:
            await self.app.stop()

def main():
    """Main function to run the bot"""
    try:
        bot = PublicAutoForwardBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    main()