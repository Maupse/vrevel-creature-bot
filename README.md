# vrevel-creature-bot

Minimal `discord.py` bot deployed to a Raspberry Pi with Docker Compose.

Deployment model:

```text
push to main
      |
      v
GitHub Actions validates Python and Docker
      |
      v
validated commit is force-pushed to deploy
      |
      v
Pi cron job fetches deploy
      |
      v
docker compose up -d --build
```

The Pi does not need to accept connections from GitHub. It pulls from GitHub using its normal outbound network connection, so manual SSH may remain behind Cloudflare Tunnel.

## Structure

```text
vrevel-creature-bot/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── bot/
│   ├── __init__.py
│   └── main.py
├── scripts/
│   └── sync-deploy.sh
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── README.md
└── requirements.txt
```

## 1. Create and push the GitHub repository

Create an empty GitHub repository named `vrevel-creature-bot`, then run locally:

```bash
git init -b main
git add .
git commit -m "Initial vrevel-creature bot"
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/vrevel-creature-bot.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

The first successful workflow run creates the `deploy` branch. Do not manually edit that branch. If branch protection is enabled for `deploy`, it must permit this workflow's force-push, or the publish step will fail.

## 2. Clone the deploy branch on the Pi

After the first workflow succeeds:

```bash
mkdir -p ~/apps
git clone --branch deploy \
  git@github.com:YOUR_GITHUB_USERNAME/vrevel-creature-bot.git \
  ~/apps/vrevel-creature-bot

cd ~/apps/vrevel-creature-bot
```

For a private repository, configure a read-only GitHub deploy key on the Pi before cloning.

## 3. Create the Pi-only environment file

```bash
cd ~/apps/vrevel-creature-bot
cp .env.example .env
nvim .env
chmod 600 .env
```

Set:

```dotenv
DISCORD_TOKEN=your-real-token
DISCORD_GUILD_ID=your-numeric-server-id
LOG_LEVEL=INFO
```

## 4. Test the first deployment

```bash
cd ~/apps/vrevel-creature-bot
./scripts/sync-deploy.sh
```

Run the deployment script. It starts the container even when the Git commit is already current:

```bash
./scripts/sync-deploy.sh
docker compose logs -f --tail=100
```

## 5. Install the cron job

Install and enable cron if necessary:

```bash
sudo apt-get update
sudo apt-get install -y cron util-linux
sudo systemctl enable --now cron
```

Ensure the deployment script is executable:

```bash
chmod +x ~/apps/vrevel-creature-bot/scripts/sync-deploy.sh
```

Edit the `ubuntu` user's crontab:

```bash
crontab -e
```

Add this line to check every two minutes:

```cron
*/2 * * * * /home/ubuntu/apps/vrevel-creature-bot/scripts/sync-deploy.sh >> /home/ubuntu/vrevel-creature-bot-deploy.log 2>&1
```

Verify:

```bash
crontab -l
```

Watch deployment output:

```bash
tail -f ~/vrevel-creature-bot-deploy.log
```

The script uses `flock`, so overlapping cron executions exit instead of running two Docker builds concurrently.

## Routine deployment

On your development computer:

```bash
git add .
git commit -m "Describe the change"
git push
```

After GitHub validates the commit and updates `deploy`, the Pi deploys it within approximately two minutes.

## Useful Pi commands

```bash
cd ~/apps/vrevel-creature-bot

docker compose ps
docker compose logs -f --tail=100
docker compose restart
./scripts/sync-deploy.sh
```
