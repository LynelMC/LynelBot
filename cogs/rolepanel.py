import discord
from discord import app_commands
from discord.ext import commands

ROLEPANEL_PREFIX = "rolepanel:"


def build_panel_view(roles: list[discord.Role]) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    for role in roles:
        view.add_item(
            discord.ui.Button(
                label=role.name[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"{ROLEPANEL_PREFIX}{role.id}",
            )
        )
    return view


class RolePanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # discord.ui.Buttonにcallbackを付けていないため、生のinteractionイベントで処理する。
        # これによりBot再起動後もcustom_idさえ一致すればボタンが機能し続ける。
        if interaction.type != discord.InteractionType.component:
            return
        data = interaction.data or {}
        custom_id = data.get("custom_id", "")
        if not custom_id.startswith(ROLEPANEL_PREFIX):
            return

        guild = interaction.guild
        if guild is None:
            return

        role_id = int(custom_id.removeprefix(ROLEPANEL_PREFIX))
        role = guild.get_role(role_id)
        if role is None:
            return await interaction.response.send_message(
                "このロールは削除されたようです。管理者に伝えてください。", ephemeral=True
            )

        member = interaction.user
        try:
            if role in member.roles:
                await member.remove_roles(role, reason="ロールパネル")
                await interaction.response.send_message(f"{role.name} を外しました。", ephemeral=True)
            else:
                await member.add_roles(role, reason="ロールパネル")
                await interaction.response.send_message(f"{role.name} を付与しました。", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "権限不足でロールを変更できませんでした。Botのロール順位を確認してください。",
                ephemeral=True,
            )

    @app_commands.command(name="rolepanel", description="ロールパネルをこのチャンネルに設置します(最大5個)")
    @app_commands.describe(
        title="パネルのタイトル",
        description="パネルの説明文",
        role1="1個目のロール",
        role2="2個目のロール(任意)",
        role3="3個目のロール(任意)",
        role4="4個目のロール(任意)",
        role5="5個目のロール(任意)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def rolepanel(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        role1: discord.Role,
        role2: discord.Role = None,
        role3: discord.Role = None,
        role4: discord.Role = None,
        role5: discord.Role = None,
    ):
        roles = [r for r in [role1, role2, role3, role4, role5] if r is not None]

        bot_member = interaction.guild.me
        for r in roles:
            if r >= bot_member.top_role:
                return await interaction.response.send_message(
                    f"{r.mention} はBotのロールより上位のため付与できません。ロール順位を調整してください。",
                    ephemeral=True,
                )

        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        embed.add_field(
            name="ロール一覧",
            value="\n".join(f"・{r.mention}" for r in roles),
            inline=False,
        )
        view = build_panel_view(roles)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("ロールパネルを設置しました。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RolePanel(bot))
