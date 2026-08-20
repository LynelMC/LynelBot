import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone

import storage


class LoggingCog(commands.Cog):
    """サーバーの管理ログを管理するCog。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(
        self,
        guild: discord.Guild,
    ) -> discord.TextChannel | None:
        channel_id = storage.get_value(guild.id, "log_channel")

        if not channel_id:
            return None

        channel = guild.get_channel(channel_id)

        if isinstance(channel, discord.TextChannel):
            return channel

        return None

    def _base_embed(self, color: discord.Color) -> discord.Embed:
        return discord.Embed(
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

    @app_commands.command(
        name="setlogchannel",
        description="サーバーの管理ログを送るチャンネルを設定します",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        channel="管理ログを送信するチャンネル",
    )
    async def setlogchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        storage.set_guild_value(
            interaction.guild_id,
            "log_channel",
            channel.id,
        )

        await interaction.response.send_message(
            f"✅ 管理ログの送信先を {channel.mention} に設定しました。",
            ephemeral=True,
        )

    # ------------------------------
    # BANログ
    # ------------------------------

    @commands.Cog.listener()
    async def on_member_ban(
        self,
        guild: discord.Guild,
        user: discord.User,
    ):
        channel = await self._get_log_channel(guild)

        if channel is None:
            return

        embed = self._base_embed(
            discord.Color.dark_red(),
        )

        embed.set_author(
            name=f"{user} がBANされました",
            icon_url=user.display_avatar.url,
        )

        embed.add_field(
            name="🆔 ユーザーID",
            value=str(user.id),
            inline=False,
        )

        await channel.send(embed=embed)

    # ------------------------------
    # BAN解除ログ
    # ------------------------------

    @commands.Cog.listener()
    async def on_member_unban(
        self,
        guild: discord.Guild,
        user: discord.User,
    ):
        channel = await self._get_log_channel(guild)

        if channel is None:
            return

        embed = self._base_embed(
            discord.Color.orange(),
        )

        embed.set_author(
            name=f"{user} のBANが解除されました",
            icon_url=user.display_avatar.url,
        )

        embed.add_field(
            name="🆔 ユーザーID",
            value=str(user.id),
            inline=False,
        )

        await channel.send(embed=embed)

    # ------------------------------
    # ロール変更ログ
    # ------------------------------

    @commands.Cog.listener()
    async def on_member_update(
        self,
        before: discord.Member,
        after: discord.Member,
    ):
        if before.roles == after.roles:
            return

        channel = await self._get_log_channel(after.guild)

        if channel is None:
            return

        added = [
            role
            for role in after.roles
            if role not in before.roles
        ]

        removed = [
            role
            for role in before.roles
            if role not in after.roles
        ]

        if not added and not removed:
            return

        embed = self._base_embed(
            discord.Color.blue(),
        )

        embed.set_author(
            name=f"{after} のロールが変更されました",
            icon_url=after.display_avatar.url,
        )

        if added:
            embed.add_field(
                name="➕ 追加",
                value=", ".join(
                    role.mention for role in added
                ),
                inline=False,
            )

        if removed:
            embed.add_field(
                name="➖ 削除",
                value=", ".join(
                    role.mention for role in removed
                ),
                inline=False,
            )

        await channel.send(embed=embed)

    # ------------------------------
    # メッセージ削除ログ
    # ------------------------------

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message: discord.Message,
    ):
        if message.author.bot:
            return

        if message.guild is None:
            return

        channel = await self._get_log_channel(
            message.guild,
        )

        if channel is None:
            return

        embed = self._base_embed(
            discord.Color.greyple(),
        )

        embed.set_author(
            name=f"{message.author} のメッセージが削除されました",
            icon_url=message.author.display_avatar.url,
        )

        embed.add_field(
            name="📢 チャンネル",
            value=message.channel.mention,
            inline=False,
        )

        content = (
            message.content
            if message.content
            else "(内容なし・埋め込みや添付ファイルの可能性)"
        )

        embed.add_field(
            name="💬 内容",
            value=content[:1000],
            inline=False,
        )

        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingCog(bot))
