import discord
from discord import app_commands

def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("このコマンドを実行するには管理者権限が必要です。", ephemeral=True)
        return False
    return app_commands.check(predicate)

def has_mod_perms():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.moderate_members:
            return True
        await interaction.response.send_message("このコマンドを実行するにはモデレーター権限が必要です。", ephemeral=True)
        return False
    return app_commands.check(predicate)
