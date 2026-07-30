import discord
from discord import app_commands
from discord.ext import commands
from views.rolepanel_view import PersistentRolePanelView
from utils.checks import is_admin
from storage import storage
from utils.embeds import EmbedUtils

class RolePanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rolepanel-add", description="ロールパネルにロールを追加します")
    @is_admin()
    async def rolepanel_add(self, interaction: discord.Interaction, role: discord.Role, label: str, emoji: str = None):
        guild_id = interaction.guild_id
        roles = storage.get_setting("rolepanel", guild_id, "roles", [])
        roles.append({"id": str(role.id), "label": label, "emoji": emoji})
        storage.set_data("rolepanel", guild_id, "roles", roles)
        await interaction.response.send_message(f"ロール {role.name} を追加しました。", ephemeral=True)

    @app_commands.command(name="rolepanel-send", description="ロールパネルを送信します")
    @is_admin()
    async def rolepanel_send(self, interaction: discord.Interaction, mode: str = "button"):
        guild_id = interaction.guild_id
        embed = EmbedUtils.create_embed(
            title="ロールパネル",
            description="下のボタンまたはメニューからロールを受け取ってください。",
            color=discord.Color.blue()
        )
        view = PersistentRolePanelView(guild_id, mode=mode)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("パネルを送信しました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # 起動時にすべてのサーバーのViewを登録
        data = storage.get_data("rolepanel")
        for guild_id in data:
            self.bot.add_view(PersistentRolePanelView(int(guild_id), mode="button"))
            self.bot.add_view(PersistentRolePanelView(int(guild_id), mode="select"))
        print("RolePanel Cog is ready.")

async def setup(bot):
    await bot.add_cog(RolePanelCog(bot))
