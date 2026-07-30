import discord
from storage import storage
from utils.embeds import EmbedUtils

class DashboardView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @discord.ui.button(label="更新", style=discord.ButtonStyle.primary, emoji="🔄")
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 実際にはここで最新の統計を再計算してメッセージを編集する
        await interaction.response.send_message("データを更新しました。", ephemeral=True)
