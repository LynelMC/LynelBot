import discord
from utils.embeds import EmbedUtils

class ModerationReasonModal(discord.ui.Modal, title="モデレーション理由"):
    reason = discord.ui.TextInput(label="理由", style=discord.TextStyle.paragraph, placeholder="理由を入力してください...", required=True, max_length=500)
    dm_notify = discord.ui.TextInput(label="DM通知 (はい/いいえ)", placeholder="はい", required=False, max_length=10)

    def __init__(self, action_type, target, callback):
        super().__init__()
        self.action_type = action_type
        self.target = target
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        send_dm = self.dm_notify.value.lower() != "いいえ"
        await self.callback(interaction, self.target, self.reason.value, send_dm)

class PunishmentConfirmView(discord.ui.View):
    def __init__(self, action_type, target, reason, send_dm, callback):
        super().__init__(timeout=60)
        self.action_type = action_type
        self.target = target
        self.reason = reason
        self.send_dm = send_dm
        self.callback = callback

    @discord.ui.button(label="確定", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.callback(interaction, self.target, self.reason, self.send_dm)
        self.stop()

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("操作をキャンセルしました。", ephemeral=True)
        self.stop()
