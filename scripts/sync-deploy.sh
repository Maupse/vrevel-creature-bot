#!/usr/bin/env bash
set -Eeuo pipefail

# Cron uses a minimal PATH. Include the usual locations explicitly.
export PATH="/usr/local/bin:/usr/bin:/bin"

readonly APP_DIR="${HOME}/apps/vrevel-creature-bot"
readonly DEPLOY_BRANCH="deploy"
readonly LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/vrevel-creature-bot-deploy.lock"

# Prevent two cron invocations from deploying at the same time.
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    exit 0
fi

cd "${APP_DIR}"

git fetch --quiet origin "${DEPLOY_BRANCH}"

local_commit="$(git rev-parse HEAD)"
remote_commit="$(git rev-parse "origin/${DEPLOY_BRANCH}")"

container_is_running() {
    docker compose ps --status running --services 2>/dev/null \
        | grep --fixed-strings --line-regexp --quiet bot
}

# Stay silent during normal unchanged checks so the cron log does not grow.
if [[ "${local_commit}" == "${remote_commit}" ]] && container_is_running; then
    exit 0
fi

if [[ "${local_commit}" != "${remote_commit}" ]]; then
    echo "Deploying commit ${remote_commit}..."
    git reset --hard "origin/${DEPLOY_BRANCH}"
else
    echo "Commit is current, but the bot is not running; starting it..."
fi

test -f .env || {
    echo "Missing ${APP_DIR}/.env"
    exit 1
}

docker compose up -d --build --remove-orphans
docker compose ps

echo "Deployment completed at $(date --iso-8601=seconds)"
