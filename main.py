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
        
        # 起動時のグローバル同期
        try:
            await self.tree.sync()
            print("Global slash commands synced.")
        except Exception as e:
            print(f"Failed to sync global commands: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        
        # ステータスを「メンテナンス中」に設定
        # ActivityType.playing を使用して「メンテナンス中 をプレイ中」と表示させます
        activity = discord.Activity(name="メンテナンス中", type=discord.ActivityType.playing)
        await self.change_presence(status=discord.Status.dnd, activity=activity)
        print("Status set to: Maintenance Mode (DND)")

    # 管理者用の手動同期コマンド (prefix: !)
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx, scope: str = None):
        async with ctx.typing():
            try:
                if scope == "guild":
                    self.tree.copy_global_to(guild=ctx.guild)
                    synced = await self.tree.sync(guild=ctx.guild)
                    await ctx.send(f"このサーバーに {len(synced)} 個のコマンドを即時同期しました。")
                else:
                    synced = await self.tree.sync()
                    await ctx.send(f"グローバルに {len(synced)} 個のコマンドを同期しました。反映まで時間がかかる場合があります。")
            except Exception as e:
                await ctx.send(f"同期中にエラーが発生しました: {e}")

async def main():
    # ローカル開発用に .env ファイルがあれば読み込む
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Flaskサーバーを起動 (Renderの生存確認用)
    from utils.keep_alive import keep_alive
    keep_alive()
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        print("エラー: 環境変数 'DISCORD_BOT_TOKEN' が設定されていません。")
        return

    bot = MyBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
