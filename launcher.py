import asyncio

import config
from bot import ShardedBot

# attempt to install uvloop
try:
    import uvloop # type: ignore
except ImportError:
    pass
else:
    uvloop.install()


async def launch():
    bot = ShardedBot()
    async with bot:
        await bot.start(config.TOKEN)

asyncio.run(launch())
