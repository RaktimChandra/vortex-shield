#!/bin/bash
# VORTEX Shield 2.0 - Database Restore Script

# Configuration
BACKUP_DIR="/var/backups/vortex-shield"
DB_NAME="vortex_shield"
DB_USER="postgres"

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -lht $BACKUP_DIR/*.sql.gz | head -10
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirm restore
read -p "This will restore the database from $BACKUP_FILE. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Drop existing database and recreate
echo "Dropping existing database..."
dropdb -U $DB_USER $DB_NAME
createdb -U $DB_USER $DB_NAME

# Restore from backup
echo "Restoring from backup..."
gunzip -c $BACKUP_FILE | psql -U $DB_USER -d $DB_NAME

if [ $? -eq 0 ]; then
    echo "Restore completed successfully!"
else
    echo "Restore failed!"
    exit 1
fi
