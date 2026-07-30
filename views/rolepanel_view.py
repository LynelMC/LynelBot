import discord
from storage import storage

class RolePanelButton(discord.ui.Button):
    def __init__(self, role_id, label, emoji=None, style=discord.ButtonStyle.secondary):
        super().__init__(label=label, emoji=emoji, style=style, custom_id=f"role_btn_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(self.role_id))
        if not role:
            return await interaction.response.send_message("ロールが見つかりません。", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role.name} を削除しました。", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role.name} を付与しました。", ephemeral=True)

class RolePanelSelect(discord.ui.Select):
    def __init__(self, guild_id, options):
        super().__init__(placeholder="ロールを選択してください...", options=options, custom_id=f"role_sel_{guild_id}")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("ロールが見つかりません。", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role.name} を削除しました。", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role.name} を付与しました。", ephemeral=True)

class PersistentRolePanelView(discord.ui.View):
    def __init__(self, guild_id, mode="button"):
        super().__init__(timeout=None)
        roles = storage.get_setting("rolepanel", guild_id, "roles", [])
        
        if mode == "button":
            for r in roles:
                self.add_item(RolePanelButton(r["id"], r["label"], r.get("emoji")))
        else:
            options = [discord.SelectOption(label=r["label"], value=str(r["id"]), emoji=r.get("emoji")) for r in roles]
            if options:
                self.add_item(RolePanelSelect(guild_id, options))
