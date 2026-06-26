from __future__ import annotations

import logging
import os

import discord
from discord import app_commands

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("vrevel_creature_bot")


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TOKEN = required_env("DISCORD_TOKEN")
GUILD_ID_RAW = os.getenv("DISCORD_GUILD_ID")
GUILD_ID = int(GUILD_ID_RAW) if GUILD_ID_RAW else None


class VrevelCreatureBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.default(),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if GUILD_ID is not None:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info("Synced %d command(s) to guild %d", len(synced), GUILD_ID)
        else:
            synced = await self.tree.sync()
            logger.info("Synced %d global command(s)", len(synced))


bot = VrevelCreatureBot()


@bot.event
async def on_ready() -> None:
    assert bot.user is not None
    logger.info("Logged in as %s (id=%d)", bot.user, bot.user.id)


@bot.tree.command(name="ping", description="Check whether the bot is online")
async def ping(interaction: discord.Interaction) -> None:
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! {latency_ms} ms")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    logger.error(
        "Application command failed",
        exc_info=(type(error), error, error.__traceback__),
    )
    message = "The command failed. Check the bot logs."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


def main() -> None:
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
