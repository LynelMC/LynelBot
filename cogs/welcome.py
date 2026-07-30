import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.embeds import EmbedUtils
import datetime

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if not storage.get_setting("modules", guild.id, "welcome_enabled", False):
            return
        
        # 自動ロール
        auto_role_id = storage.get_setting("welcome", guild.id, "auto_role_id")
        if auto_role_id:
            role = guild.get_role(int(auto_role_id))
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass
        
        # Welcomeメッセージ
        channel_id = storage.get_setting("welcome", guild.id, "channel_id")
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                title = storage.get_setting("welcome", guild.id, "title", "ようこそ！")
                desc = storage.get_setting("welcome", guild.id, "description", "{user} さん、{server} へようこそ！")
                
                # プレースホルダー置換
                desc = desc.replace("{user}", member.mention).replace("{server}", guild.name)
                
                embed = EmbedUtils.create_embed(
                    title=title,
                    description=desc,
                    color=discord.Color.green(),
                    thumbnail=member.display_avatar.url,
                    timestamp=True
                )
                await channel.send(embed=embed)

    @app_commands.command(name="welcome-setup", description="Welcomeメッセージの設定")
    @is_admin()
    async def welcome_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, auto_role: discord.Role = None):
        guild_id = interaction.guild_id
        storage.set_data("modules", guild_id, "welcome_enabled", True)
        storage.set_data("welcome", guild_id, "channel_id", str(channel.id))
        if auto_role:
            storage.set_data("welcome", guild_id, "auto_role_id", str(auto_role.id))
        
        await interaction.response.send_message(f"Welcomeメッセージを {channel.mention} に設定しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
