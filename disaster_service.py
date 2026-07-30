import discord
from storage import storage
from utils.embeds import EmbedUtils
import datetime

class DisasterService:
    def __init__(self, bot):
        self.bot = bot

    async def send_disaster_alert(self, guild_id: int, title: str, description: str, alert_type: str):
        channel_id = storage.get_setting("disaster", guild_id, "channel_id")
        if not channel_id:
            return
            
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return

        # 災害種類に応じた色の設定
        color = discord.Color.red() if "緊急" in title or "警報" in title else discord.Color.orange()
        
        embed = EmbedUtils.create_embed(
            title=f"【{alert_type}】{title}",
            description=description,
            color=color,
            timestamp=True
        )
        
        mention = "@everyone" if storage.get_setting("disaster", guild_id, "mention_everyone", False) else ""
        
        try:
            await channel.send(content=mention, embed=embed)
        except:
            pass
