import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from services.disaster_service import DisasterService

class DisasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = DisasterService(bot)

    @app_commands.command(name="disaster-setup", description="防災通知の設定")
    @is_admin()
    async def disaster_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, pref: str):
        guild_id = interaction.guild_id
        storage.set_data("disaster", guild_id, "channel_id", str(channel.id))
        storage.set_data("disaster", guild_id, "prefecture", pref)
        await interaction.response.send_message(f"防災通知を {channel.mention} (対象: {pref}) に設定しました。", ephemeral=True)

    @app_commands.command(name="disaster-test", description="防災通知のテスト送信")
    @is_admin()
    async def disaster_test(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        await self.service.send_disaster_alert(
            guild_id=guild_id,
            title="緊急地震速報 (テスト)",
            description="これはテスト通知です。震源地: テスト、最大震度: 5弱",
            alert_type="地震"
        )
        await interaction.response.send_message("テスト通知を送信しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DisasterCog(bot))
