import discord
from discord import app_commands
from discord.ext import commands
from views.dashboard_view import DashboardView
from utils.checks import is_admin
from storage import storage
from utils.embeds import EmbedUtils

class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dashboard", description="サーバーダッシュボードの表示")
    @is_admin()
    async def dashboard(self, interaction: discord.Interaction):
        # 応答を保留してタイムアウトを防ぐ (ephemeral=True は後続の送信にも引き継がれる)
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            
            embed = EmbedUtils.create_embed(
                title=f"{guild.name} ダッシュボード",
                color=discord.Color.purple(),
                timestamp=True
            )
            
            # 統計情報 (Intents.membersが必要)
            # メンバーリストがキャッシュされていない場合を考慮
            if not guild.chunked and guild.member_count > 1000:
                # 大規模サーバーでまだチャンクされていない場合
                bot_count = "集計中..."
                user_count = guild.member_count
            else:
                bot_count = len([m for m in guild.members if m.bot])
                user_count = guild.member_count - bot_count
            
            embed.add_field(name="メンバー統計", value=f"総数: {guild.member_count}\nユーザー: {user_count}\nBot: {bot_count}", inline=True)
            
            # チケット統計
            ticket_data = storage.get_data("ticket").get(str(guild.id), {})
            ticket_count = ticket_data.get("ticket_count", 0)
            embed.add_field(name="チケット統計", value=f"総発行数: {ticket_count}", inline=True)
            
            # モジュール状態
            mod_data = storage.get_data("modules").get(str(guild.id), {})
            enabled_mods = [k.replace("_enabled", "").capitalize() for k, v in mod_data.items() if v]
            embed.add_field(name="有効なモジュール", value=", ".join(enabled_mods) if enabled_mods else "なし", inline=False)
            
            # 保留した応答に対してメッセージを送信
            await interaction.followup.send(embed=embed, view=DashboardView(guild.id), ephemeral=True)
            
        except Exception as e:
            # エラーが発生した場合はユーザーに通知
            error_embed = EmbedUtils.error_embed(f"ダッシュボードの読み込み中にエラーが発生しました: {e}")
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(DashboardCog(bot))
