import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from services.botguard_service import BotGuardService

class BotGuardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = BotGuardService(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.bot:
            return
        
        guild = member.guild
        if not storage.get_setting("modules", guild.id, "botguard_enabled", False):
            return
        
        await self.service.log_bot_join(member)

    @app_commands.command(name="botguard-setup", description="BotGuardの設定")
    @is_admin()
    async def botguard_setup(self, interaction: discord.Interaction, notify: bool):
        storage.set_data("modules", interaction.guild_id, "botguard_enabled", notify)
        await interaction.response.send_message(f"BotGuardを {'有効' if notify else '無効'} にしました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BotGuardCog(bot))
