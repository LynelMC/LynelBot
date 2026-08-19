import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta, datetime, timezone

import storage


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel_id = storage.get_value(guild.id, "log_channel")
        if not channel_id:
            return None
        return guild.get_channel(channel_id)

    @app_commands.command(name="timeout", description="メンバーを一定時間タイムアウトします")
    @app_commands.describe(
        member="タイムアウトさせる相手",
        minutes="タイムアウトする分数(例: 10)",
        reason="理由(任意)",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],  # Discord上限は28日=40320分
        reason: str = "理由なし",
    ):
        if member.guild_permissions.administrator:
            return await interaction.response.send_message(
                "管理者権限を持つメンバーはタイムアウトできません。", ephemeral=True
            )

        bot_member = interaction.guild.me
        if member.top_role >= bot_member.top_role:
            return await interaction.response.send_message(
                "対象のロールがBotより上位のためタイムアウトできません。", ephemeral=True
            )

        duration = timedelta(minutes=minutes)
        try:
            await member.timeout(duration, reason=f"{interaction.user}: {reason}")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "権限不足でタイムアウトできませんでした。", ephemeral=True
            )

        await interaction.response.send_message(
            f"{member.mention} を{minutes}分間タイムアウトしました。理由: {reason}", ephemeral=True
        )

        log_channel = await self._get_log_channel(interaction.guild)
        if log_channel:
            embed = discord.Embed(color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
            embed.set_author(name=f"{member} がタイムアウトされました", icon_url=member.display_avatar.url)
            embed.add_field(name="実行者", value=interaction.user.mention, inline=True)
            embed.add_field(name="時間", value=f"{minutes}分", inline=True)
            embed.add_field(name="理由", value=reason, inline=False)
            await log_channel.send(embed=embed)

    @app_commands.command(name="untimeout", description="メンバーのタイムアウトを解除します")
    @app_commands.describe(member="解除する相手", reason="理由(任意)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member, reason: str = "理由なし"):
        try:
            await member.timeout(None, reason=f"{interaction.user}: {reason}")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "権限不足で解除できませんでした。", ephemeral=True
            )

        await interaction.response.send_message(f"{member.mention} のタイムアウトを解除しました。", ephemeral=True)

        log_channel = await self._get_log_channel(interaction.guild)
        if log_channel:
            embed = discord.Embed(color=discord.Color.green(), timestamp=datetime.now(timezone.utc))
            embed.set_author(name=f"{member} のタイムアウトが解除されました", icon_url=member.display_avatar.url)
            embed.add_field(name="実行者", value=interaction.user.mention, inline=True)
            embed.add_field(name="理由", value=reason, inline=False)
            await log_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
