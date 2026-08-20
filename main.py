import os
import asyncio
import logging

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from keep_alive import keep_alive


load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)


INITIAL_COGS = [
    "cogs.verification",
    "cogs.rolepanel",
    "cogs.logging_cog",
    "cogs.welcome_log",
    "cogs.mention_guard",
    "cogs.moderation",
]


@tasks.loop(seconds=30)
async def update_ping_status():
    if not bot.is_ready():
        return

    ping = round(bot.latency * 1000)

    await bot.change_presence(
        activity=discord.Game(
            name=f"Ping: {ping}ms"
        )
    )


@update_ping_status.before_loop
async def before_update_ping_status():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash command sync failed: {e}")

    if not update_ping_status.is_running():
        update_ping_status.start()


async def main():
    async with bot:
        for cog in INITIAL_COGS:
            await bot.load_extension(cog)

        keep_alive()

        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN が設定されていません。"
            "環境変数を確認してください。"
        )

    asyncio.run(main())
