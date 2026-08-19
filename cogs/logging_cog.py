import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone

import storage


class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel_id = storage.get_value(guild.id, "log_channel")
        if not channel_id:
            return None
        return guild.get_channel(channel_id)

    def _base_embed(self, color: discord.Color) -> discord.Embed:
        embed = discord.Embed(color=color, timestamp=datetime.now(timezone.utc))
        return embed

    @app_commands.command(name="setlogchannel", description="サーバーログを送るチャンネルを設定します")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        storage.set_guild_value(interaction.guild_id, "log_channel", channel.id)
        await interaction.response.send_message(f"ログチャンネルを {channel.mention} に設定しました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch = await self._get_log_channel(member.guild)
        if not ch:
            return
        embed = self._base_embed(discord.Color.green())
        embed.set_author(name=f"{member} が参加しました", icon_url=member.display_avatar.url)
        embed.add_field(name="ユーザーID", value=str(member.id))
        embed.add_field(name="アカウント作成日", value=discord.utils.format_dt(member.created_at, "R"))
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        ch = await self._get_log_channel(member.guild)
        if not ch:
            return
        embed = self._base_embed(discord.Color.red())
        embed.set_author(name=f"{member} が退出しました", icon_url=member.display_avatar.url)
        embed.add_field(name="ユーザーID", value=str(member.id))
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        if roles:
            embed.add_field(name="所持していたロール", value=", ".join(roles), inline=False)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        ch = await self._get_log_channel(guild)
        if not ch:
            return
        embed = self._base_embed(discord.Color.dark_red())
        embed.set_author(name=f"{user} がBANされました", icon_url=user.display_avatar.url)
        embed.add_field(name="ユーザーID", value=str(user.id))
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        ch = await self._get_log_channel(guild)
        if not ch:
            return
        embed = self._base_embed(discord.Color.orange())
        embed.set_author(name=f"{user} のBANが解除されました", icon_url=user.display_avatar.url)
        embed.add_field(name="ユーザーID", value=str(user.id))
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            return
        ch = await self._get_log_channel(after.guild)
        if not ch:
            return
        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]
        if not added and not removed:
            return
        embed = self._base_embed(discord.Color.blue())
        embed.set_author(name=f"{after} のロールが変更されました", icon_url=after.display_avatar.url)
        if added:
            embed.add_field(name="追加", value=", ".join(r.mention for r in added), inline=False)
        if removed:
            embed.add_field(name="削除", value=", ".join(r.mention for r in removed), inline=False)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        ch = await self._get_log_channel(message.guild)
        if not ch:
            return
        embed = self._base_embed(discord.Color.greyple())
        embed.set_author(name=f"{message.author} のメッセージが削除されました", icon_url=message.author.display_avatar.url)
        embed.add_field(name="チャンネル", value=message.channel.mention, inline=False)
        content = message.content if message.content else "(内容なし・埋め込みや添付ファイルの可能性)"
        embed.add_field(name="内容", value=content[:1000], inline=False)
        await ch.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingCog(bot))
