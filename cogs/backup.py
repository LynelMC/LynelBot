import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.embeds import EmbedUtils
import json
import datetime

class BackupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="backup-create", description="サーバー設定のバックアップを作成します")
    @is_admin()
    async def backup_create(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        backup_data = {
            "name": guild.name,
            "roles": [],
            "categories": [],
            "channels": []
        }
        
        # ロール情報の取得
        for role in guild.roles:
            if not role.is_default() and not role.managed:
                backup_data["roles"].append({
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable
                })
        
        # カテゴリとチャンネル情報の取得
        for category in guild.categories:
            backup_data["categories"].append({
                "name": category.name,
                "position": category.position
            })
            
        for channel in guild.text_channels:
            backup_data["channels"].append({
                "name": channel.name,
                "category": channel.category.name if channel.category else None,
                "topic": channel.topic,
                "nsfw": channel.nsfw
            })

        storage.set_data("backup", guild.id, "last_backup", backup_data)
        await interaction.followup.send(embed=EmbedUtils.success_embed("バックアップを作成しました。"), ephemeral=True)

    @app_commands.command(name="backup-restore", description="サーバー設定を復元します (注意: ロールのみ)")
    @is_admin()
    async def backup_restore(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        backup_data = storage.get_setting("backup", guild.id, "last_backup")
        
        if not backup_data:
            return await interaction.followup.send(embed=EmbedUtils.error_embed("バックアップが見つかりません。"), ephemeral=True)
        
        # ロールの復元 (名前が一致しないものを作成)
        existing_role_names = [r.name for r in guild.roles]
        created_count = 0
        for role_info in backup_data["roles"]:
            if role_info["name"] not in existing_role_names:
                try:
                    await guild.create_role(
                        name=role_info["name"],
                        color=discord.Color(role_info["color"]),
                        permissions=discord.Permissions(role_info["permissions"]),
                        hoist=role_info["hoist"],
                        mentionable=role_info["mentionable"]
                    )
                    created_count += 1
                except:
                    pass
        
        await interaction.followup.send(embed=EmbedUtils.success_embed(f"復元が完了しました。作成されたロール: {created_count}"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(BackupCog(bot))
