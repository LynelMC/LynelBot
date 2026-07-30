import discord
from utils.logger import Logger
from utils.embeds import EmbedUtils
from models.punishment import PunishmentRecord
from storage import storage
import datetime

class ModerationService:
    def __init__(self, bot):
        self.bot = bot

    async def ban_member(self, guild: discord.Guild, target: discord.User, executor: discord.Member, reason: str, send_dm: bool):
        if send_dm:
            try:
                embed = EmbedUtils.create_embed(
                    title=f"【{guild.name}】BAN通知",
                    description=f"あなたは {guild.name} で BAN されました。\n理由: {reason}",
                    color=discord.Color.red(),
                    timestamp=True
                )
                await target.send(embed=embed)
            except:
                pass

        await guild.ban(target, reason=reason)
        
        # ログ記録
        await Logger.log_action(self.bot, guild.id, "メンバーBAN", f"{target.mention} がBANされました。", color=discord.Color.red(), fields=[
            ("実行者", executor.mention, True),
            ("理由", reason, False)
        ])
        
        # データの保存 (Punishment History)
        record = PunishmentRecord(
            user_id=str(target.id),
            action="BAN",
            executor_id=str(executor.id),
            reason=reason,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        history = storage.get_setting("punishment", guild.id, "history", [])
        history.append(record.to_dict())
        storage.set_data("punishment", guild.id, "history", history)

    async def timeout_member(self, guild: discord.Guild, member: discord.Member, executor: discord.Member, duration_minutes: int, reason: str):
        until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=duration_minutes)
        await member.timeout(until, reason=reason)
        
        await Logger.log_action(self.bot, guild.id, "タイムアウト", f"{member.mention} がタイムアウトされました。", color=discord.Color.orange(), fields=[
            ("期間", f"{duration_minutes}分", True),
            ("実行者", executor.mention, True),
            ("理由", reason, False)
        ])
        
        record = PunishmentRecord(
            user_id=str(member.id),
            action="Timeout",
            executor_id=str(executor.id),
            reason=reason,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            duration=duration_minutes
        )
        history = storage.get_setting("punishment", guild.id, "history", [])
        history.append(record.to_dict())
        storage.set_data("punishment", guild.id, "history", history)
