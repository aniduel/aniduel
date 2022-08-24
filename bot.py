import logging
import pathlib

import discord
from discord.ext import commands

from config import APPLICATION_ID, SUPPORT_GUILD_INVITE


_log = logging.getLogger()

DISABLED_MESSAGE = (
    "The bot has currently been disabled, either due to maintenance or due "
    "to a major bug being identified. Please try again later. "
    f"You can always join our support server at {SUPPORT_GUILD_INVITE}"
)

class ShardedBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("ad!"),
            intents=discord.Intents.none(),
            application_id=APPLICATION_ID,
            chunk_guilds_at_startup=False
        )

        discord.utils.stream_supports_colour = lambda _: True # for some reason is false
        # on my choice of terminal even though it does support it
        discord.utils.setup_logging(level=logging.INFO)

        self.disabled = False

        async def disabled_check(interaction: discord.Interaction) -> bool:
            assert self.application is not None

            if interaction.user.id == self.application.owner.id:
                return True
            
            if self.disabled is True:
                try:
                    await interaction.response.send_message(DISABLED_MESSAGE, ephemeral=True)
                except Exception:
                    # suppress any errors that occur here
                    pass
                return False

            return True

        self.tree.interaction_check = disabled_check

    async def setup_hook(self):
        path = pathlib.Path("cogs/")
        for posix in path.iterdir():
            if posix.is_dir():
                continue

            name = posix.name[:-3]
            ext = "cogs.%s" % name

            await self.load_extension(ext)
            _log.info("Loaded cog %s", ext)
