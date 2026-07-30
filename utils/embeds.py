import discord
import datetime

class EmbedUtils:
    @staticmethod
    def create_embed(title=None, description=None, color=discord.Color.blue(), thumbnail=None, image=None, footer_text=None, footer_icon=None, timestamp=False):
        embed = discord.Embed(
            title=title if title else discord.Embed.Empty,
            description=description if description else discord.Embed.Empty,
            color=color
        )
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)
        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon if footer_icon else discord.Embed.Empty)
        if timestamp:
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        return embed

    @staticmethod
    def error_embed(description):
        return discord.Embed(
            title="❌ エラー",
            description=description,
            color=discord.Color.red()
        )

    @staticmethod
    def success_embed(description):
        return discord.Embed(
            title="✅ 成功",
            description=description,
            color=discord.Color.green()
        )
