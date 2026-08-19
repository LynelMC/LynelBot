import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone, timedelta

import storage

WARN_DELETE_DELAY = 8  # 警告メッセージを自動削除するまでの秒数
DEFAULT_TIMEOUT_MINUTES = 10


class MentionGuard(commands.Cog):
    """権限を持たないメンバーによる @everyone / @here の使用を検知・削除・警告・タイムアウトするCog。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        # /setlogchannel で設定したチャンネルをそのまま流用する
        channel_id = storage.get_value(guild.id, "log_channel")
        if not channel_id:
            return None
        return guild.get_channel(channel_id)

    @app_commands.command(name="mentionguard", description="@everyone/@here不正使用時の対応を設定します")
    @app_commands.describe(
        state="この機能をon/offする",
        timeoutminutes="不正使用者をタイムアウトする分数(1〜40320)",
    )
    @app_commands.choices(
        state=[
            app_commands.Choice(name="on", value="on"),
            app_commands.Choice(name="off", value="off"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def mentionguard(
        self,
        interaction: discord.Interaction,
        state: app_commands.Choice[str] = None,
        timeoutminutes: app_commands.Range[int, 1, 40320] = None,
    ):
        guild_id = interaction.guild_id
        messages = []

        if state is not None:
            enabled = state.value == "on"
            storage.set_guild_value(guild_id, "mention_guard_enabled", enabled)
            messages.append(f"@everyone/@here監視を{state.value}にしました。")

        if timeoutminutes is not None:
            storage.set_guild_value(guild_id, "mention_guard_timeout_minutes", timeoutminutes)
            messages.append(f"タイムアウト時間を{timeoutminutes}分に設定しました。")

        if not messages:
            current_enabled = storage.get_value(guild_id, "mention_guard_enabled", True)
            current_minutes = storage.get_value(guild_id, "mention_guard_timeout_minutes", DEFAULT_TIMEOUT_MINUTES)
            messages.append(
                f"現在の設定: {'on' if current_enabled else 'off'} / タイムアウト{current_minutes}分"
            )

        await interaction.response.send_message("\n".join(messages), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        if not storage.get_value(message.guild.id, "mention_guard_enabled", True):
            return

        content = message.content or ""
        triggered = message.mention_everyone or "@everyone" in content or "@here" in content
        if not triggered:
            return

        member = message.author
        # Mention Everyone権限(または管理者)を持つ人は正規利用として除外
        if member.guild_permissions.mention_everyone or member.guild_permissions.administrator:
            return

        # メッセージ削除
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        # タイムアウト実行
        timeout_minutes = storage.get_value(message.guild.id, "mention_guard_timeout_minutes", DEFAULT_TIMEOUT_MINUTES)
        timed_out = False
        bot_member = message.guild.me
        if member.top_role < bot_member.top_role:
            try:
                await member.timeout(timedelta(minutes=timeout_minutes), reason="@everyone/@here不正使用")
                timed_out = True
            except discord.Forbidden:
                pass

        # 送信者への警告(チャンネルに一定時間だけ表示)
        try:
            if timed_out:
                warn_text = (
                    f"{member.mention} @everyone / @here の使用は許可されていません。"
                    f"メッセージを削除し、{timeout_minutes}分間タイムアウトしました。"
                )
            else:
                warn_text = (
                    f"{member.mention} @everyone / @here の使用は許可されていません。メッセージを削除しました。"
                )
            warn_msg = await message.channel.send(warn_text)
            await warn_msg.delete(delay=WARN_DELETE_DELAY)
        except discord.Forbidden:
            pass

        # ログチャンネルへ通知
        log_channel = await self._get_log_channel(message.guild)
        if log_channel:
            embed = discord.Embed(
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_author(name=f"{member} が@everyone/@hereを使用しました", icon_url=member.display_avatar.url)
            embed.add_field(name="チャンネル", value=message.channel.mention, inline=False)
            embed.add_field(name="内容", value=content[:1000] if content else "(内容なし)", inline=False)
            action_text = (
                f"メッセージを自動削除・{timeout_minutes}分タイムアウト済み"
                if timed_out
                else "メッセージを自動削除(タイムアウトは権限不足で失敗)"
            )
            embed.add_field(name="対応", value=action_text, inline=False)
            await log_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MentionGuard(bot))
