# vrevel-creature-bot

Minimal Discord bot built with Python, `discord.py`, Docker Compose, and automatic deployment to a Raspberry Pi.

## Project structure

```text
vrevel-creature-bot/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── bot/
│   ├── __init__.py
│   ├── main.py
│   └── extensions/
│       ├── __init__.py
│       └── general.py
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── README.md
└── requirements.txt
```

The structure has three important levels:

```text
bot/main.py
    loads
        ↓
bot/extensions/general.py          ← Discord.py extension
    contains
        ↓
class General(commands.Cog)        ← cog
    contains
        ↓
/ping, /about, ...                 ← commands
```

### What is a Discord.py extension?

An **extension** is an importable Python module that the bot can load.

In this project, this file is an extension:

```text
bot/extensions/general.py
```

It is loaded by its module path:

```python
await bot.load_extension("bot.extensions.general")
```

Every extension must expose an asynchronous `setup` function:

```python
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
```

An extension is the unit used to organize and load a feature area. It may contain commands, cogs, event listeners, or background tasks.

### What is a cog?

A **cog** is a class that groups related Discord functionality.

```python
class General(commands.Cog):
    ...
```

For example, the `General` cog can contain:

```text
/ping
/about
/hello
```

A future `Creatures` cog could contain:

```text
/creature
/feed
/stats
```

The distinction is:

```text
extension = Python module/file loaded by the bot
cog       = class inside the extension
command   = method inside the cog
```

For a small bot, use one cog per extension file. This keeps the mapping obvious:

```text
extensions/general.py    → General cog
extensions/creatures.py  → Creatures cog
extensions/admin.py      → Admin cog
```

## Core files

### `bot/main.py`

`main.py` starts the bot, loads extensions, and synchronizes slash commands to the configured Discord server.

```python
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
    level=os.getenv("LOG_LEVEL", "INFO"),
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

        # Make the commands available immediately in this server.
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        logger.info(
            "Synced %d command(s) to guild %d",
            len(synced),
            GUILD_ID,
        )

    async def on_ready(self) -> None:
        logger.info(
            "Logged in as %s (id=%s)",
            self.user,
            self.user.id if self.user else None,
        )


def main() -> None:
    bot = VrevelCreatureBot()
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
```

### `bot/extensions/general.py`

`general.py` contains small general-purpose commands.

```python
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
```

The empty `__init__.py` files make `bot` and `bot.extensions` importable Python packages.

## Adding commands

### Add a related command

Add it to the existing cog.

For example, add `/hello` inside the `General` class in `bot/extensions/general.py`:

```python
@app_commands.command(
    name="hello",
    description="Receive a greeting.",
)
async def hello(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        f"Hello, {interaction.user.mention}!"
    )
```

### Add a new feature area

Create a new extension when commands belong to a distinct feature.

```text
bot/extensions/creatures.py
```

```python
import discord
from discord import app_commands
from discord.ext import commands


class Creatures(commands.Cog):
    @app_commands.command(
        name="creature",
        description="Summon a creature.",
    )
    async def creature(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("A creature appeared!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Creatures())
```

Register the extension in `bot/main.py`:

```python
EXTENSIONS = (
    "bot.extensions.general",
    "bot.extensions.creatures",
)
```

### Growth rule

Keep the structure small until the code requires another layer:

| Situation | Action |
|---|---|
| A new command belongs to an existing feature | Add it to the existing cog |
| Several commands form a distinct feature | Create a new extension and cog |
| A command contains substantial reusable logic | Move that logic into a service module later |
| Code is used by only one short command | Keep it in the extension |

Do not add `services/`, `utils/`, repositories, or database abstractions before there is real logic to place there.

## Environment configuration

The Pi-only environment file is:

```text
/home/ubuntu/apps/vrevel-creature-bot/.env
```

Create it with:

```bash
cd /home/ubuntu/apps/vrevel-creature-bot
cp .env.example .env
nvim .env
chmod 600 .env
```

Contents:

```dotenv
DISCORD_TOKEN=your-real-discord-bot-token
DISCORD_GUILD_ID=your-numeric-discord-server-id
LOG_LEVEL=INFO
```

The `.env` file must not be committed.

## Docker

Build and start the bot:

```bash
cd /home/ubuntu/apps/vrevel-creature-bot
docker compose up -d --build
```

Inspect it:

```bash
docker compose ps
docker compose logs --since=5m -f
```

The container executes:

```text
python -m bot.main
```

## Deployment

Deployment flow:

```text
push to main
      ↓
GitHub Actions validates the project
      ↓
validated commit is published to deploy
      ↓
Pi cron job runs the sync script
      ↓
Pi fetches deploy and rebuilds the container
```

The repository is located at:

```text
/home/ubuntu/apps/vrevel-creature-bot
```

The Pi deployment script is intentionally outside the repository:

```text
/home/ubuntu/apps/sync-vrevel-creature-bot.sh
```

This prevents `git reset --hard origin/deploy` from replacing the deployment script.

### Cron job

Make the script executable:

```bash
chmod +x /home/ubuntu/apps/sync-vrevel-creature-bot.sh
```

Open the user crontab:

```bash
EDITOR=nvim crontab -e
```

Add:

```cron
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

*/2 * * * * /usr/bin/flock -n /tmp/vrevel-creature-bot-deploy.lock /home/ubuntu/apps/sync-vrevel-creature-bot.sh >> /home/ubuntu/apps/vrevel-creature-bot-deploy.log 2>&1
```

Verify:

```bash
crontab -l
```

Read deployment logs:

```bash
tail -f /home/ubuntu/apps/vrevel-creature-bot-deploy.log
```

## Normal development workflow

On the development computer:

```bash
git add .
git commit -m "Add creature command"
git push
```

After GitHub updates the `deploy` branch, the Pi deploys the change during the next cron run.
