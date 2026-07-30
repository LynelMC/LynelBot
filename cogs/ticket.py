import discord
from discord import app_commands
from discord.ext import commands
from views.ticket_view import PersistentTicketPanelView, TicketActionView
from utils.checks import is_admin
from utils.embeds import EmbedUtils
from services.ticket_service import TicketService
import datetime

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = TicketService(bot)

    @app_commands.command(name="ticket-setup", description="チケットパネルの設置")
    @is_admin()
    async def ticket_setup(self, interaction: discord.Interaction):
        embed = EmbedUtils.create_embed(
            title="お問い合わせチケット",
            description="下のボタンを押してチケットを作成してください。",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed, view=PersistentTicketPanelView())
        await interaction.response.send_message("チケットパネルを設置しました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data.get("custom_id") == "create_ticket_btn":
                await self._handle_ticket_creation(interaction)

    async def _handle_ticket_creation(self, interaction: discord.Interaction):
        try:
            channel, count = await self.service.create_ticket(interaction.guild, interaction.user)
            
            embed = EmbedUtils.create_embed(
                title=f"チケット #{count:04d}",
                description=f"{interaction.user.mention} さん、お問い合わせ内容を入力してください。\n担当者が来るまでお待ちください。",
                color=discord.Color.blue()
            )
            await channel.send(embed=embed, view=TicketActionView(str(channel.id)))
            await interaction.response.send_message(f"チケットを作成しました: {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"チケット作成に失敗しました: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(PersistentTicketPanelView())
        print("Ticket Cog is ready.")

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
