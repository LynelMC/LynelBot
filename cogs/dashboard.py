import discord
from discord import app_commands
from discord.ext import commands
from views.dashboard_view import DashboardView
from utils.checks import is_admin
from storage import storage
from utils.embeds import EmbedUtils


class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="dashboard",
        description="サーバーダッシュボードの表示"
    )
    @is_admin()
    async def dashboard(self, interaction: discord.Interaction):
        # 先に応答を予約（3秒制限対策）
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        embed = EmbedUtils.create_embed(
            title=f"{guild.name} ダッシュボード",
            color=discord.Color.purple(),
            timestamp=True
        )

        # メンバー統計
        bot_count = len([m for m in guild.members if m.bot])
        user_count = guild.member_count - bot_count

        embed.add_field(
            name="メンバー統計",
            value=(
                f"総数: {guild.member_count}\n"
                f"ユーザー: {user_count}\n"
                f"Bot: {bot_count}"
            ),
            inline=True
        )

        # チケット統計
        ticket_data = storage.get_data("ticket").get(str(guild.id), {})
        ticket_count = ticket_data.get("ticket_count", 0)

        embed.add_field(
            name="チケット統計",
            value=f"総発行数: {ticket_count}",
            inline=True
        )

        # モジュール状態
        mod_data = storage.get_data("modules").get(str(guild.id), {})
        enabled_mods = [
            k.replace("_enabled", "").capitalize()
            for k, v in mod_data.items()
            if v
        ]

        embed.add_field(
            name="有効なモジュール",
            value=", ".join(enabled_mods) if enabled_mods else "なし",
            inline=False
        )

        # Dashboard表示
        await interaction.followup.send(
            embed=embed,
            view=DashboardView(guild.id),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(DashboardCog(bot))
