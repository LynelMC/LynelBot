import discord
from discord import app_commands
from discord.ext import commands

import storage


VERIFY_CUSTOM_ID = "verify:button"

DEFAULT_TITLE = "サーバー認証"
DEFAULT_DESCRIPTION = (
    "下のボタンを押すと認証が完了し、"
    "サーバーを閲覧できるようになります。"
)
DEFAULT_BUTTON_LABEL = "認証する"
DEFAULT_BUTTON_EMOJI = "✅"
DEFAULT_COLOR = discord.Color.green().value


def parse_color(value: str) -> int:
    """カラーコードをDiscord Color用の整数に変換します。"""
    text = value.strip().lstrip("#")

    if len(text) != 6:
        raise ValueError(
            "カラーコードは6桁の16進数で指定してください"
            "(例: #00ff00)"
        )

    try:
        return int(text, 16)
    except ValueError as exc:
        raise ValueError(
            "カラーコードは16進数で指定してください"
            "(例: #00ff00)"
        ) from exc


def build_verify_view(
    label: str,
    emoji: str | None,
) -> discord.ui.View:
    """認証ボタンの永続Viewを作成します。"""
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
    """認証機能を管理するCog。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Bot再起動後も認証ボタンを動作させる。
        self.bot.add_view(
            build_verify_view(
                DEFAULT_BUTTON_LABEL,
                DEFAULT_BUTTON_EMOJI,
            )
        )

    @commands.Cog.listener()
    async def on_interaction(
        self,
        interaction: discord.Interaction,
    ):
        """認証ボタンが押されたときの処理。"""
        if interaction.type != discord.InteractionType.component:
            return

        data = interaction.data or {}

        if data.get("custom_id") != VERIFY_CUSTOM_ID:
            return

        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "サーバー内で使ってください。",
                ephemeral=True,
            )

        role_id = storage.get_value(
            guild.id,
            "verify_role",
        )

        if not role_id:
            return await interaction.response.send_message(
                "認証ロールが設定されていません。\n"
                "管理者に `/setup verifyrole` を実行してもらってください。",
                ephemeral=True,
            )

        role = guild.get_role(role_id)

        if role is None:
            return await interaction.response.send_message(
                "設定されている認証ロールが見つかりません。\n"
                "管理者に再設定を依頼してください。",
                ephemeral=True,
            )

        member = interaction.user

        if role in member.roles:
            return await interaction.response.send_message(
                "すでに認証済みです。",
                ephemeral=True,
            )

        try:
            await member.add_roles(
                role,
                reason="ボタン認証",
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "権限不足でロールを付与できませんでした。\n"
                "Botのロール順位を確認してください。",
                ephemeral=True,
            )

        except discord.HTTPException:
            return await interaction.response.send_message(
                "Discordとの通信中にエラーが発生しました。\n"
                "もう一度お試しください。",
                ephemeral=True,
            )

        await interaction.response.send_message(
            "認証が完了しました！ようこそ。",
            ephemeral=True,
        )

    # ==============================
    # /setup グループ
    # ==============================

    setup_group = app_commands.Group(
        name="setup",
        description="Bot設定コマンド",
    )

    @setup_group.command(
        name="verifyrole",
        description="認証時に付与するロールを設定します",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def setup_verifyrole(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        storage.set_guild_value(
            interaction.guild_id,
            "verify_role",
            role.id,
        )

        await interaction.response.send_message(
            f"認証ロールを {role.mention} に設定しました。",
            ephemeral=True,
        )

    @setup_group.command(
        name="verifymessage",
        description="認証パネルの見た目をカスタマイズします",
    )
    @app_commands.describe(
        title="パネルのタイトル",
        description="パネルの説明文",
        buttonlabel="ボタンに表示する文字",
        buttonemoji="ボタンに表示する絵文字",
        color="埋め込みの色(#00ff00など)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
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
            storage.set_guild_value(
                guild_id,
                "verify_title",
                title,
            )

        if description is not None:
            storage.set_guild_value(
                guild_id,
                "verify_description",
                description,
            )

        if buttonlabel is not None:
            storage.set_guild_value(
                guild_id,
                "verify_button_label",
                buttonlabel,
            )

        if buttonemoji is not None:
            value = buttonemoji.strip().lower()

            if value in ("none", "なし", ""):
                emoji_value = None
            else:
                emoji_value = buttonemoji

            storage.set_guild_value(
                guild_id,
                "verify_button_emoji",
                emoji_value,
            )

        if color is not None:
            try:
                color_value = parse_color(color)

            except ValueError as exc:
                return await interaction.response.send_message(
                    str(exc),
                    ephemeral=True,
                )

            storage.set_guild_value(
                guild_id,
                "verify_color",
                color_value,
            )

        await interaction.response.send_message(
            "認証パネルの設定を更新しました。\n"
            "`/verifypanel` で反映したパネルを設置できます。",
            ephemeral=True,
        )

    # ==============================
    # /verifypanel
    # ==============================

    @app_commands.command(
        name="verifypanel",
        description="認証パネルをこのチャンネルに設置します",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def verifypanel(
        self,
        interaction: discord.Interaction,
    ):
        # 最初に応答を確保して3秒タイムアウトを防ぐ。
        await interaction.response.defer(
            ephemeral=True
        )

        guild_id = interaction.guild_id

        if guild_id is None:
            return await interaction.followup.send(
                "サーバー内で使ってください。",
                ephemeral=True,
            )

        channel = interaction.channel

        if not isinstance(
            channel,
            discord.TextChannel,
        ):
            return await interaction.followup.send(
                "このコマンドはテキストチャンネルで使用してください。",
                ephemeral=True,
            )

        role_id = storage.get_value(
            guild_id,
            "verify_role",
        )

        if not role_id:
            return await interaction.followup.send(
                "先に `/setup verifyrole` で"
                "認証ロールを設定してください。",
                ephemeral=True,
            )

        title = storage.get_value(
            guild_id,
            "verify_title",
            DEFAULT_TITLE,
        )

        description = storage.get_value(
            guild_id,
            "verify_description",
            DEFAULT_DESCRIPTION,
        )

        button_label = storage.get_value(
            guild_id,
            "verify_button_label",
            DEFAULT_BUTTON_LABEL,
        )

        button_emoji = storage.get_value(
            guild_id,
            "verify_button_emoji",
            DEFAULT_BUTTON_EMOJI,
        )

        color_value = storage.get_value(
            guild_id,
            "verify_color",
            DEFAULT_COLOR,
        )

        try:
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color(color_value),
            )

            try:
                view = build_verify_view(
                    button_label,
                    button_emoji,
                )

            except (
                discord.InvalidArgument,
                ValueError,
                TypeError,
            ):
                # 絵文字が不正なら絵文字なしで作成。
                view = build_verify_view(
                    button_label,
                    None,
                )

            await channel.send(
                embed=embed,
                view=view,
            )

        except discord.Forbidden:
            return await interaction.followup.send(
                "このチャンネルにメッセージを送信する権限がありません。",
                ephemeral=True,
            )

        except discord.HTTPException:
            return await interaction.followup.send(
                "認証パネルの送信中にDiscord側で"
                "エラーが発生しました。",
                ephemeral=True,
            )

        except (
            ValueError,
            TypeError,
        ):
            return await interaction.followup.send(
                "認証パネルの設定値が不正です。\n"
                "`/setup verifymessage` で確認してください。",
                ephemeral=True,
            )

        await interaction.followup.send(
            "✅ 認証パネルを設置しました。",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
