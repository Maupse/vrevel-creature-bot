import logging
import os

import discord
from discord.ext import commands


TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

EXTENSIONS = (
    "bot.extensions.general",
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("vrevel_creature_bot")


class VrevelCreatureBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.default(),
        )

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            await self.load_extension(extension)
            logger.info("Loaded extension %s", extension)

        guild = discord.Object(id=GUILD_ID)

        # Copy globally defined commands into the development guild so
        # changes appear immediately.
        self.tree.copy_global_to(guild=guild)

        synced_commands = await self.tree.sync(guild=guild)

        logger.info(
            "Synced %d command(s) to guild %d",
            len(synced_commands),
            GUILD_ID,
        )

    async def on_ready(self) -> None:
        if self.user is None:
            return

        logger.info(
            "Logged in as %s (id=%d)",
            self.user,
            self.user.id,
        )


def main() -> None:
    bot = VrevelCreatureBot()
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
