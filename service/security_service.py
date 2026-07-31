import discord
import re
import datetime
from storage import storage
from utils.logger import Logger
from utils.embeds import EmbedUtils

class SecurityService:
    def __init__(self, bot):
        self.bot = bot
        self.url_pattern = re.compile(r'https?://\S+')
        self.phishing_domains = ["discord-gift.com", "discord-nitro.com", "dlscord.com", "discord-app.com"]
        self.join_records = {} # guild_id -> list of timestamps

    async def check_message(self, message: discord.Message):
        guild_id = message.guild.id
        
        # 招待リンク制限
        if storage.get_setting("security", guild_id, "anti_invite", False):
            if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
                if not message.author.guild_permissions.manage_messages:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} 招待リンクの送信は禁止されています。", delete_after=5)
                    return True

        # フィッシングURL検知
        if storage.get_setting("security", guild_id, "anti_phishing", False):
            urls = self.url_pattern.findall(message.content)
            for url in urls:
                for domain in self.phishing_domains:
                    if domain in url:
                        await message.delete()
                        try:
                            await message.guild.ban(message.author, reason="フィッシングURLの送信")
                            await Logger.log_action(self.bot, guild_id, "フィッシング検知", f"{message.author.mention} をフィッシングURL送信のためBANしました。", color=discord.Color.red())
                        except:
                            pass
                        return True

        # NGワード対策
        ng_words = storage.get_setting("security", guild_id, "ng_words", [])
        for word in ng_words:
            if word in message.content:
                if not message.author.guild_permissions.manage_messages:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} 不適切な言葉が含まれています。", delete_after=5)
                    return True
        
        return False

    async def process_join(self, member: discord.Member):
        guild_id = member.guild.id
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Raid対策 (短時間の大量参加)
        if storage.get_setting("security", guild_id, "anti_raid", False):
            if guild_id not in self.join_records:
                self.join_records[guild_id] = []
            
            self.join_records[guild_id].append(now)
            # 10秒以内の参加をカウント
            self.join_records[guild_id] = [t for t in self.join_records[guild_id] if (now - t).total_seconds() <= 10]
            
            threshold = storage.get_setting("security", guild_id, "raid_threshold", 5)
            if len(self.join_records[guild_id]) >= threshold:
                await Logger.log_action(self.bot, guild_id, "🚨 Raid検知", f"短時間に {len(self.join_records[guild_id])} 人の参加を検知しました。", color=discord.Color.red())
                # 必要に応じてサーバーロック等の処理を追加
        
        # 新規アカウント制限
        min_age_days = storage.get_setting("security", guild_id, "min_account_age", 0)
        if min_age_days > 0:
            age = (now - member.created_at).days
            if age < min_age_days:
                try:
                    await member.kick(reason=f"新規アカウント制限 ({min_age_days}日未満)")
                    await Logger.log_action(self.bot, guild_id, "新規垢制限", f"{member.mention} (作成後{age}日) をキックしました。", color=discord.Color.orange())
                except:
                    pass
