import discord
from storage import storage
from utils.embeds import EmbedUtils

class VerificationButton(discord.ui.Button):
    def __init__(self, label="認証", emoji=None, style=discord.ButtonStyle.success):
        super().__init__(label=label, emoji=emoji, style=style, custom_id="persistent_verify_button")

    async def callback(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        role_id = storage.get_setting("verification", guild_id, "verify_role_id")
        
        if not role_id:
            return await interaction.response.send_message("認証ロールが設定されていません。", ephemeral=True)
        
        role = interaction.guild.get_role(int(role_id))
        if not role:
            return await interaction.response.send_message("設定されたロールが見つかりません。", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("既に認証されています。", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"{role.name} を付与しました。認証完了です！", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("権限不足によりロールを付与できませんでした。", ephemeral=True)

class PersistentVerificationView(discord.ui.View):
    def __init__(self, label="認証", emoji=None):
        super().__init__(timeout=None)
        self.add_item(VerificationButton(label=label, emoji=emoji))

class VerificationTextModal(discord.ui.Modal, title="認証パネル設定"):
    title_input = discord.ui.TextInput(label="タイトル", placeholder="サーバー認証", required=True)
    desc_input = discord.ui.TextInput(label="説明文", style=discord.TextStyle.paragraph, placeholder="下のボタンを押して認証してください。", required=True)
    button_label = discord.ui.TextInput(label="ボタン名", placeholder="認証する", required=True)
    button_emoji = discord.ui.TextInput(label="絵文字 (任意)", placeholder="✅", required=False)

    def __init__(self, current_data):
        super().__init__()
        self.title_input.default = current_data.get("title", "サーバー認証")
        self.desc_input.default = current_data.get("desc", "下のボタンを押して認証してください。")
        self.button_label.default = current_data.get("button_label", "認証する")
        self.button_emoji.default = current_data.get("button_emoji", "✅")

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        storage.set_data("verification", guild_id, "verify_title", self.title_input.value)
        storage.set_data("verification", guild_id, "verify_desc", self.desc_input.value)
        storage.set_data("verification", guild_id, "verify_button_label", self.button_label.value)
        storage.set_data("verification", guild_id, "verify_button_emoji", self.button_emoji.value)
        await interaction.response.send_message("設定を保存しました。", ephemeral=True)

class VerificationSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @discord.ui.button(label="テキスト設定", style=discord.ButtonStyle.primary)
    async def setup_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        current_data = {
            "title": storage.get_setting("verification", guild_id, "verify_title"),
            "desc": storage.get_setting("verification", guild_id, "verify_desc"),
            "button_label": storage.get_setting("verification", guild_id, "verify_button_label"),
            "button_emoji": storage.get_setting("verification", guild_id, "verify_button_emoji")
        }
        await interaction.response.send_modal(VerificationTextModal(current_data))

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="認証ロールを選択")
    async def setup_role(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        role = select.values[0]
        storage.set_data("verification", interaction.guild_id, "verify_role_id", str(role.id))
        await interaction.response.send_message(f"ロールを {role.mention} に設定しました。", ephemeral=True)

    @discord.ui.button(label="パネル送信", style=discord.ButtonStyle.success)
    async def send_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        title = storage.get_setting("verification", guild_id, "verify_title", "サーバー認証")
        desc = storage.get_setting("verification", guild_id, "verify_desc", "下のボタンを押して認証してください。")
        label = storage.get_setting("verification", guild_id, "verify_button_label", "認証する")
        emoji = storage.get_setting("verification", guild_id, "verify_button_emoji", "✅")
        
        embed = EmbedUtils.create_embed(title=title, description=desc, color=discord.Color.green())
        view = PersistentVerificationView(label=label, emoji=emoji)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("認証パネルを送信しました。", ephemeral=True)
