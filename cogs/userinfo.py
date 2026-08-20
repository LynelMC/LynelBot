import discord
from discord import app_commands
from discord.ext import commands


class UserInfo(commands.Cog):
    """ユーザー情報を表示するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="userinfo",
        description="ユーザーの情報を表示します。"
    )
    @app_commands.describe(
        user="情報を表示するユーザー"
    )
    @app_commands.guild_only()
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None
    ):
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ このコマンドはサーバー内で使用してください。",
                ephemeral=True
            )
            return

        target = user or interaction.user

        embed = discord.Embed(
            title="👤 ユーザー情報",
            color=discord.Color.from_rgb(88, 166, 255)
        )

        embed.set_thumbnail(
            url=target.display_avatar.url
        )

        embed.add_field(
            name="👤 ユーザー",
            value=target.mention,
            inline=True
        )

        embed.add_field(
            name="🏷️ 表示名",
            value=target.display_name,
            inline=True
        )

        embed.add_field(
            name="🤖 Bot",
            value="はい" if target.bot else "いいえ",
            inline=True
        )

        embed.add_field(
            name="🆔 ユーザーID",
            value=f"`{target.id}`",
            inline=False
        )

        embed.add_field(
            name="📅 アカウント作成日",
            value=discord.utils.format_dt(
                target.created_at,
                style="F"
            ),
            inline=False
        )

        embed.add_field(
            name="📥 サーバー参加日",
            value=discord.utils.format_dt(
                target.joined_at,
                style="F"
            ) if target.joined_at else "不明",
            inline=False
        )

        roles = [
            role.mention
            for role in target.roles
            if role != guild.default_role
        ]

        if roles:
            role_text = " ".join(roles)

            if len(role_text) > 1000:
                role_text = role_text[:997] + "..."

        else:
            role_text = "なし"

        embed.add_field(
            name="🎭 ロール",
            value=role_text,
            inline=False
        )

        embed.set_footer(
            text=f"{guild.name} • User Info"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(UserInfo(bot))
