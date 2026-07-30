import discord
from discord.ext import commands
import os
import asyncio

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all() # 全てのインテントを有効化
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Cogの読み込み
        cog_count = 0
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    cog_count += 1
                except Exception as e:
                    print(f"Failed to load extension {filename}: {e}")
        
        print(f"Loaded {cog_count} extensions.")
        
        # スラッシュコマンドの同期
        # await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

async def main():
    # ローカル開発用に .env ファイルがあれば読み込む (Render上では不要)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # 環境変数からトークンを取得
    # Renderのダッシュボードで 'DISCORD_BOT_TOKEN' という名前で環境変数を設定してください
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        print("エラー: 環境変数 'DISCORD_BOT_TOKEN' が設定されていません。")
        print("RenderのEnvironment設定、または .env ファイルを確認してください。")
        return

    bot = MyBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
