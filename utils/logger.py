import discord
import datetime
from storage import storage
from utils.embeds import EmbedUtils

class Logger:
    @staticmethod
    async def send_log(bot, guild_id, embed):
        log_channel_id = storage.get_setting("logging", guild_id, "log_channel_id")
        if not log_channel_id:
            return
        
        channel = bot.get_channel(int(log_channel_id))
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass

    @staticmethod
    async def log_action(bot, guild_id, title, description, color=discord.Color.blue(), fields=None):
        embed = EmbedUtils.create_embed(
            title=title,
            description=description,
            color=color,
            timestamp=True
        )
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        await Logger.send_log(bot, guild_id, embed)
