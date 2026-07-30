import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.logger import Logger
from utils.embeds import EmbedUtils
import datetime

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="log-setup", description="ログチャンネルの設定")
    @is_admin()
    async def log_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        storage.set_data("logging", interaction.guild_id, "log_channel_id", str(channel.id))
        await interaction.response.send_message(f"ログチャンネルを {channel.mention} に設定しました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        embed = EmbedUtils.create_embed(
            title="メッセージ編集",
            description=f"{before.author.mention} がメッセージを編集しました。\n[メッセージへ移動]({after.jump_url})",
            color=discord.Color.blue(),
            timestamp=True
        )
        embed.add_field(name="編集前", value=before.content[:1024] or "なし", inline=False)
        embed.add_field(name="編集後", value=after.content[:1024] or "なし", inline=False)
        await Logger.send_log(self.bot, before.guild.id, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return
        
        guild_id = member.guild.id
        if not before.channel:
            desc = f"{member.mention} が VC **{after.channel.name}** に参加しました。"
            color = discord.Color.green()
        elif not after.channel:
            desc = f"{member.mention} が VC **{before.channel.name}** から退出しました。"
            color = discord.Color.red()
        else:
            desc = f"{member.mention} が VC を移動しました: **{before.channel.name}** ➔ **{after.channel.name}**"
            color = discord.Color.blue()
        
        embed = EmbedUtils.create_embed(title="VCログ", description=desc, color=color, timestamp=True)
        await Logger.send_log(self.bot, guild_id, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = EmbedUtils.create_embed(
                title="ニックネーム変更",
                description=f"{before.mention} のニックネームが変更されました。",
                color=discord.Color.blue(),
                timestamp=True
            )
            embed.add_field(name="変更前", value=before.nick or "なし", inline=True)
            embed.add_field(name="変更後", value=after.nick or "なし", inline=True)
            await Logger.send_log(self.bot, before.guild.id, embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
