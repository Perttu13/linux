
#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?Usage: deploy.sh SOURCE_DIR COMMIT_SHA}"
COMMIT_SHA="${2:?Usage: deploy.sh SOURCE_DIR COMMIT_SHA}"

if [[ ! "$COMMIT_SHA" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Invalid Git commit SHA"
    exit 1
fi

if [[ ! -f "$SOURCE_DIR/app.py" ]]; then
    echo "Application source not found"
    exit 1
fi

echo "Deploying commit: $COMMIT_SHA"

rsync -a --chown=week5:week5 \
    --exclude='venv/' \
    --exclude='deploy.env' \
    "$SOURCE_DIR/" /opt/week5/

runuser -u week5 -- \
    /opt/week5/venv/bin/pip install -r /opt/week5/requirements.txt

install -o root -g root -m 644 \
    "$SOURCE_DIR/nginx-week5.conf" \
    /etc/nginx/snippets/week5.conf

install -o root -g root -m 644 \
    "$SOURCE_DIR/week5.service" \
    /etc/systemd/system/week5.service

printf 'GIT_SHA=%s\n' "$COMMIT_SHA" > /opt/week5/deploy.env
chown root:week5 /opt/week5/deploy.env
chmod 640 /opt/week5/deploy.env

systemctl daemon-reload

nginx -t
systemctl reload nginx

systemctl restart week5

for attempt in {1..15}; do
    if curl -fsS http://127.0.0.1:5002/health \
        | grep -Fq "\"commit\":\"$COMMIT_SHA\""; then
        echo "Deployment successful: $COMMIT_SHA"
        exit 0
    fi
    sleep 2
done

echo "Health check failed"
exit 1
