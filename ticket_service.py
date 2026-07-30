import discord
from storage import storage
from utils.embeds import EmbedUtils
import datetime

class TicketService:
    def __init__(self, bot):
        self.bot = bot

    async def create_ticket(self, guild: discord.Guild, user: discord.Member):
        # チケット番号の管理
        count = storage.get_setting("ticket", guild.id, "ticket_count", 0) + 1
        storage.set_data("ticket", guild.id, "ticket_count", count)
        
        ticket_name = f"ticket-{count:04d}"
        
        # カテゴリの取得
        category_id = storage.get_setting("guild_config", guild.id, "ticket_category_id")
        category = guild.get_channel(int(category_id)) if category_id else None
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        
        channel = await guild.create_text_channel(
            name=ticket_name, 
            category=category, 
            overwrites=overwrites
        )
        
        # チケットデータの保存
        ticket_data = {
            "creator_id": str(user.id),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "open"
        }
        storage.set_data("ticket", guild.id, str(channel.id), ticket_data)
        
        return channel, count

    async def close_ticket(self, channel: discord.TextChannel, executor: discord.Member):
        guild_id = channel.guild.id
        ticket_data = storage.get_setting("ticket", guild_id, str(channel.id))
        
        if ticket_data:
            ticket_data["status"] = "closed"
            ticket_data["closed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            ticket_data["closed_by"] = str(executor.id)
            storage.set_data("ticket", guild_id, str(channel.id), ticket_data)
            
            # 作成者の権限剥奪
            creator_id = ticket_data.get("creator_id")
            creator = channel.guild.get_member(int(creator_id))
            if creator:
                await channel.set_permissions(creator, view_channel=True, send_messages=False)
            
            return True
        return False
