import discord
from storage import storage
from utils.logger import Logger
from utils.embeds import EmbedUtils
import datetime

class BotGuardService:
    def __init__(self, bot):
        self.bot = bot

    async def log_bot_join(self, member: discord.Member):
        guild = member.guild
        
        embed = EmbedUtils.create_embed(
            title="🤖 新規Bot参加",
            description=f"新しいBot {member.mention} ({member.id}) がサーバーに参加しました。",
            color=discord.Color.orange(),
            timestamp=True
        )
        await Logger.send_log(self.bot, guild.id, embed)
        
        # 履歴の保存
        logs = storage.get_setting("botguard", guild.id, "bot_logs", [])
        logs.append({
            "id": str(member.id),
            "name": str(member),
            "joined_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        storage.set_data("botguard", guild.id, "bot_logs", logs)

    async def check_bot_spam(self, message: discord.Message):
        # ここに詳細なBotスパム検知ロジックを実装
        pass
