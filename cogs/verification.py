import discord
from discord import app_commands
from discord.ext import commands

import storage

VERIFY_CUSTOM_ID = "verify:button"


class VerifyView(discord.ui.View):
    """認証ボタンのView。persistentにするためtimeout=Noneかつcustom_id固定。"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="認証する",
        style=discord.ButtonStyle.success,
        custom_id=VERIFY_CUSTOM_ID,
        emoji="✅",
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("サーバー内で使ってください。", ephemeral=True)

        role_id = storage.get_value(guild.id, "verify_role")
        if not role_id:
            return await interaction.response.send_message(
                "認証ロールが設定されていません。管理者に `/setup verifyrole` を実行してもらってください。",
                ephemeral=True,
            )

        role = guild.get_role(role_id)
        if role is None:
            return await interaction.response.send_message(
                "設定されている認証ロールが見つかりません。管理者に再設定を依頼してください。",
                ephemeral=True,
            )

        member = interaction.user
        if role in member.roles:
            return await interaction.response.send_message("すでに認証済みです。", ephemeral=True)

        try:
            await member.add_roles(role, reason="ボタン認証")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "権限不足でロールを付与できませんでした。Botのロール順位を確認してください。",
                ephemeral=True,
            )

        await interaction.response.send_message("認証が完了しました！ようこそ。", ephemeral=True)


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Bot再起動後もボタンを動作させるためpersistent viewとして登録
        self.bot.add_view(VerifyView())

    setup_group = app_commands.Group(name="setup", description="Bot設定コマンド")

    @setup_group.command(name="verifyrole", description="認証時に付与するロールを設定します")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_verifyrole(self, interaction: discord.Interaction, role: discord.Role):
        storage.set_guild_value(interaction.guild_id, "verify_role", role.id)
        await interaction.response.send_message(
            f"認証ロールを {role.mention} に設定しました。", ephemeral=True
        )

    @app_commands.command(name="verifypanel", description="認証パネルをこのチャンネルに設置します")
    @app_commands.checks.has_permissions(administrator=True)
    async def verifypanel(self, interaction: discord.Interaction):
        role_id = storage.get_value(interaction.guild_id, "verify_role")
        if not role_id:
            return await interaction.response.send_message(
                "先に `/setup verifyrole` で認証ロールを設定してください。", ephemeral=True
            )

        embed = discord.Embed(
            title="サーバー認証",
            description="下のボタンを押すと認証が完了し、サーバーを閲覧できるようになります。",
            color=discord.Color.green(),
        )
        await interaction.channel.send(embed=embed, view=VerifyView())
        await interaction.response.send_message("認証パネルを設置しました。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
