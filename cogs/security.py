import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
from utils.checks import is_admin
from services.security_service import SecurityService

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = SecurityService(bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        await self.service.check_message(message)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.service.process_join(member)

    @app_commands.command(name="security-setup", description="セキュリティ機能の設定")
    @is_admin()
    async def security_setup(self, interaction: discord.Interaction, 
                               anti_invite: bool = None, 
                               anti_phishing: bool = None,
                               anti_raid: bool = None,
                               min_age_days: int = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id
        
        if anti_invite is not None: storage.set_data("security", guild_id, "anti_invite", anti_invite)
        if anti_phishing is not None: storage.set_data("security", guild_id, "anti_phishing", anti_phishing)
        if anti_raid is not None: storage.set_data("security", guild_id, "anti_raid", anti_raid)
        if min_age_days is not None: storage.set_data("security", guild_id, "min_account_age", min_age_days)
        
        await interaction.followup.send("セキュリティ設定を更新しました。", ephemeral=True)

    @app_commands.command(name="ngword-add", description="NGワードを追加します")
    @is_admin()
    async def ngword_add(self, interaction: discord.Interaction, word: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id
        ng_words = storage.get_setting("security", guild_id, "ng_words", [])
        if word not in ng_words:
            ng_words.append(word)
            storage.set_data("security", guild_id, "ng_words", ng_words)
            await interaction.followup.send(f"NGワードに `{word}` を追加しました。", ephemeral=True)
        else:
            await interaction.followup.send("そのワードは既に追加されています。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
