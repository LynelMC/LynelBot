import discord
from discord.ext import commands
import os
import asyncio
import threading
from flask import Flask

# -----------------------------
# Flask (Render Web Service用)
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Discord Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# -----------------------------
# Discord Bot
# -----------------------------
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        print("=== setup_hook 開始 ===")

        cog_count = 0

        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and not filename.startswith("__"):
                    try:
                        print(f"Loading {filename}")
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        print(f"Loaded {filename}")
                        cog_count += 1
                    except Exception as e:
                        print(f"Failed to load {filename}")
                        print(e)

        print(f"Loaded {cog_count} extensions.")

        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            print("Slash command sync failed:")
            print(e)

    async def on_ready(self):
        print("----------------------------")
        print(f"Logged in as {self.user}")
        print(f"ID: {self.user.id}")
        print("----------------------------")


async def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    token = os.getenv("DISCORD_BOT_TOKEN")

    if not token:
        print("DISCORD_BOT_TOKEN が設定されていません。")
        return

    # Webサーバー起動
    threading.Thread(target=run_web, daemon=True).start()

    bot = MyBot()

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
