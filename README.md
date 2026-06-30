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
bot/extensions/general.py          ← discord.py extension
    contains
        ↓
class General(commands.Cog)        ← cog
    contains
        ↓
/ping, /about, ...                 ← commands
```

### What is a discord.py extension?

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
extension = Python module or file loaded by the bot
cog       = class inside the extension
command   = method inside the cog
```

For a small bot, use one cog per extension file. This keeps the mapping obvious:

```text
extensions/general.py    → General cog
extensions/creatures.py  → Creatures cog
extensions/admin.py      → Admin cog
```

## Adding commands

### Add a related command

Add the command to the existing cog.

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

Create:

```text
bot/extensions/creatures.py
```

Add:

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

| Situation                                     | Action                                      |
| --------------------------------------------- | ------------------------------------------- |
| A new command belongs to an existing feature  | Add it to the existing cog                  |
| Several commands form a distinct feature      | Create a new extension and cog              |
| A command contains substantial reusable logic | Move that logic into a service module later |
| Code is used by only one short command        | Keep it in the extension                    |

Do not add `services/`, `utils/`, repositories, or database abstractions before there is real logic to place there.

## Git development workflow

Do not make changes directly on the `main` branch.

Create a separate branch for each feature, fix, or maintenance task. When the work is ready, push the branch to GitHub and open a pull request into `main`.

GitHub calls this a **pull request**. GitLab and some other platforms call the same concept a **merge request**.

The workflow is:

```text
update local main
      ↓
create a feature branch
      ↓
make and commit changes
      ↓
push the feature branch
      ↓
open a pull request into main
      ↓
review and approval
      ↓
merge into main
```

### 1. Clone the repository

This is only required the first time:

```bash
git clone https://github.com/OWNER/vrevel-creature-bot.git
cd vrevel-creature-bot
```

Replace `OWNER` with the GitHub username or organization that owns the repository.

### 2. Update the local `main` branch

Before starting new work, switch to `main` and download the latest changes:

```bash
git switch main
git pull --ff-only origin main
```

The `--ff-only` option prevents Git from creating an unexpected merge commit while updating the local branch.

### 3. Create a side branch

Create a new branch with a descriptive name:

```bash
git switch -c feature/add-creature-command
```

Common branch-name prefixes include:

```text
feature/   new functionality
fix/       bug fixes
docs/      documentation changes
refactor/  internal code restructuring
chore/     maintenance work
```

Examples:

```text
feature/add-creature-command
fix/ping-latency
docs/update-readme
refactor/extension-loading
```

Keep branch names short, lowercase, and descriptive.

### 4. Make the changes

Edit the required files:

```bash
nvim bot/extensions/general.py
```

Inspect the current changes:

```bash
git status
git diff
```

### 5. Stage and commit the changes

Stage the relevant files:

```bash
git add bot/extensions/general.py
```

Or stage all changes:

```bash
git add .
```

Create a commit:

```bash
git commit -m "Add creature command"
```

A commit message should briefly describe what the commit changes.

Good examples:

```text
Add creature command
Fix incorrect latency calculation
Document feature branch workflow
Refactor extension loading
```

### 6. Push the side branch

Push the branch to GitHub:

```bash
git push -u origin feature/add-creature-command
```

The `-u` option connects the local branch to the corresponding remote branch.

After the first push, future pushes from the same branch can use:

```bash
git push
```

### 7. Open a pull request

On GitHub:

1. Open the repository.
2. Select **Pull requests**.
3. Select **New pull request**.
4. Set the base branch to `main`.
5. Set the compare branch to the side branch.
6. Review the displayed changes.
7. Add a clear title and description.
8. Select **Create pull request**.

Example:

```text
base:    main
compare: feature/add-creature-command
```

A useful pull request description should explain:

```text
What changed?
Why was it changed?
How was it tested?
Are there any known limitations?
```

Example:

```text
Adds a new /creature slash command.

The command currently responds with a fixed message.

Tested by running the bot locally and invoking /creature in the
development Discord server.
```

### 8. Review and approval

The pull request should be reviewed before it is merged.

A reviewer may:

* approve the changes;
* request changes;
* leave comments or questions;
* identify bugs or missing tests.

When changes are requested, update the same local side branch:

```bash
nvim bot/extensions/creatures.py
git add bot/extensions/creatures.py
git commit -m "Address pull request review"
git push
```

The existing pull request updates automatically after the new commits are pushed.

Do not create a new pull request for every review change.

### 9. Keep the branch up to date

If `main` changes while the pull request is open, update the side branch:

```bash
git switch main
git pull --ff-only origin main
git switch feature/add-creature-command
git merge main
```

If there are conflicts, Git marks the conflicting files. Resolve them manually, then run:

```bash
git add .
git commit
git push
```

For this project, merging `main` into the feature branch is preferred over rewriting shared branch history.

Avoid using force-push unless you understand the consequences.

### 10. Merge the pull request

After the required review and automated checks pass, merge the pull request through GitHub.

Depending on the repository settings, GitHub may provide:

* **Merge commit**
* **Squash and merge**
* **Rebase and merge**

For small feature branches, **Squash and merge** is usually the simplest option because it creates one clean commit on `main`.

Do not merge when:

* required checks are failing;
* requested changes are unresolved;
* the branch has unresolved conflicts;
* the reviewer has not approved the changes.

### 11. Delete the completed branch

After the pull request has been merged, delete the remote branch using GitHub's **Delete branch** button.

Then clean up the local branch:

```bash
git switch main
git pull --ff-only origin main
git branch -d feature/add-creature-command
```

The `-d` option refuses to delete a branch that Git does not consider merged.

### Complete example

```bash
# Update main.
git switch main
git pull --ff-only origin main

# Create a side branch.
git switch -c feature/add-creature-command

# Edit the project.
nvim bot/extensions/creatures.py

# Inspect and commit the changes.
git status
git diff
git add bot/extensions/creatures.py bot/main.py
git commit -m "Add creature command"

# Push the side branch.
git push -u origin feature/add-creature-command
```

Then open a pull request on GitHub:

```text
feature/add-creature-command → main
```

After the pull request is approved and merged:

```bash
git switch main
git pull --ff-only origin main
git branch -d feature/add-creature-command
```

## Creating your own development bot on Windows

Each developer should create a separate Discord bot application for local development and connect it to the existing **Vrevel-Labs** Discord server.

Do not use the production bot token on a development computer. A separate development bot prevents unfinished code, command changes, and crashes from affecting the production bot.

The setup is:

```text
production Discord application
    ↓
production bot
    ↓
production Discord server

developer Discord application
    ↓
developer bot
    ↓
Vrevel-Labs development server
```

## 1. Create a Discord application

Open the Discord Developer Portal and select:

```text
New Application
```

Give the application a recognizable name that identifies both the project and the developer.

Examples:

```text
vrevel-creature-bot-dev-maups
vrevel-creature-bot-dev-vikk
```

Each developer should use their own Discord application and bot token.

Do not reuse the production Discord application.

Just like the production bot on the server needs a `.env` a dev bot needs the following `.env` file in the project root **THAT SHOULD NOT BE COMMITED EVER!**

This template can be copied from .env.example, the .env is ingored by .gitignore, do never change that!
```env
# Copy this file to .env on the Raspberry Pi. Never commit the real token.
DISCORD_TOKEN=replace-me

# Optional: your test Discord server ID. Slash commands appear there quickly.
# Remove this variable to register commands globally instead.
DISCORD_GUILD_ID=123456789012345678

LOG_LEVEL=INFO
```

## 2. Obtain the development bot token

Open the application and select:

```text
Bot
```

Use **Reset Token** or **Copy Token** to obtain the bot token.

The token authenticates the bot and must be treated like a password.

**Never, NEVER DO THE FOLLOWING**:

* commit the token to Git;
* paste it into the source code;
* send it in Discord;
* include it in screenshots;
* reuse the production token for development.

If a token is exposed, reset it immediately in the Discord Developer Portal.

The current bot uses only the default Discord intents. Do not enable privileged intents unless a future feature explicitly requires them.

## 3. Install the development bot in Vrevel-Labs

In the Discord Developer Portal, open:

```text
Installation
```

Configure a Discord-provided installation link for a server installation.

Select these scopes:

```text
bot
applications.commands
```

Grant only the permissions required by the bot. For the current commands, these permissions are sufficient:

```text
View Channels
Send Messages
```

Copy the installation link and open it in a browser.

Select the existing development server:

```text
Vrevel-Labs
```

You must have permission to add applications to the server. Contact a Vrevel-Labs administrator if the server does not appear in the list.

The bot will initially appear offline because the Python program is not running yet.

## 4. Obtain the Vrevel-Labs server ID

In the Discord desktop application:

1. Open **User Settings**.
2. Open **Advanced**.
3. Enable **Developer Mode**.
4. Right-click the **Vrevel-Labs** server icon.
5. Select **Copy Server ID**.

The copied numeric value is the development `DISCORD_GUILD_ID`.

Example:

```text
123456789012345678
```

All developers testing inside Vrevel-Labs use the same server ID, but each developer uses their own bot token.

The local configuration therefore has this structure:

```text
DISCORD_TOKEN     = your personal development bot token
DISCORD_GUILD_ID  = the shared Vrevel-Labs server ID
```

Do not use the production server ID for local development.

## 5. Install Python and Git

Install current versions of:

* Python 3;
* Git for Windows;
* Neovim, or another editor.

Verify the installations in PowerShell:

```powershell
py --version
git --version
nvim --version
```

## 6. Clone the repository

Open PowerShell and run:

```powershell
git clone https://github.com/OWNER/vrevel-creature-bot.git
Set-Location vrevel-creature-bot
```

Replace `OWNER` with the GitHub username or organization that owns the repository.

## 7. Create a Python virtual environment

Create a project-local virtual environment:

```powershell
py -3 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

The PowerShell prompt should now begin with:

```text
(.venv)
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents `Activate.ps1` from running, activation is optional. Use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Do not commit the `.venv` directory. It should be included in `.gitignore`.

## 8. Configure the development environment

There are two supported ways to provide the development credentials.

### Option A: PowerShell environment variables

Set the variables in the current PowerShell session:

```powershell
$env:DISCORD_TOKEN = "your-personal-development-bot-token"
$env:DISCORD_GUILD_ID = "the-vrevel-labs-server-id"
$env:LOG_LEVEL = "DEBUG"
```

These variables exist only in the current PowerShell process. Closing the terminal removes them.

Run the bot:

```powershell
python -m bot.main
```

Without virtual-environment activation, use:

```powershell
$env:DISCORD_TOKEN = "your-personal-development-bot-token"
$env:DISCORD_GUILD_ID = "the-vrevel-labs-server-id"
$env:LOG_LEVEL = "DEBUG"

.\.venv\Scripts\python.exe -m bot.main
```

### Option B: Docker Desktop and `.env`

Install Docker Desktop, then create a local `.env` file:

```powershell
Copy-Item .env.example .env
nvim .env
```

Add the development credentials:

```dotenv
DISCORD_TOKEN=your-personal-development-bot-token
DISCORD_GUILD_ID=the-vrevel-labs-server-id
LOG_LEVEL=DEBUG
```

Start the bot:

```powershell
docker compose up --build
```

Stop it with:

```text
Ctrl+C
```

Run it in the background with:

```powershell
docker compose up -d --build
```

Inspect the logs:

```powershell
docker compose logs --since=5m -f
```

Stop and remove the development container:

```powershell
docker compose down
```

The `.env` file contains secrets and must never be committed.

Verify that Git ignores it:

```powershell
git status
```

The `.env` file should not appear as an untracked file.

## 9. Test the bot in Vrevel-Labs

After the bot starts, the terminal should report that:

* the extension was loaded;
* commands were synchronized;
* the bot logged in successfully.

Because commands are synchronized to the Vrevel-Labs server ID, the slash commands should become available quickly inside Vrevel-Labs.

Test:

```text
/ping
/about
```

Several development bots may be present in Vrevel-Labs at the same time. Confirm that you are selecting your own bot when testing commands.

Use a distinctive bot name such as:

```text
vrevel-creature-bot-dev-maups
```

This makes it easier to distinguish development bots from each other and from the production bot.

## 10. Stop the local bot

For direct Python execution, press:

```text
Ctrl+C
```

Deactivate the virtual environment:

```powershell
deactivate
```

For Docker execution:

```powershell
docker compose down
```

## Development safety rules

| Rule                                                  | Reason                                                        |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| Use a separate Discord application for each developer | Prevents developers from sharing bot credentials              |
| Use the Vrevel-Labs server for testing                | Keeps development activity out of production                  |
| Use a personal development token                      | Prevents local code from authenticating as the production bot |
| Never commit `.env`                                   | Prevents credential exposure                                  |
| Enable only required permissions                      | Reduces the impact of mistakes                                |
| Use a distinctive bot name                            | Makes concurrent development bots easy to identify            |
| Use `LOG_LEVEL=DEBUG` locally                         | Provides more diagnostic information                          |
| Reset an exposed token immediately                    | Invalidates the compromised credential                        |

A developer's local configuration should therefore use:

```text
DISCORD_TOKEN     = personal development bot token
DISCORD_GUILD_ID  = shared Vrevel-Labs server ID
LOG_LEVEL         = DEBUG
```

The Raspberry Pi continues to use:

```text
DISCORD_TOKEN     = production bot token
DISCORD_GUILD_ID  = production server ID
LOG_LEVEL         = INFO
```


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
merge pull request into main
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

Use a separate branch for every change:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/short-description

# Make changes.

git add .
git commit -m "Describe the change"
git push -u origin feature/short-description
```

Open a pull request from the side branch into `main`.

After the pull request is reviewed, approved, and merged, GitHub updates the `deploy` branch through the deployment workflow. The Pi deploys the change during the next cron run.

