import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Check whether the bot is online.",
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"Pong! `{latency_ms} ms`",
            ephemeral=True,
        )

    @app_commands.command(
        name="about",
        description="Show information about the bot.",
    )
    async def about(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "I am vrevel-creature.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
