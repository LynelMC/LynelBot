import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from utils.embeds import EmbedUtils
from utils.logger import Logger
from collections import defaultdict, deque
import datetime
import asyncio

class AntiSpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_records = defaultdict(lambda: deque(maxlen=20))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        guild_id = message.guild.id
        if not storage.get_setting("modules", guild_id, "antispam_enabled", False):
            return

        user_id = message.author.id
        now = datetime.datetime.now(datetime.timezone.utc)
        self.user_records[user_id].append(now)

        # 設定の取得
        threshold = storage.get_setting("antispam", guild_id, "threshold", 5)
        interval = storage.get_setting("antispam", guild_id, "interval", 5) # 秒
        
        if len(self.user_records[user_id]) >= threshold:
            time_diff = (self.user_records[user_id][-1] - self.user_records[user_id][0]).total_seconds()
            if time_diff <= interval:
                await self._handle_spam(message)

    async def _handle_spam(self, message):
        guild = message.guild
        member = message.author
        action = storage.get_setting("antispam", guild.id, "action", "timeout")
        
        try:
            if action == "timeout":
                until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
                await member.timeout(until, reason="スパム検知")
            elif action == "kick":
                await member.kick(reason="スパム検知")
            elif action == "ban":
                await guild.ban(member, reason="スパム検知")
            
            await message.channel.send(f"{member.mention} スパムを検知したため {action} しました。", delete_after=10)
            await Logger.log_action(self.bot, guild.id, "スパム検知", f"{member.mention} のスパムを検知し、{action} を実行しました。", color=discord.Color.orange())
            self.user_records[member.id].clear()
        except:
            pass

    @app_commands.command(name="antispam-setup", description="AntiSpamの設定")
    @is_admin()
    async def antispam_setup(self, interaction: discord.Interaction, threshold: int, interval: int, action: str):
        if action not in ["timeout", "kick", "ban"]:
            return await interaction.response.send_message("アクションは timeout, kick, ban のいずれかである必要があります。", ephemeral=True)
        
        guild_id = interaction.guild_id
        storage.set_data("antispam", guild_id, "threshold", threshold)
        storage.set_data("antispam", guild_id, "interval", interval)
        storage.set_data("antispam", guild_id, "action", action)
        
        await interaction.response.send_message(f"AntiSpamを設定しました: {threshold}回/{interval}秒 ➔ {action}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AntiSpamCog(bot))
