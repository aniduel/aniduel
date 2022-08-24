import asyncio
import logging
import pathlib

import discord
from discord import app_commands
from discord.ext import commands

from config import TEST_GUILD
from bot import ShardedBot


_log = logging.getLogger()

@app_commands.guilds(TEST_GUILD)
class Developer(commands.GroupCog):
    def __init__(self, bot: ShardedBot):
        self.bot = bot

    @app_commands.command(
        description="Developer: Disable/Enable bot"
    )
    async def disenable(self, interaction: discord.Interaction):
        self.bot.disabled = not self.bot.disabled
        await interaction.response.send_message(
            f"Bot's disabled setting has been set to: `{self.bot.disabled}`",
            ephemeral=True
        )

    @app_commands.command(
        description="Developer: Reload cogs and re-sync commands"
    )
    async def reload(self, interaction: discord.Interaction, resync: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)

        path = pathlib.Path("cogs/")
        for posix in path.iterdir():
            if posix.is_dir():
                continue

            name = posix.name[:-3]
            ext = "cogs.%s" % name

            await self.bot.reload_extension(ext)
            _log.info("Reloaded cog %s", ext)

        
        if resync:
            guild = discord.Object(TEST_GUILD)
            tree = self.bot.tree
            tree.copy_global_to(guild=guild)

            _log.info("Upserting global and guild commands")
            await asyncio.gather(
                tree.sync(),
                tree.sync(guild=guild)
            )

        confirmation = (
            "Reloaded cogs + re-synced commands"
            if resync is True else "Reloaded cogs"
        )

        await interaction.followup.send(confirmation, ephemeral=True)


async def setup(bot: ShardedBot):
    await bot.add_cog(Developer(bot))
    