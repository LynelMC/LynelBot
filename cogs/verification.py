import discord
from discord import app_commands
from discord.ext import commands
from views.verification_view import VerificationSetupView, PersistentVerificationView
from utils.checks import is_admin
from storage import storage

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify-setup", description="認証パネルのセットアップ")
    @is_admin()
    async def verify_setup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="認証システム設定",
            description="認証パネルのカスタマイズを行ってください。",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=VerificationSetupView(), ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # 永続Viewの登録
        self.bot.add_view(PersistentVerificationView())
        print("Verification Cog is ready with Persistent View.")

async def setup(bot):
    await bot.add_cog(VerificationCog(bot))
