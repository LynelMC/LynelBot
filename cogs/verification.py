import discord
from discord import app_commands
from discord.ext import commands

import storage

VERIFY_CUSTOM_ID = "verify:button"

DEFAULT_TITLE = "サーバー認証"
DEFAULT_DESCRIPTION = "下のボタンを押すと認証が完了し、サーバーを閲覧できるようになります。"
DEFAULT_BUTTON_LABEL = "認証する"
DEFAULT_BUTTON_EMOJI = "✅"
DEFAULT_COLOR = discord.Color.green().value


def parse_color(value: str) -> int:
    """'#00ff00' や '00ff00' 形式の文字列を discord.Color用のint値に変換する。"""
    text = value.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError("カラーコードは6桁の16進数で指定してください(例: #00ff00)")
    return int(text, 16)


def build_verify_view(label: str, emoji: str | None) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(
        discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.success,
            custom_id=VERIFY_CUSTOM_ID,
            emoji=emoji,
        )
    )
    return view


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Bot再起動後もボタンを動作させるためpersistent viewとして登録。
        # ラベル/絵文字はcustom_idマッチングには影響しないため、デフォルト表示で登録しておけばよい。
        self.bot.add_view(build_verify_view(DEFAULT_BUTTON_LABEL, DEFAULT_BUTTON_EMOJI))

    # ---- 認証ボタンが押された時の処理(生のinteractionイベントで拾う) ----
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        data = interaction.data or {}
        if data.get("custom_id") != VERIFY_CUSTOM_ID:
            return

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

    # ---- 設定コマンド群 ----
    setup_group = app_commands.Group(name="setup", description="Bot設定コマンド")

    @setup_group.command(name="verifyrole", description="認証時に付与するロールを設定します")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_verifyrole(self, interaction: discord.Interaction, role: discord.Role):
        storage.set_guild_value(interaction.guild_id, "verify_role", role.id)
        await interaction.response.send_message(
            f"認証ロールを {role.mention} に設定しました。", ephemeral=True
        )

    @setup_group.command(name="verifymessage", description="認証パネルの見た目をカスタマイズします(空欄は変更なし)")
    @app_commands.describe(
        title="パネルのタイトル",
        description="パネルの説明文",
        buttonlabel="ボタンに表示する文字",
        buttonemoji="ボタンに表示する絵文字(任意・'none'で絵文字なしにできます)",
        color="埋め込みの色をカラーコードで指定(例: #00ff00)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_verifymessage(
        self,
        interaction: discord.Interaction,
        title: str = None,
        description: str = None,
        buttonlabel: str = None,
        buttonemoji: str = None,
        color: str = None,
    ):
        guild_id = interaction.guild_id
        if title is not None:
            storage.set_guild_value(guild_id, "verify_title", title)
        if description is not None:
            storage.set_guild_value(guild_id, "verify_description", description)
        if buttonlabel is not None:
            storage.set_guild_value(guild_id, "verify_button_label", buttonlabel)
        if buttonemoji is not None:
            # 'none' / 'なし' 指定で絵文字を削除できるようにする
            if buttonemoji.strip().lower() in ("none", "なし", ""):
                storage.set_guild_value(guild_id, "verify_button_emoji", None)
            else:
                storage.set_guild_value(guild_id, "verify_button_emoji", buttonemoji)
        if color is not None:
            try:
                color_value = parse_color(color)
            except ValueError as e:
                return await interaction.response.send_message(str(e), ephemeral=True)
            storage.set_guild_value(guild_id, "verify_color", color_value)

        await interaction.response.send_message(
            "認証パネルの設定を更新しました。`/verifypanel` で反映したパネルを設置できます。",
            ephemeral=True,
        )

    @app_commands.command(name="verifypanel", description="認証パネルをこのチャンネルに設置します")
    @app_commands.checks.has_permissions(administrator=True)
    async def verifypanel(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        role_id = storage.get_value(guild_id, "verify_role")
        if not role_id:
            return await interaction.response.send_message(
                "先に `/setup verifyrole` で認証ロールを設定してください。", ephemeral=True
            )

        title = storage.get_value(guild_id, "verify_title", DEFAULT_TITLE)
        description = storage.get_value(guild_id, "verify_description", DEFAULT_DESCRIPTION)
        button_label = storage.get_value(guild_id, "verify_button_label", DEFAULT_BUTTON_LABEL)
        button_emoji = storage.get_value(guild_id, "verify_button_emoji", DEFAULT_BUTTON_EMOJI)
        color_value = storage.get_value(guild_id, "verify_color", DEFAULT_COLOR)

        embed = discord.Embed(title=title, description=description, color=discord.Color(color_value))

        try:
            view = build_verify_view(button_label, button_emoji)
        except (discord.InvalidArgument, ValueError, TypeError):
            # 絵文字の指定が不正だった場合は絵文字なしでフォールバック
            view = build_verify_view(button_label, None)

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("認証パネルを設置しました。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
