import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.embeds import EmbedUtils
from utils.logger import Logger
import re
import datetime

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_pattern = re.compile(r'https?://\S+')
        # フィッシングURLの簡易リスト (本来は外部APIやDBを使用)
        self.phishing_domains = ["discord-gift.com", "discord-nitro.com", "dlscord.com"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        guild_id = message.guild.id
        
        # 招待リンク対策
        if storage.get_setting("security", guild_id, "anti_invite", False):
            if "discord.gg/" in message.content:
                if not message.author.guild_permissions.manage_messages:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} 招待リンクの送信は禁止されています。", delete_after=5)
                    return

        # フィッシングURL検知
        if storage.get_setting("security", guild_id, "anti_phishing", False):
            urls = self.url_pattern.findall(message.content)
            for url in urls:
                for domain in self.phishing_domains:
                    if domain in url:
                        await message.delete()
                        await message.guild.ban(message.author, reason="フィッシングURLの送信")
                        await Logger.log_action(self.bot, guild_id, "フィッシング検知", f"{message.author.mention} がフィッシングURLを送信したためBANしました。", color=discord.Color.red())
                        return

        # NGワード対策
        ng_words = storage.get_setting("security", guild_id, "ng_words", [])
        for word in ng_words:
            if word in message.content:
                await message.delete()
                await message.channel.send(f"{message.author.mention} 不適切な言葉が含まれています。", delete_after=5)
                return

    @app_commands.command(name="security-setup", description="セキュリティ機能の設定")
    @is_admin()
    async def security_setup(self, interaction: discord.Interaction, anti_invite: bool = None, anti_phishing: bool = None):
        guild_id = interaction.guild_id
        if anti_invite is not None:
            storage.set_data("security", guild_id, "anti_invite", anti_invite)
        if anti_phishing is not None:
            storage.set_data("security", guild_id, "anti_phishing", anti_phishing)
        
        await interaction.response.send_message("セキュリティ設定を更新しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
