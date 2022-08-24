from __future__ import annotations

import json
import asyncio
import logging
from dataclasses import dataclass
from typing import (
    Optional,
    Union,
    Coroutine,
    Callable,
    TYPE_CHECKING
)

from redis import asyncio as aioredis
from discord.ext import commands

from utils import fmt
from config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT
)

if TYPE_CHECKING:
    from redis.asyncio.client import PubSub
    from bot import ShardedBot


_log = logging.getLogger(__name__)


@dataclass
class RedisMessage:
    type: str
    pattern: Optional[Union[str, bytes]]
    channel: bytes
    data: bytes

class RedisIPC(commands.Cog):
    def __init__(self, bot: ShardedBot):
        self.bot = bot
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[PubSub] = None

        self.listen_future: Optional[asyncio.Task] = None

        self.channel_handlers = {
            "stripe:1": self.stripe_handler
        }

    async def cog_load(self) -> None:
        redis = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )
        self.redis = redis
        self.pubsub = redis.pubsub()

        # subscribe to channels
        # stripe
        await self.pubsub.subscribe("stripe:1")
        _log.info("Subscribed to stripe:1")

        # create the listen task
        self.listen_future = asyncio.ensure_future(
            self._listen_task()
        )

    async def cog_unload(self) -> None:
        _log.warning("Cog unloaded, cancelling listen future")
        if self.listen_future:
            self.listen_future.cancel("Cog unloaded, cancelled listen future")
        
        if self.redis:
            await self.pubsub.close() # type: ignore
            await self.redis.close()
        
    async def _listen_task(self):
        # the root listen task
        # this is responsible for routing
        # messages to their respectable methods
        assert self.pubsub is not None

        try:
            async for message in self.pubsub.listen(): # type: ignore
                # I honestly don't know why we now need to await listen
                _log.debug("Received ipc message: %s", message)
                try:
                    message = RedisMessage(**message)
                except TypeError:
                    continue

                try:
                    data = json.loads(message.data)
                except (TypeError, ValueError, json.JSONDecodeError):
                    _log.error("Failed to decode ipc data: %s", message.data)
                    continue
                
                channel = message.channel.decode()
                handler = self.channel_handlers.get(channel)

                if not handler:
                    _log.warning("IPC message received with no matching channel handler: %s", channel)
                    continue

                wrapped = self._run_handler(handler, data)
                asyncio.create_task(wrapped, name=f"{channel}-handler")
        except Exception as exc:
            _log.warning(
                "No longer listening to redis messages, possible disconnect: %s: %s",
                exc.__class__.__name__,
                exc
            )

    async def _run_handler(self, handler: Callable[..., Coroutine[None, None, None]], *args):
        try:
            await handler(*args)
        except Exception as exc:
            _log.warning(
                "IPC handler failed: %s: %s",
                exc.__class__.__name__,
                exc
            )

    async def stripe_handler(self, data: dict):
        print("Stripe Handler", data)

async def setup(bot: ShardedBot):
    await bot.add_cog(RedisIPC(bot))