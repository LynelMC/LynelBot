import discord
from discord import app_commands
from discord.ext import commands, tasks
from storage import storage
from utils.checks import has_mod_perms
from utils.embeds import EmbedUtils
from utils.logger import Logger
from utils.time_utils import parse_duration
import datetime

class RoleRestrictionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_restrictions.start()

    def cog_unload(self):
        self.check_restrictions.cancel()

    @tasks.loop(minutes=1)
    async def check_restrictions(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        data = storage.get_data("punishment")
        
        for guild_id_str, guild_data in data.items():
            guild = self.bot.get_guild(int(guild_id_str))
            if not guild: continue
            
            restrictions = guild_data.get("role_restrictions", {})
            for member_id_str, info in list(restrictions.items()):
                until = datetime.datetime.fromisoformat(info["until"]) if info.get("until") else None
                if until and now >= until:
                    await self._restore_roles(guild, int(member_id_str), info)
                    del restrictions[member_id_str]
            
            storage.set_data("punishment", int(guild_id_str), "role_restrictions", restrictions)

    async def _restore_roles(self, guild, member_id, info):
        member = guild.get_member(member_id)
        if not member: return
        
        # 隔離ロール削除
        q_role_id = storage.get_setting("moderation", guild.id, "quarantine_role_id")
        if q_role_id:
            q_role = guild.get_role(int(q_role_id))
            if q_role: await member.remove_roles(q_role)
            
        # 元のロール復元
        for role_id in info["role_ids"]:
            role = guild.get_role(int(role_id))
            if role:
                try: await member.add_roles(role)
                except: pass

    @app_commands.command(name="restrict", description="メンバーのロールを制限します")
    @has_mod_perms()
    async def restrict(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "理由なし"):
        delta = parse_duration(duration)
        until = datetime.datetime.now(datetime.timezone.utc) + delta if delta else None
        
        # ロール保存と削除
        role_ids = [str(r.id) for r in member.roles if not r.is_default() and not r.managed]
        for r_id in role_ids:
            role = interaction.guild.get_role(int(r_id))
            if role:
                try: await member.remove_roles(role)
                except: pass
        
        # 隔離ロール付与
        q_role_id = storage.get_setting("moderation", interaction.guild_id, "quarantine_role_id")
        if q_role_id:
            q_role = interaction.guild.get_role(int(q_role_id))
            if q_role: await member.add_roles(q_role)
            
        # データ保存
        restrictions = storage.get_setting("punishment", interaction.guild_id, "role_restrictions", {})
        restrictions[str(member.id)] = {
            "role_ids": role_ids,
            "until": until.isoformat() if until else None,
            "reason": reason
        }
        storage.set_data("punishment", interaction.guild_id, "role_restrictions", restrictions)
        
        await interaction.response.send_message(f"{member.mention} を制限しました。期間: {duration}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleRestrictionCog(bot))
