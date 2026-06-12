#!/bin/bash
# Backup Postiz PostgreSQL database
# Run via cron: 0 2 * * 0 /path/to/scripts/backup-postiz.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/postiz_backup_$DATE.sql.gz"

mkdir -p "$BACKUP_DIR"

cd "$PROJECT_DIR/postiz"

# Run pg_dump inside the Postiz Postgres container
docker compose exec -T postiz-postgres pg_dump \
  -U postiz-user \
  -d postiz-db-local \
  --no-owner \
  --no-acl \
  | gzip > "$BACKUP_FILE"

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/postiz_backup_*.sql.gz | tail -n +11 | xargs -r rm

echo "Postiz backup completed: $BACKUP_FILE"
