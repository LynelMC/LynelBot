import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    """サーバー情報を表示するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="info",
        description="サーバーの情報を表示します。"
    )
    @app_commands.guild_only()
    async def info(self, interaction: discord.Interaction):
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ このコマンドはサーバー内で使用してください。",
                ephemeral=True
            )
            return

        member_count = guild.member_count or 0
        bot_count = sum(
            1 for member in guild.members if member.bot
        )
        human_count = max(member_count - bot_count, 0)

        channel_count = len(guild.channels)
        text_count = len(guild.text_channels)
        voice_count = len(guild.voice_channels)
        role_count = max(len(guild.roles) - 1, 0)

        owner = guild.owner
        owner_text = (
            owner.mention
            if owner
            else f"<@{guild.owner_id}>"
        )

        embed = discord.Embed(
            title="🏠 サーバー情報",
            color=discord.Color.from_rgb(88, 166, 255)
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(
            name="📛 サーバー名",
            value=guild.name,
            inline=False
        )

        embed.add_field(
            name="👑 オーナー",
            value=owner_text,
            inline=True
        )

        embed.add_field(
            name="👥 メンバー",
            value=f"{member_count:,}人",
            inline=True
        )

        embed.add_field(
            name="👤 ユーザー",
            value=f"{human_count:,}人",
            inline=True
        )

        embed.add_field(
            name="🤖 Bot",
            value=f"{bot_count:,}体",
            inline=True
        )

        embed.add_field(
            name="💬 チャンネル",
            value=f"{channel_count:,}個",
            inline=True
        )

        embed.add_field(
            name="📝 テキスト",
            value=f"{text_count:,}個",
            inline=True
        )

        embed.add_field(
            name="🔊 ボイス",
            value=f"{voice_count:,}個",
            inline=True
        )

        embed.add_field(
            name="🎭 ロール",
            value=f"{role_count:,}個",
            inline=True
        )

        embed.add_field(
            name="📅 作成日",
            value=discord.utils.format_dt(
                guild.created_at,
                style="F"
            ),
            inline=False
        )

        embed.add_field(
            name="🆔 サーバーID",
            value=f"`{guild.id}`",
            inline=False
        )

        embed.set_footer(
            text=f"{guild.name} • Server Info"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
