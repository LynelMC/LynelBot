import discord
from discord import app_commands
from discord.ext import commands
from views.moderation_view import ModerationReasonModal, PunishmentConfirmView
from utils.checks import has_mod_perms
from utils.embeds import EmbedUtils
from services.moderation_service import ModerationService
import datetime

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = ModerationService(bot)

    @app_commands.command(name="ban", description="メンバーをBANします")
    @has_mod_perms()
    async def ban(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_modal(ModerationReasonModal("BAN", user, self._confirm_ban))

    async def _confirm_ban(self, interaction: discord.Interaction, user: discord.User, reason: str, send_dm: bool):
        embed = EmbedUtils.create_embed(
            title="BANの確認",
            description=f"以下の内容で {user.mention} をBANしますか？",
            color=discord.Color.orange()
        )
        embed.add_field(name="対象", value=f"{user} ({user.id})")
        embed.add_field(name="理由", value=reason)
        embed.add_field(name="DM通知", value="はい" if send_dm else "いいえ")
        
        await interaction.followup.send(embed=embed, view=PunishmentConfirmView("BAN", user, reason, send_dm, self._execute_ban), ephemeral=True)

    async def _execute_ban(self, interaction: discord.Interaction, user: discord.User, reason: str, send_dm: bool):
        try:
            await self.service.ban_member(interaction.guild, user, interaction.user, reason, send_dm)
            await interaction.followup.send(embed=EmbedUtils.success_embed(f"{user.mention} をBANしました。"), ephemeral=True)
        except Exception as e:
            await interaction.followup.send(embed=EmbedUtils.error_embed(f"BANに失敗しました: {e}"), ephemeral=True)

    @app_commands.command(name="timeout", description="メンバーをタイムアウトします")
    @has_mod_perms()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "理由なし"):
        try:
            await self.service.timeout_member(interaction.guild, member, interaction.user, duration, reason)
            await interaction.response.send_message(embed=EmbedUtils.success_embed(f"{member.mention} を {duration}分間タイムアウトしました。"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=EmbedUtils.error_embed(f"タイムアウトに失敗しました: {e}"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
