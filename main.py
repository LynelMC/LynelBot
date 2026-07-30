import discord
from discord.ext import commands
import os
import asyncio

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    print(f"Failed to load extension {filename}: {e}")

        print("All extensions loaded.")

    async def on_ready(self):
        # ステータス設定
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="正常稼働中")
        )

        print("=" * 50)
        print(f"Logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")
        print("ステータス: 正常稼働中")
        print("=" * 50)

async def main():
    # ローカル開発用に .env を読み込む
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Renderの生存確認用
    from utils.keep_alive import keep_alive
    keep_alive()

    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found.")
        return

    bot = MyBot()

    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
