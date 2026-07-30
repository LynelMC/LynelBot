import discord
from storage import storage

class ModuleToggleButton(discord.ui.Button):
    def __init__(self, module_name, guild_id):
        self.module_name = module_name
        self.guild_id = guild_id
        self.module_key = f"{module_name.lower()}_enabled"
        current_status = storage.get_setting("modules", guild_id, self.module_key, False)
        
        label = f"{module_name}: {'ON' if current_status else 'OFF'}"
        style = discord.ButtonStyle.success if current_status else discord.ButtonStyle.danger
        super().__init__(label=label, style=style, custom_id=f"mod_toggle_{module_name}")

    async def callback(self, interaction: discord.Interaction):
        current_status = storage.get_setting("modules", self.guild_id, self.module_key, False)
        new_status = not current_status
        storage.set_data("modules", self.guild_id, self.module_key, new_status)
        
        self.label = f"{self.module_name}: {'ON' if new_status else 'OFF'}"
        self.style = discord.ButtonStyle.success if new_status else discord.ButtonStyle.danger
        await interaction.response.edit_message(view=self.view)

class ModulesView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=300)
        modules = [
            "Verification", "RolePanel", "Welcome", "Logging", 
            "Embed", "Moderation", "AntiSpam", "BotGuard", 
            "Ticket", "Disaster", "Security", "Backup"
        ]
        for mod in modules:
            self.add_item(ModuleToggleButton(mod, guild_id))
