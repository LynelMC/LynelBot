import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.embeds import EmbedUtils
import datetime


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_text(self, text: str, member: discord.Member):
        guild = member.guild

        joined = (
            member.joined_at.strftime("%Y/%m/%d %H:%M")
            if member.joined_at
            else "不明"
        )

        return (
            text.replace("{user}", member.mention)
            .replace("{username}", member.name)
            .replace("{server}", guild.name)
            .replace("{member_count}", str(guild.member_count))
            .replace(
                "{created_at}",
                member.created_at.strftime("%Y/%m/%d %H:%M"),
            )
            .replace("{joined_at}", joined)
        )
        class WelcomeSetupModal(discord.ui.Modal, title="Welcome設定"):

    welcome_title = discord.ui.TextInput(
        label="Welcomeタイトル",
        default="🎉 ようこそ！",
        required=True,
        max_length=100,
    )

    welcome_description = discord.ui.TextInput(
        label="Welcome本文",
        style=discord.TextStyle.paragraph,
        default="{user} さん、{server}へようこそ！",
        required=True,
        max_length=1000,
    )

    leave_title = discord.ui.TextInput(
        label="退出タイトル",
        default="👋 さようなら！",
        required=True,
        max_length=100,
    )

    leave_description = discord.ui.TextInput(
        label="退出本文",
        style=discord.TextStyle.paragraph,
        default="{username} さんが退出しました。",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "title",
            str(self.welcome_title),
        )

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "description",
            str(self.welcome_description),
        )

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "leave_title",
            str(self.leave_title),
        )

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "leave_description",
            str(self.leave_description),
        )

        await interaction.response.send_message(
            "✅ タイトルと本文を保存しました。\n次はチャンネルを選択します。",
            ephemeral=True,
        )
        class WelcomeChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.channel_select(
        channel_types=[discord.ChannelType.text],
        placeholder="Welcomeチャンネルを選択"
    )
    async def welcome_channel(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect,
    ):
        channel = select.values[0]

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "channel_id",
            str(channel.id),
        )

        await interaction.response.send_message(
            "✅ Welcomeチャンネルを保存しました。\n次は退出チャンネルを選択してください。",
            view=LeaveChannelView(),
            ephemeral=True,
        )


class LeaveChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.channel_select(
        channel_types=[discord.ChannelType.text],
        placeholder="退出チャンネルを選択"
    )
    async def leave_channel(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect,
    ):
        channel = select.values[0]

        storage.set_data(
            "welcome",
            interaction.guild.id,
            "leave_channel_id",
            str(channel.id),
        )

        await interaction.response.send_message(
            "✅ 退出チャンネルを保存しました。\n次は自動ロールを選択してください。",
            view=RoleSelectView(),
            ephemeral=True,
        )
        class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.role_select(
        placeholder="自動付与するロールを選択（任意）",
        min_values=0,
        max_values=1,
    )
    async def role_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.RoleSelect,
    ):
        if len(select.values) == 0:
            storage.set_data(
                "welcome",
                interaction.guild.id,
                "auto_role_id",
                None,
            )
        else:
            role = select.values[0]

            storage.set_data(
                "welcome",
                interaction.guild.id,
                "auto_role_id",
                str(role.id),
            )

        storage.set_data(
            "modules",
            interaction.guild.id,
            "welcome_enabled",
            True,
        )

        embed = EmbedUtils.create_embed(
            title="✅ Welcome設定完了",
            description=(
                "Welcome機能の設定が完了しました！\n\n"
                "参加・退出メッセージが有効になりました。"
            ),
            color=discord.Color.green(),
            timestamp=True,
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
        
