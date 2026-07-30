import discord
from discord.ext import commands
from discord import app_commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Botの応答速度を確認します。")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🌐 Ping!",
            description=f"現在のPing: **{latency}ms**",
            color=discord.Color.green()
        )

        if latency < 100:
            embed.add_field(name="状態", value="🟢 とても快適")
        elif latency < 200:
            embed.add_field(name="状態", value="🟡 普通")
        else:
            embed.add_field(name="状態", value="🔴 少し遅い")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
