import discord
from discord import app_commands
from discord.ext import commands

import storage


class WelcomeLog(commands.Cog):
    """メンバーの参加・退出ログを管理するCog。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="welcomelog",
        description="メンバーの参加・退出ログを設定します",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        channel="参加・退出ログを送信するチャンネル",
    )
    async def welcomelog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        storage.set_guild_value(
            interaction.guild_id,
            "welcome_log_channel",
            channel.id,
        )

        await interaction.response.send_message(
            f"✅ 入退出ログの送信先を {channel.mention} に設定しました。",
            ephemeral=True,
        )

    def _get_channel(
        self,
        guild: discord.Guild,
    ) -> discord.TextChannel | None:
        channel_id = storage.get_value(
            guild.id,
            "welcome_log_channel",
        )

        if not channel_id:
            return None

        channel = guild.get_channel(channel_id)

        if isinstance(channel, discord.TextChannel):
            return channel

        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self._get_channel(member.guild)

        if channel is None:
            return

        embed = discord.Embed(
            title="👋 メンバーが参加しました",
            color=discord.Color.green(),
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👤 ユーザー",
            value=member.mention,
            inline=False,
        )

        embed.add_field(
            name="🆔 ユーザーID",
            value=str(member.id),
            inline=False,
        )

        embed.add_field(
            name="📅 アカウント作成日",
            value=discord.utils.format_dt(
                member.created_at,
                "F",
            ),
            inline=False,
        )

        embed.add_field(
            name="👥 現在のメンバー数",
            value=f"{member.guild.member_count}人",
            inline=False,
        )

        embed.set_footer(
            text=f"{member.guild.name} • Welcome Log",
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self._get_channel(member.guild)

        if channel is None:
            return

        embed = discord.Embed(
            title="🚪 メンバーが退出しました",
            color=discord.Color.red(),
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👤 ユーザー",
            value=f"{member} ({member.mention})",
            inline=False,
        )

        embed.add_field(
            name="🆔 ユーザーID",
            value=str(member.id),
            inline=False,
        )

        embed.add_field(
            name="📅 アカウント作成日",
            value=discord.utils.format_dt(
                member.created_at,
                "F",
            ),
            inline=False,
        )

        embed.add_field(
            name="👥 現在のメンバー数",
            value=f"{member.guild.member_count}人",
            inline=False,
        )

        embed.set_footer(
            text=f"{member.guild.name} • Welcome Log",
        )

        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeLog(bot))
