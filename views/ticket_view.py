import discord
from storage import storage
import datetime
import io

class TicketRatingView(discord.ui.View):
    def __init__(self, callback):
        super().__init__(timeout=60)
        self.callback = callback

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary)
    async def star1(self, interaction, button): await self.callback(interaction, 1)
    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.secondary)
    async def star2(self, interaction, button): await self.callback(interaction, 2)
    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def star3(self, interaction, button): await self.callback(interaction, 3)
    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def star4(self, interaction, button): await self.callback(interaction, 4)
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def star5(self, interaction, button): await self.callback(interaction, 5)

class TicketActionView(discord.ui.View):
    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="担当", style=discord.ButtonStyle.primary, emoji="🙋", custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.mention} が担当します。", ephemeral=False)
        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="閉じる", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("チケットを閉じます。評価をお願いします。", view=TicketRatingView(self._rate_callback), ephemeral=False)
        # 実際にはここでチャンネルの権限変更などを行う

    async def _rate_callback(self, interaction, rating):
        await interaction.response.send_message(f"評価 {rating} を受け付けました。ありがとうございました！", ephemeral=True)

class PersistentTicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="チケット作成", style=discord.ButtonStyle.success, emoji="🎫", custom_id="create_ticket_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 実際にはここでチャンネル作成を行う
        await interaction.response.send_message("チケットを作成しています...", ephemeral=True)
