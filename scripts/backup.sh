#!/bin/bash
# VORTEX Shield 2.0 - Database Backup Script

# Configuration
BACKUP_DIR="/var/backups/vortex-shield"
DB_NAME="vortex_shield"
DB_USER="postgres"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/vortex_shield_${TIMESTAMP}.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting backup at $(date)"
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi

# Remove old backups
echo "Removing backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "vortex_shield_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List recent backups
echo "Recent backups:"
ls -lht $BACKUP_DIR | head -10

echo "Backup completed at $(date)"
