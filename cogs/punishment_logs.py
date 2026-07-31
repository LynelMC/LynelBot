import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import has_mod_perms
from utils.embeds import EmbedUtils
import datetime

class PunishmentLogsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="history", description="メンバーの処罰履歴を表示します")
    @has_mod_perms()
    async def history(self, interaction: discord.Interaction, user: discord.User):
        # 監査ログの取得には時間がかかるため、必ず defer する
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = EmbedUtils.create_embed(
                title=f"{user} の処罰履歴",
                color=discord.Color.blue(),
                timestamp=True
            )
            
            logs_found = False
            # 監査ログから直近20件を取得
            async for entry in interaction.guild.audit_logs(limit=50):
                if entry.target and entry.target.id == user.id:
                    if entry.action in [discord.AuditLogAction.ban, discord.AuditLogAction.kick, discord.AuditLogAction.timeout]:
                        action_name = str(entry.action).split(".")[-1].capitalize()
                        embed.add_field(
                            name=f"{action_name} - {entry.created_at.strftime('%Y/%m/%d')}",
                            value=f"実行者: {entry.user.mention}\n理由: {entry.reason or 'なし'}",
                            inline=False
                        )
                        logs_found = True
                
                if len(embed.fields) >= 20: # 最大20件まで
                    break
            
            if not logs_found:
                embed.description = "指定されたユーザーの処罰履歴は見つかりませんでした。"
                
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"履歴の取得中にエラーが発生しました: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PunishmentLogsCog(bot))
