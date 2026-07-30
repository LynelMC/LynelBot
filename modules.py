import discord
from discord import app_commands
from discord.ext import commands
from views.modules_view import ModulesView
from utils.checks import is_admin
from storage import storage
from utils.embeds import EmbedUtils

class ModulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="modules", description="モジュール管理パネルの表示")
    @is_admin()
    async def modules(self, interaction: discord.Interaction):
        embed = EmbedUtils.create_embed(
            title="モジュール管理",
            description="各機能の有効/無効を切り替えることができます。",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=ModulesView(interaction.guild_id), ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModulesCog(bot))
