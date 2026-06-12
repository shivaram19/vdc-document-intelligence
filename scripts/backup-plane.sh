#!/bin/bash
# Backup Plane PostgreSQL database
# Run via cron: 0 2 * * 0 /path/to/scripts/backup-plane.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/plane_backup_$DATE.sql.gz"

mkdir -p "$BACKUP_DIR"

cd "$PROJECT_DIR/plane/plane-app"

# Get PostgreSQL password from .env
PG_PASS=$(grep '^POSTGRES_PASSWORD=' .env | cut -d= -f2)

# Run pg_dump inside the Plane Postgres container
docker compose exec -T -e PGPASSWORD="$PG_PASS" plane-db pg_dump \
  -U plane \
  -d plane \
  --no-owner \
  --no-acl \
  | gzip > "$BACKUP_FILE"

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/plane_backup_*.sql.gz | tail -n +11 | xargs -r rm

echo "Plane backup completed: $BACKUP_FILE"
