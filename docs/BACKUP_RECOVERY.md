# Backup and Recovery Guide / 백업 및 복구 가이드

## Table of Contents / 목차
1. [Overview / 개요](#overview--개요)
2. [Backup Strategy / 백업 전략](#backup-strategy--백업-전략)
3. [Automated Backups / 자동 백업](#automated-backups--자동-백업)
4. [Manual Backup Procedures / 수동 백업 절차](#manual-backup-procedures--수동-백업-절차)
5. [Recovery Procedures / 복구 절차](#recovery-procedures--복구-절차)
6. [Disaster Recovery / 재해 복구](#disaster-recovery--재해-복구)
7. [Testing and Validation / 테스트 및 검증](#testing-and-validation--테스트-및-검증)
8. [Backup Monitoring / 백업 모니터링](#backup-monitoring--백업-모니터링)
9. [Recovery Time Objectives / 복구 시간 목표](#recovery-time-objectives--복구-시간-목표)
10. [Best Practices / 모범 사례](#best-practices--모범-사례)

## Overview / 개요

### Backup Philosophy / 백업 철학
- **3-2-1 Rule**: 3 copies, 2 different media, 1 offsite
- **Regular Testing**: Monthly recovery drills
- **Automation First**: Minimize human error
- **Version Control**: Git as primary backup

### What to Backup / 백업 대상
```yaml
Critical Data:
  - /data/settings.json         # System configuration
  - /data/sites.json           # Site definitions
  - /data/scraped/*.json       # Historical news data
  - /data/history/*.json       # WhatsApp logs
  - Environment variables       # API keys and secrets

Code and Configuration:
  - Source code (via Git)
  - GitHub Actions workflows
  - Vercel configuration
  - Documentation

Infrastructure:
  - DNS settings
  - SSL certificates
  - Domain configuration
```

## Backup Strategy / 백업 전략

### 1. Tiered Backup Approach / 계층적 백업 접근
```
Tier 1: Real-time (Git)
  ├── Every commit
  ├── Immediate sync
  └── Version history

Tier 2: Daily Automated
  ├── GitHub Actions
  ├── Compressed archives
  └── 30-day retention

Tier 3: Weekly Snapshots
  ├── Full system backup
  ├── External storage
  └── 90-day retention

Tier 4: Monthly Archives
  ├── Long-term storage
  ├── Encrypted archives
  └── 1-year retention
```

### 2. Backup Schedule / 백업 일정
```yaml
Real-time:
  - Git commits (continuous)
  - Database replication (if applicable)

Daily:
  - 02:00 KST: Incremental backup
  - 14:00 KST: Settings backup

Weekly:
  - Sunday 03:00 KST: Full backup
  - Wednesday 03:00 KST: Verification test

Monthly:
  - 1st day 04:00 KST: Archive creation
  - 15th day: Recovery drill
```

## Automated Backups / 자동 백업

### 1. GitHub Actions Backup Workflow / GitHub Actions 백업 워크플로우
```yaml
# .github/workflows/backup.yml
name: Automated Backup

on:
  schedule:
    - cron: '0 17 * * *'  # Daily at 02:00 KST (17:00 UTC)
  workflow_dispatch:      # Manual trigger

jobs:
  backup:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Get full history
      
      - name: Set up backup timestamp
        run: |
          echo "BACKUP_DATE=$(date +%Y%m%d)" >> $GITHUB_ENV
          echo "BACKUP_TIME=$(date +%Y%m%d_%H%M%S)" >> $GITHUB_ENV
      
      - name: Create backup directory
        run: mkdir -p backups/${{ env.BACKUP_DATE }}
      
      - name: Backup data files
        run: |
          # Create compressed archive
          tar -czf backups/${{ env.BACKUP_DATE }}/data_${{ env.BACKUP_TIME }}.tar.gz \
            data/settings.json \
            data/sites.json \
            data/scraped/ \
            data/history/
          
          # Create checksums
          sha256sum backups/${{ env.BACKUP_DATE }}/*.tar.gz > \
            backups/${{ env.BACKUP_DATE }}/checksums.sha256
      
      - name: Backup environment configuration
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Export repository secrets (metadata only)
          gh api repos/${{ github.repository }}/actions/secrets | \
            jq '.secrets[] | {name: .name, created_at: .created_at}' > \
            backups/${{ env.BACKUP_DATE }}/secrets_metadata.json
          
          # Export workflow configurations
          cp -r .github/workflows backups/${{ env.BACKUP_DATE }}/
      
      - name: Create backup manifest
        run: |
          cat > backups/${{ env.BACKUP_DATE }}/manifest.json << EOF
          {
            "timestamp": "${{ env.BACKUP_TIME }}",
            "commit": "${{ github.sha }}",
            "files": $(find backups/${{ env.BACKUP_DATE }} -type f -name "*.tar.gz" | wc -l),
            "size": "$(du -sh backups/${{ env.BACKUP_DATE }} | cut -f1)",
            "type": "automated_daily"
          }
          EOF
      
      - name: Upload to backup branch
        run: |
          git config user.name "Backup Bot"
          git config user.email "backup@bot.com"
          
          # Create or switch to backup branch
          git checkout -B backups
          
          # Add backup files
          git add backups/
          git commit -m "Automated backup: ${{ env.BACKUP_TIME }}"
          
          # Push to backup branch
          git push origin backups --force
      
      - name: Upload to external storage
        if: secrets.BACKUP_S3_BUCKET != ''
        uses: jakejarvis/s3-sync-action@master
        with:
          args: --acl private --follow-symlinks
        env:
          AWS_S3_BUCKET: ${{ secrets.BACKUP_S3_BUCKET }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          SOURCE_DIR: backups/${{ env.BACKUP_DATE }}
          DEST_DIR: singapore-news-scraper/${{ env.BACKUP_DATE }}
      
      - name: Clean old backups
        run: |
          # Remove backups older than 30 days
          find backups -type d -mtime +30 -exec rm -rf {} + || true
          
          # Commit cleanup
          git add backups/
          git commit -m "Cleanup: Remove old backups" || true
          git push origin backups
      
      - name: Send notification
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Backup Status: ${{ job.status }}
            Date: ${{ env.BACKUP_TIME }}
            Type: Automated Daily
```

### 2. Incremental Backup Script / 증분 백업 스크립트
```python
#!/usr/bin/env python3
# scripts/incremental_backup.py

import os
import json
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

class IncrementalBackup:
    def __init__(self, source_dir='data', backup_dir='backups'):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.state_file = self.backup_dir / '.backup_state.json'
        self.backup_dir.mkdir(exist_ok=True)
        
    def load_state(self):
        """Load previous backup state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_state(self, state):
        """Save current backup state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def calculate_checksum(self, filepath):
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def find_changed_files(self, state):
        """Find files that have changed since last backup"""
        changed_files = []
        current_state = {}
        
        for file_path in self.source_dir.rglob('*.json'):
            relative_path = str(file_path.relative_to(self.source_dir))
            checksum = self.calculate_checksum(file_path)
            current_state[relative_path] = {
                'checksum': checksum,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            }
            
            # Check if file is new or changed
            if relative_path not in state or state[relative_path]['checksum'] != checksum:
                changed_files.append(file_path)
        
        return changed_files, current_state
    
    def create_incremental_backup(self):
        """Create incremental backup of changed files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'incremental_{timestamp}'
        
        # Load previous state
        state = self.load_state()
        
        # Find changed files
        changed_files, current_state = self.find_changed_files(state)
        
        if not changed_files:
            print("No files have changed since last backup")
            return None
        
        print(f"Found {len(changed_files)} changed files")
        
        # Create backup directory
        backup_path.mkdir(parents=True)
        
        # Copy changed files
        for file_path in changed_files:
            relative_path = file_path.relative_to(self.source_dir)
            dest_path = backup_path / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            print(f"Backed up: {relative_path}")
        
        # Create backup metadata
        metadata = {
            'timestamp': timestamp,
            'type': 'incremental',
            'files_count': len(changed_files),
            'files': [str(f.relative_to(self.source_dir)) for f in changed_files],
            'total_size': sum(f.stat().st_size for f in changed_files)
        }
        
        with open(backup_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Compress backup
        archive_name = f'{backup_path}.tar.gz'
        subprocess.run([
            'tar', '-czf', archive_name, 
            '-C', str(self.backup_dir),
            backup_path.name
        ])
        
        # Remove uncompressed directory
        shutil.rmtree(backup_path)
        
        # Save new state
        self.save_state(current_state)
        
        print(f"Incremental backup created: {archive_name}")
        return archive_name

# Run incremental backup
if __name__ == '__main__':
    backup = IncrementalBackup()
    backup.create_incremental_backup()
```

### 3. Database Backup (Future) / 데이터베이스 백업 (향후)
```bash
#!/bin/bash
# scripts/backup_database.sh

# Database backup script (for future database implementation)
set -e

# Configuration
DB_NAME="singapore_news"
BACKUP_DIR="/backups/database"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Perform backup
echo "Starting database backup..."

# PostgreSQL example
pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > $BACKUP_DIR/db_${TIMESTAMP}.sql.gz

# MongoDB example
# mongodump --uri=$MONGO_URI --archive=$BACKUP_DIR/db_${TIMESTAMP}.archive --gzip

# Create checksum
sha256sum $BACKUP_DIR/db_${TIMESTAMP}.* > $BACKUP_DIR/db_${TIMESTAMP}.sha256

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/db_${TIMESTAMP}.* s3://$BACKUP_BUCKET/database/

# Clean old backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Database backup completed: db_${TIMESTAMP}"
```

## Manual Backup Procedures / 수동 백업 절차

### 1. Emergency Backup Script / 긴급 백업 스크립트
```bash
#!/bin/bash
# scripts/emergency_backup.sh

echo "=== Emergency Backup Procedure ==="
echo "Starting at: $(date)"

# Set variables
BACKUP_ROOT="emergency_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_ROOT

# 1. Backup all data files
echo "1. Backing up data files..."
cp -r data/ $BACKUP_ROOT/
echo "   ✓ Data files copied"

# 2. Export Git information
echo "2. Exporting Git information..."
git log --oneline -n 100 > $BACKUP_ROOT/git_history.txt
git status > $BACKUP_ROOT/git_status.txt
git remote -v > $BACKUP_ROOT/git_remotes.txt
echo "   ✓ Git information exported"

# 3. Export environment information
echo "3. Exporting environment..."
printenv | grep -E "GITHUB_|VERCEL_" | sed 's/=.*/=***/' > $BACKUP_ROOT/env_vars.txt
echo "   ✓ Environment exported (sanitized)"

# 4. Create system snapshot
echo "4. Creating system snapshot..."
cat > $BACKUP_ROOT/system_info.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "node_version": "$(node --version)",
  "npm_version": "$(npm --version)",
  "python_version": "$(python --version)",
  "git_commit": "$(git rev-parse HEAD)",
  "git_branch": "$(git branch --show-current)"
}
EOF
echo "   ✓ System snapshot created"

# 5. Create compressed archive
echo "5. Creating compressed archive..."
tar -czf ${BACKUP_ROOT}.tar.gz $BACKUP_ROOT/
echo "   ✓ Archive created: ${BACKUP_ROOT}.tar.gz"

# 6. Calculate checksum
echo "6. Calculating checksum..."
sha256sum ${BACKUP_ROOT}.tar.gz > ${BACKUP_ROOT}.sha256
echo "   ✓ Checksum: $(cat ${BACKUP_ROOT}.sha256)"

# 7. Clean up
rm -rf $BACKUP_ROOT/

echo ""
echo "=== Emergency Backup Complete ==="
echo "File: ${BACKUP_ROOT}.tar.gz"
echo "Size: $(du -h ${BACKUP_ROOT}.tar.gz | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Upload to secure location"
echo "2. Verify checksum after transfer"
echo "3. Test restoration on separate system"
```

### 2. Selective Backup / 선택적 백업
```python
#!/usr/bin/env python3
# scripts/selective_backup.py

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

class SelectiveBackup:
    def __init__(self):
        self.backup_configs = {
            'minimal': {
                'files': ['data/settings.json', 'data/sites.json'],
                'description': 'Essential configuration only'
            },
            'recent': {
                'files': ['data/settings.json', 'data/sites.json'],
                'dirs': [('data/scraped', 7)],  # Last 7 days
                'description': 'Configuration + recent data'
            },
            'full': {
                'files': ['data/settings.json', 'data/sites.json'],
                'dirs': [('data/scraped', None), ('data/history', None)],
                'description': 'Complete backup'
            }
        }
    
    def backup(self, backup_type='recent', output_dir='manual_backups'):
        """Perform selective backup"""
        if backup_type not in self.backup_configs:
            raise ValueError(f"Unknown backup type: {backup_type}")
        
        config = self.backup_configs[backup_type]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = Path(output_dir) / f'{backup_type}_{timestamp}'
        backup_path.mkdir(parents=True)
        
        print(f"Starting {backup_type} backup: {config['description']}")
        
        # Backup individual files
        for file_path in config.get('files', []):
            source = Path(file_path)
            if source.exists():
                dest = backup_path / source.name
                shutil.copy2(source, dest)
                print(f"  ✓ Copied {file_path}")
        
        # Backup directories with optional date filtering
        for dir_info in config.get('dirs', []):
            if isinstance(dir_info, tuple):
                dir_path, days_limit = dir_info
            else:
                dir_path, days_limit = dir_info, None
            
            source_dir = Path(dir_path)
            if not source_dir.exists():
                continue
            
            dest_dir = backup_path / source_dir.name
            dest_dir.mkdir(exist_ok=True)
            
            # Copy files with date filtering
            cutoff_date = None
            if days_limit:
                cutoff_date = datetime.now() - timedelta(days=days_limit)
            
            file_count = 0
            for file_path in source_dir.glob('*.json'):
                if cutoff_date:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        continue
                
                shutil.copy2(file_path, dest_dir / file_path.name)
                file_count += 1
            
            print(f"  ✓ Copied {file_count} files from {dir_path}")
        
        # Create backup info
        info = {
            'type': backup_type,
            'timestamp': timestamp,
            'description': config['description'],
            'file_count': sum(1 for _ in backup_path.rglob('*') if _.is_file())
        }
        
        with open(backup_path / 'backup_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        
        # Compress
        archive_path = f'{backup_path}.tar.gz'
        shutil.make_archive(str(backup_path), 'gztar', str(backup_path))
        shutil.rmtree(backup_path)
        
        print(f"\nBackup complete: {archive_path}")
        return archive_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['minimal', 'recent', 'full'], 
                       default='recent', help='Backup type')
    parser.add_argument('--output', default='manual_backups', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    backup = SelectiveBackup()
    backup.backup(args.type, args.output)
```

## Recovery Procedures / 복구 절차

### 1. Quick Recovery Script / 빠른 복구 스크립트
```bash
#!/bin/bash
# scripts/quick_recovery.sh

echo "=== Quick Recovery Procedure ==="

# Check if backup file provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Verify checksum if available
CHECKSUM_FILE="${BACKUP_FILE%.tar.gz}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    echo "Verifying checksum..."
    if sha256sum -c "$CHECKSUM_FILE"; then
        echo "✓ Checksum verified"
    else
        echo "✗ Checksum verification failed!"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Create recovery directory
RECOVERY_DIR="recovery_$(date +%Y%m%d_%H%M%S)"
mkdir -p $RECOVERY_DIR

# Extract backup
echo "Extracting backup..."
tar -xzf $BACKUP_FILE -C $RECOVERY_DIR
echo "✓ Backup extracted to $RECOVERY_DIR"

# Find the actual backup directory
BACKUP_DIR=$(find $RECOVERY_DIR -mindepth 1 -maxdepth 1 -type d | head -1)

# Backup current data
echo "Backing up current data..."
if [ -d "data" ]; then
    mv data data.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Current data backed up"
fi

# Restore data
echo "Restoring data..."
if [ -d "$BACKUP_DIR/data" ]; then
    cp -r $BACKUP_DIR/data .
    echo "✓ Data restored"
else
    echo "✗ No data directory found in backup"
fi

# Restore specific files
for file in settings.json sites.json; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        cp $BACKUP_DIR/$file data/
        echo "✓ Restored $file"
    fi
done

# Clean up
rm -rf $RECOVERY_DIR

echo ""
echo "=== Recovery Complete ==="
echo "Next steps:"
echo "1. Verify data integrity"
echo "2. Restart services"
echo "3. Test functionality"
```

### 2. Granular Recovery / 세분화된 복구
```python
#!/usr/bin/env python3
# scripts/granular_recovery.py

import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime
import argparse

class GranularRecovery:
    def __init__(self, backup_file):
        self.backup_file = Path(backup_file)
        self.temp_dir = Path(f'temp_recovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
    def extract_backup(self):
        """Extract backup to temporary directory"""
        print(f"Extracting {self.backup_file}...")
        self.temp_dir.mkdir()
        
        with tarfile.open(self.backup_file, 'r:gz') as tar:
            tar.extractall(self.temp_dir)
        
        # Find actual backup directory
        dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
        if dirs:
            self.backup_root = dirs[0]
        else:
            self.backup_root = self.temp_dir
            
        print(f"✓ Extracted to {self.backup_root}")
    
    def list_contents(self):
        """List backup contents"""
        print("\nBackup Contents:")
        print("=" * 50)
        
        for item in sorted(self.backup_root.rglob('*')):
            if item.is_file():
                relative_path = item.relative_to(self.backup_root)
                size = item.stat().st_size
                print(f"  {relative_path} ({size:,} bytes)")
    
    def recover_file(self, file_path, destination=None):
        """Recover specific file"""
        source = self.backup_root / file_path
        
        if not source.exists():
            print(f"✗ File not found in backup: {file_path}")
            return False
        
        if destination is None:
            destination = Path(file_path)
        else:
            destination = Path(destination)
        
        # Backup existing file
        if destination.exists():
            backup_name = f"{destination}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(str(destination), backup_name)
            print(f"  → Existing file backed up to: {backup_name}")
        
        # Ensure directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source, destination)
        print(f"✓ Recovered: {file_path} → {destination}")
        return True
    
    def recover_directory(self, dir_path, destination=None):
        """Recover entire directory"""
        source = self.backup_root / dir_path
        
        if not source.exists():
            print(f"✗ Directory not found in backup: {dir_path}")
            return False
        
        if destination is None:
            destination = Path(dir_path)
        else:
            destination = Path(destination)
        
        # Backup existing directory
        if destination.exists():
            backup_name = f"{destination}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(str(destination), backup_name)
            print(f"  → Existing directory backed up to: {backup_name}")
        
        # Copy directory
        shutil.copytree(source, destination)
        print(f"✓ Recovered directory: {dir_path} → {destination}")
        return True
    
    def recover_by_pattern(self, pattern, destination_dir='.'):
        """Recover files matching pattern"""
        destination_dir = Path(destination_dir)
        recovered = 0
        
        for file_path in self.backup_root.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.backup_root)
                dest = destination_dir / relative_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                recovered += 1
                print(f"  ✓ {relative_path}")
        
        print(f"\n✓ Recovered {recovered} files matching '{pattern}'")
        return recovered
    
    def cleanup(self):
        """Remove temporary files"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("✓ Cleaned up temporary files")

def main():
    parser = argparse.ArgumentParser(description='Granular backup recovery')
    parser.add_argument('backup_file', help='Backup archive file')
    parser.add_argument('--list', action='store_true', help='List backup contents')
    parser.add_argument('--file', help='Recover specific file')
    parser.add_argument('--dir', help='Recover specific directory')
    parser.add_argument('--pattern', help='Recover files matching pattern')
    parser.add_argument('--dest', help='Destination path')
    
    args = parser.parse_args()
    
    recovery = GranularRecovery(args.backup_file)
    
    try:
        recovery.extract_backup()
        
        if args.list:
            recovery.list_contents()
        elif args.file:
            recovery.recover_file(args.file, args.dest)
        elif args.dir:
            recovery.recover_directory(args.dir, args.dest)
        elif args.pattern:
            recovery.recover_by_pattern(args.pattern, args.dest or '.')
        else:
            recovery.list_contents()
            print("\nUse --file, --dir, or --pattern to recover specific items")
    
    finally:
        recovery.cleanup()

if __name__ == '__main__':
    main()
```

### 3. Point-in-Time Recovery / 시점 복구
```bash
#!/bin/bash
# scripts/point_in_time_recovery.sh

echo "=== Point-in-Time Recovery ==="

# Get target date/time
read -p "Enter target date (YYYY-MM-DD): " TARGET_DATE
read -p "Enter target time (HH:MM): " TARGET_TIME

# Convert to timestamp
TARGET_TIMESTAMP=$(date -d "$TARGET_DATE $TARGET_TIME" +%s)

echo "Searching for backups near $TARGET_DATE $TARGET_TIME..."

# Find closest backup
CLOSEST_BACKUP=""
CLOSEST_DIFF=999999999

for backup in backups/*.tar.gz; do
    # Extract timestamp from filename
    BACKUP_DATE=$(basename $backup | grep -oE '[0-9]{8}_[0-9]{6}')
    
    if [ -n "$BACKUP_DATE" ]; then
        # Convert to timestamp
        BACKUP_TS=$(date -d "${BACKUP_DATE:0:8} ${BACKUP_DATE:9:2}:${BACKUP_DATE:11:2}:${BACKUP_DATE:13:2}" +%s)
        
        # Calculate difference
        DIFF=$((TARGET_TIMESTAMP - BACKUP_TS))
        ABS_DIFF=${DIFF#-}  # Absolute value
        
        if [ $ABS_DIFF -lt $CLOSEST_DIFF ]; then
            CLOSEST_DIFF=$ABS_DIFF
            CLOSEST_BACKUP=$backup
        fi
    fi
done

if [ -z "$CLOSEST_BACKUP" ]; then
    echo "No backups found"
    exit 1
fi

echo "Found closest backup: $CLOSEST_BACKUP"
echo "Time difference: $((CLOSEST_DIFF / 60)) minutes"

read -p "Proceed with recovery? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./scripts/quick_recovery.sh "$CLOSEST_BACKUP"
fi
```

## Disaster Recovery / 재해 복구

### 1. Complete System Recovery / 전체 시스템 복구
```bash
#!/bin/bash
# scripts/disaster_recovery.sh

echo "=== Disaster Recovery Procedure ==="
echo "This will rebuild the entire system from scratch"
echo ""

# Step 1: Clone repository
echo "Step 1: Cloning repository..."
git clone https://github.com/djyalu/singapore_news_github.git recovery_system
cd recovery_system

# Step 2: Restore from latest backup
echo "Step 2: Restoring from backup..."
LATEST_BACKUP=$(ls -t backups/*.tar.gz 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "Found backup: $LATEST_BACKUP"
    tar -xzf "$LATEST_BACKUP"
else
    echo "No local backup found. Downloading from remote..."
    # Download from S3 or other remote storage
    aws s3 cp s3://backup-bucket/latest.tar.gz ./
    tar -xzf latest.tar.gz
fi

# Step 3: Install dependencies
echo "Step 3: Installing dependencies..."
pip install -r requirements.txt
npm install

# Step 4: Restore environment variables
echo "Step 4: Setting up environment..."
read -p "Enter GITHUB_TOKEN: " GITHUB_TOKEN
read -p "Enter WHATSAPP_API_KEY: " WHATSAPP_API_KEY
read -p "Enter GOOGLE_GEMINI_API_KEY: " GEMINI_KEY

# Create .env file
cat > .env << EOF
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_OWNER=djyalu
GITHUB_REPO=singapore_news_github
WHATSAPP_API_KEY=$WHATSAPP_API_KEY
GOOGLE_GEMINI_API_KEY=$GEMINI_KEY
EOF

# Step 5: Verify configuration
echo "Step 5: Verifying configuration..."
python scripts/validate_config.py

# Step 6: Test core functionality
echo "Step 6: Testing core functionality..."
python scripts/test_scraper.py --quick
python scripts/test_whatsapp.py --dry-run

# Step 7: Deploy
echo "Step 7: Deploying..."
vercel --prod

echo ""
echo "=== Disaster Recovery Complete ==="
echo "Please verify:"
echo "1. GitHub Pages is accessible"
echo "2. Vercel APIs are responding"
echo "3. Scheduled workflows are active"
```

### 2. Disaster Recovery Runbook / 재해 복구 실행서
```markdown
# Disaster Recovery Runbook

## Scenario 1: Complete Data Loss

### Symptoms
- All data files missing or corrupted
- Repository deleted or inaccessible
- No recent backups available

### Recovery Steps
1. **Immediate Actions** (0-15 minutes)
   - [ ] Notify stakeholders
   - [ ] Assess damage scope
   - [ ] Activate recovery team

2. **Data Recovery** (15-60 minutes)
   - [ ] Check Git history: `git reflog`
   - [ ] Check GitHub backup branch
   - [ ] Access external backups (S3/GCS)
   - [ ] Contact GitHub support if needed

3. **System Restoration** (1-2 hours)
   - [ ] Clone repository from fork/backup
   - [ ] Restore latest data backup
   - [ ] Reconfigure environment variables
   - [ ] Test basic functionality

4. **Verification** (30 minutes)
   - [ ] Run integrity checks
   - [ ] Verify all endpoints
   - [ ] Test scraping functionality
   - [ ] Confirm WhatsApp integration

## Scenario 2: Partial System Failure

### Symptoms
- Some services unavailable
- Data inconsistency
- Performance degradation

### Recovery Steps
1. **Diagnosis** (0-10 minutes)
   - [ ] Check service status
   - [ ] Review error logs
   - [ ] Identify affected components

2. **Targeted Recovery** (10-30 minutes)
   - [ ] Restore affected services only
   - [ ] Maintain operational services
   - [ ] Implement temporary workarounds

3. **Validation** (10-20 minutes)
   - [ ] Test restored services
   - [ ] Verify data consistency
   - [ ] Monitor performance

## Scenario 3: Security Breach

### Symptoms
- Unauthorized access detected
- Data tampering suspected
- Credentials compromised

### Recovery Steps
1. **Containment** (0-5 minutes)
   - [ ] Revoke all API keys
   - [ ] Disable compromised accounts
   - [ ] Enable maintenance mode

2. **Investigation** (30-60 minutes)
   - [ ] Review access logs
   - [ ] Identify breach vector
   - [ ] Assess data impact

3. **Recovery** (1-2 hours)
   - [ ] Restore from pre-breach backup
   - [ ] Generate new credentials
   - [ ] Implement additional security
   - [ ] Notify affected users

## Communication Template

### Initial Notification
```
Subject: System Issue Detected - Recovery in Progress

We are currently experiencing [issue description].
Impact: [affected services]
ETA: [estimated recovery time]

We will provide updates every 30 minutes.
```

### Update Template
```
Subject: Recovery Update - [timestamp]

Status: [current status]
Progress: [completed steps]
Next: [upcoming steps]
ETA: [updated estimate]
```

### Resolution Notice
```
Subject: System Recovered - All Services Operational

The issue has been resolved.
Duration: [start time] - [end time]
Impact: [summary of impact]
Actions taken: [brief summary]

Full post-mortem will follow within 48 hours.
```
```

## Testing and Validation / 테스트 및 검증

### 1. Backup Validation Script / 백업 검증 스크립트
```python
#!/usr/bin/env python3
# scripts/validate_backup.py

import json
import tarfile
import tempfile
from pathlib import Path
import hashlib

class BackupValidator:
    def __init__(self, backup_file):
        self.backup_file = Path(backup_file)
        self.validation_results = {
            'file_exists': False,
            'checksum_valid': False,
            'archive_intact': False,
            'files_complete': False,
            'data_valid': False
        }
    
    def validate(self):
        """Run all validation checks"""
        print(f"Validating backup: {self.backup_file}")
        print("=" * 50)
        
        # Check 1: File exists
        self.validation_results['file_exists'] = self.backup_file.exists()
        self._report_check('File exists', self.validation_results['file_exists'])
        
        if not self.validation_results['file_exists']:
            return self.validation_results
        
        # Check 2: Verify checksum
        checksum_file = self.backup_file.with_suffix('.sha256')
        if checksum_file.exists():
            self.validation_results['checksum_valid'] = self._verify_checksum()
            self._report_check('Checksum valid', self.validation_results['checksum_valid'])
        else:
            print("  ⚠ No checksum file found")
        
        # Check 3: Archive integrity
        self.validation_results['archive_intact'] = self._verify_archive()
        self._report_check('Archive intact', self.validation_results['archive_intact'])
        
        if not self.validation_results['archive_intact']:
            return self.validation_results
        
        # Check 4: Required files present
        self.validation_results['files_complete'] = self._verify_files()
        self._report_check('Files complete', self.validation_results['files_complete'])
        
        # Check 5: Data validity
        self.validation_results['data_valid'] = self._verify_data()
        self._report_check('Data valid', self.validation_results['data_valid'])
        
        # Summary
        print("\n" + "=" * 50)
        passed = sum(1 for v in self.validation_results.values() if v)
        total = len(self.validation_results)
        print(f"Validation Result: {passed}/{total} checks passed")
        
        return self.validation_results
    
    def _report_check(self, check_name, passed):
        """Report check result"""
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {check_name}")
    
    def _verify_checksum(self):
        """Verify file checksum"""
        checksum_file = self.backup_file.with_suffix('.sha256')
        
        with open(checksum_file, 'r') as f:
            expected_checksum = f.read().split()[0]
        
        sha256_hash = hashlib.sha256()
        with open(self.backup_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        actual_checksum = sha256_hash.hexdigest()
        return actual_checksum == expected_checksum
    
    def _verify_archive(self):
        """Verify archive can be opened"""
        try:
            with tarfile.open(self.backup_file, 'r:gz') as tar:
                # Check for common issues
                members = tar.getmembers()
                if len(members) == 0:
                    return False
            return True
        except:
            return False
    
    def _verify_files(self):
        """Verify required files are present"""
        required_files = [
            'data/settings.json',
            'data/sites.json'
        ]
        
        try:
            with tarfile.open(self.backup_file, 'r:gz') as tar:
                archive_files = [m.name for m in tar.getmembers()]
                
                for required in required_files:
                    found = any(required in f for f in archive_files)
                    if not found:
                        print(f"    Missing: {required}")
                        return False
            
            return True
        except:
            return False
    
    def _verify_data(self):
        """Verify data files are valid JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract backup
            with tarfile.open(self.backup_file, 'r:gz') as tar:
                tar.extractall(temp_path)
            
            # Find and validate JSON files
            for json_file in temp_path.rglob('*.json'):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    print(f"    Invalid JSON: {json_file.name}")
                    return False
            
            return True

# Run validation
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python validate_backup.py <backup_file>")
        sys.exit(1)
    
    validator = BackupValidator(sys.argv[1])
    results = validator.validate()
    
    # Exit with error if validation failed
    if not all(results.values()):
        sys.exit(1)
```

### 2. Recovery Test Script / 복구 테스트 스크립트
```bash
#!/bin/bash
# scripts/test_recovery.sh

echo "=== Recovery Test Procedure ==="
echo "This will test backup and recovery without affecting production"

# Create test environment
TEST_DIR="recovery_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p $TEST_DIR
cd $TEST_DIR

echo "Test directory: $(pwd)"

# Step 1: Create test data
echo "1. Creating test data..."
mkdir -p data/scraped
cat > data/settings.json << EOF
{
    "test": true,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

cat > data/sites.json << EOF
{
    "sites": [
        {"name": "Test Site", "url": "https://example.com"}
    ]
}
EOF

# Create some dummy scraped files
for i in {1..5}; do
    cat > data/scraped/news_2025012${i}_120000.json << EOF
    {
        "articles": [
            {"title": "Test Article $i", "url": "https://example.com/$i"}
        ]
    }
EOF
done

echo "   ✓ Test data created"

# Step 2: Create backup
echo "2. Creating backup..."
tar -czf test_backup.tar.gz data/
sha256sum test_backup.tar.gz > test_backup.sha256
echo "   ✓ Backup created"

# Step 3: Simulate data loss
echo "3. Simulating data loss..."
rm -rf data/
echo "   ✓ Data removed"

# Step 4: Recover from backup
echo "4. Recovering from backup..."
tar -xzf test_backup.tar.gz
echo "   ✓ Data recovered"

# Step 5: Verify recovery
echo "5. Verifying recovery..."
ERRORS=0

# Check files exist
for file in data/settings.json data/sites.json; do
    if [ ! -f "$file" ]; then
        echo "   ✗ Missing: $file"
        ((ERRORS++))
    fi
done

# Check content integrity
if [ -f "data/settings.json" ]; then
    if grep -q '"test": true' data/settings.json; then
        echo "   ✓ Settings file valid"
    else
        echo "   ✗ Settings file corrupted"
        ((ERRORS++))
    fi
fi

# Count scraped files
SCRAPED_COUNT=$(find data/scraped -name "*.json" 2>/dev/null | wc -l)
if [ $SCRAPED_COUNT -eq 5 ]; then
    echo "   ✓ All scraped files recovered"
else
    echo "   ✗ Expected 5 scraped files, found $SCRAPED_COUNT"
    ((ERRORS++))
fi

# Cleanup
cd ..
rm -rf $TEST_DIR

# Report
echo ""
echo "=== Test Complete ==="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All recovery tests passed"
    exit 0
else
    echo "✗ $ERRORS errors found"
    exit 1
fi
```

## Backup Monitoring / 백업 모니터링

### 1. Backup Status Dashboard / 백업 상태 대시보드
```python
#!/usr/bin/env python3
# scripts/backup_monitor.py

import json
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

class BackupMonitor:
    def __init__(self, backup_dir='backups'):
        self.backup_dir = Path(backup_dir)
        self.alerts = []
        
    def check_backup_health(self):
        """Check overall backup health"""
        print("=== Backup Health Check ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Check 1: Recent backup exists
        latest_backup = self.get_latest_backup()
        if latest_backup:
            age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)
            print(f"Latest backup: {latest_backup.name}")
            print(f"Age: {age.total_seconds() / 3600:.1f} hours")
            
            if age > timedelta(days=1):
                self.alerts.append({
                    'level': 'WARNING',
                    'message': f'No backup in last 24 hours (latest: {age.total_seconds() / 3600:.1f}h old)'
                })
        else:
            self.alerts.append({
                'level': 'CRITICAL',
                'message': 'No backups found!'
            })
        
        # Check 2: Backup size trends
        self.check_backup_sizes()
        
        # Check 3: Backup success rate
        self.check_success_rate()
        
        # Check 4: Storage space
        self.check_storage_space()
        
        # Report alerts
        if self.alerts:
            print("\nAlerts:")
            for alert in self.alerts:
                print(f"  [{alert['level']}] {alert['message']}")
            
            # Send email alerts for critical issues
            critical_alerts = [a for a in self.alerts if a['level'] == 'CRITICAL']
            if critical_alerts:
                self.send_alert_email(critical_alerts)
        else:
            print("\n✓ All checks passed")
    
    def get_latest_backup(self):
        """Get most recent backup file"""
        backups = list(self.backup_dir.glob('*.tar.gz'))
        if not backups:
            return None
        return max(backups, key=lambda f: f.stat().st_mtime)
    
    def check_backup_sizes(self):
        """Check backup size trends"""
        backups = sorted(self.backup_dir.glob('*.tar.gz'), 
                        key=lambda f: f.stat().st_mtime)[-10:]
        
        if len(backups) < 2:
            return
        
        sizes = [b.stat().st_size for b in backups]
        avg_size = sum(sizes) / len(sizes)
        latest_size = sizes[-1]
        
        # Check for significant size changes
        size_change = (latest_size - avg_size) / avg_size * 100
        
        print(f"\nBackup sizes (last {len(backups)}):")
        print(f"  Average: {avg_size / 1024 / 1024:.1f} MB")
        print(f"  Latest: {latest_size / 1024 / 1024:.1f} MB")
        print(f"  Change: {size_change:+.1f}%")
        
        if abs(size_change) > 50:
            self.alerts.append({
                'level': 'WARNING',
                'message': f'Significant backup size change: {size_change:+.1f}%'
            })
    
    def check_success_rate(self):
        """Check backup success rate from logs"""
        log_file = self.backup_dir / '.backup_log.json'
        
        if not log_file.exists():
            return
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        # Get last 30 days of logs
        cutoff = datetime.now() - timedelta(days=30)
        recent_logs = [
            log for log in logs 
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        
        if recent_logs:
            successful = sum(1 for log in recent_logs if log['status'] == 'success')
            success_rate = successful / len(recent_logs) * 100
            
            print(f"\nBackup success rate (30 days):")
            print(f"  Total attempts: {len(recent_logs)}")
            print(f"  Successful: {successful}")
            print(f"  Success rate: {success_rate:.1f}%")
            
            if success_rate < 90:
                self.alerts.append({
                    'level': 'WARNING',
                    'message': f'Low backup success rate: {success_rate:.1f}%'
                })
    
    def check_storage_space(self):
        """Check available storage space"""
        import shutil
        
        stat = shutil.disk_usage(self.backup_dir)
        free_gb = stat.free / 1024 / 1024 / 1024
        used_percent = (stat.used / stat.total) * 100
        
        print(f"\nStorage space:")
        print(f"  Total: {stat.total / 1024 / 1024 / 1024:.1f} GB")
        print(f"  Used: {used_percent:.1f}%")
        print(f"  Free: {free_gb:.1f} GB")
        
        if free_gb < 5:
            self.alerts.append({
                'level': 'CRITICAL',
                'message': f'Low storage space: {free_gb:.1f} GB remaining'
            })
        elif used_percent > 80:
            self.alerts.append({
                'level': 'WARNING',
                'message': f'Storage {used_percent:.1f}% full'
            })
    
    def send_alert_email(self, alerts):
        """Send email notification for critical alerts"""
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender = "backup-monitor@example.com"
        recipients = ["admin@example.com"]
        
        # Compose message
        subject = f"[CRITICAL] Backup System Alert - {len(alerts)} issues"
        body = "Critical backup system alerts:\n\n"
        
        for alert in alerts:
            body += f"- {alert['message']}\n"
        
        body += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        body += f"\nSystem: Singapore News Scraper"
        
        # Send email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, "password")  # Use env variable
                server.send_message(msg)
            print("\n✓ Alert email sent")
        except Exception as e:
            print(f"\n✗ Failed to send alert email: {e}")

if __name__ == '__main__':
    monitor = BackupMonitor()
    monitor.check_backup_health()
```

### 2. Automated Backup Reports / 자동 백업 보고서
```python
#!/usr/bin/env python3
# scripts/backup_report.py

import json
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

class BackupReporter:
    def __init__(self, backup_dir='backups'):
        self.backup_dir = Path(backup_dir)
        
    def generate_report(self, days=30):
        """Generate comprehensive backup report"""
        print(f"Generating backup report for last {days} days...")
        
        # Collect backup data
        backup_data = self.collect_backup_data(days)
        
        # Generate report sections
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'summary': self.generate_summary(backup_data),
            'daily_stats': self.calculate_daily_stats(backup_data),
            'size_analysis': self.analyze_sizes(backup_data),
            'reliability': self.calculate_reliability(backup_data)
        }
        
        # Save report
        report_file = f'backup_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate visualizations
        self.create_charts(backup_data)
        
        print(f"Report saved to: {report_file}")
        return report
    
    def collect_backup_data(self, days):
        """Collect backup metadata"""
        cutoff = datetime.now() - timedelta(days=days)
        backup_data = []
        
        for backup_file in self.backup_dir.glob('*.tar.gz'):
            stat = backup_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            if mtime > cutoff:
                backup_data.append({
                    'filename': backup_file.name,
                    'timestamp': mtime,
                    'size': stat.st_size,
                    'type': self.determine_backup_type(backup_file.name)
                })
        
        return sorted(backup_data, key=lambda x: x['timestamp'])
    
    def determine_backup_type(self, filename):
        """Determine backup type from filename"""
        if 'full' in filename:
            return 'full'
        elif 'incremental' in filename:
            return 'incremental'
        elif 'emergency' in filename:
            return 'emergency'
        else:
            return 'daily'
    
    def generate_summary(self, backup_data):
        """Generate summary statistics"""
        if not backup_data:
            return {'status': 'No backups found'}
        
        total_size = sum(b['size'] for b in backup_data)
        
        return {
            'total_backups': len(backup_data),
            'total_size_gb': round(total_size / 1024 / 1024 / 1024, 2),
            'average_size_mb': round(total_size / len(backup_data) / 1024 / 1024, 2),
            'oldest_backup': backup_data[0]['timestamp'].isoformat(),
            'newest_backup': backup_data[-1]['timestamp'].isoformat(),
            'backup_types': {
                backup_type: sum(1 for b in backup_data if b['type'] == backup_type)
                for backup_type in set(b['type'] for b in backup_data)
            }
        }
    
    def calculate_daily_stats(self, backup_data):
        """Calculate daily backup statistics"""
        daily_stats = {}
        
        for backup in backup_data:
            date = backup['timestamp'].date()
            if date not in daily_stats:
                daily_stats[date] = {
                    'count': 0,
                    'total_size': 0,
                    'types': []
                }
            
            daily_stats[date]['count'] += 1
            daily_stats[date]['total_size'] += backup['size']
            daily_stats[date]['types'].append(backup['type'])
        
        return {
            str(date): {
                'count': stats['count'],
                'total_size_mb': round(stats['total_size'] / 1024 / 1024, 2),
                'types': list(set(stats['types']))
            }
            for date, stats in daily_stats.items()
        }
    
    def analyze_sizes(self, backup_data):
        """Analyze backup size trends"""
        if not backup_data:
            return {}
        
        sizes = [b['size'] for b in backup_data]
        
        return {
            'min_size_mb': round(min(sizes) / 1024 / 1024, 2),
            'max_size_mb': round(max(sizes) / 1024 / 1024, 2),
            'avg_size_mb': round(sum(sizes) / len(sizes) / 1024 / 1024, 2),
            'growth_rate': self.calculate_growth_rate(backup_data)
        }
    
    def calculate_growth_rate(self, backup_data):
        """Calculate average daily growth rate"""
        if len(backup_data) < 2:
            return 0
        
        # Group by date and get daily totals
        daily_sizes = {}
        for backup in backup_data:
            date = backup['timestamp'].date()
            if date not in daily_sizes:
                daily_sizes[date] = 0
            daily_sizes[date] += backup['size']
        
        if len(daily_sizes) < 2:
            return 0
        
        # Calculate average daily growth
        dates = sorted(daily_sizes.keys())
        total_growth = daily_sizes[dates[-1]] - daily_sizes[dates[0]]
        days = (dates[-1] - dates[0]).days
        
        if days > 0:
            daily_growth = total_growth / days
            return round(daily_growth / 1024 / 1024, 2)  # MB per day
        
        return 0
    
    def calculate_reliability(self, backup_data):
        """Calculate backup reliability metrics"""
        # Group by date
        dates_with_backups = set(b['timestamp'].date() for b in backup_data)
        
        # Calculate expected dates (assuming daily backups)
        if backup_data:
            start_date = min(b['timestamp'].date() for b in backup_data)
            end_date = max(b['timestamp'].date() for b in backup_data)
            expected_dates = set()
            
            current = start_date
            while current <= end_date:
                expected_dates.add(current)
                current += timedelta(days=1)
            
            missing_dates = expected_dates - dates_with_backups
            
            return {
                'expected_backups': len(expected_dates),
                'actual_backups': len(dates_with_backups),
                'missing_backups': len(missing_dates),
                'reliability_percent': round(len(dates_with_backups) / len(expected_dates) * 100, 2),
                'missing_dates': [str(d) for d in sorted(missing_dates)]
            }
        
        return {'reliability_percent': 0}
    
    def create_charts(self, backup_data):
        """Create visualization charts"""
        if not backup_data:
            return
        
        # Prepare data
        df = pd.DataFrame(backup_data)
        df['date'] = df['timestamp'].dt.date
        df['size_mb'] = df['size'] / 1024 / 1024
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Daily backup count
        daily_counts = df.groupby('date').size()
        ax1.bar(daily_counts.index, daily_counts.values)
        ax1.set_title('Daily Backup Count')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Backups')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Backup size over time
        ax2.plot(df['timestamp'], df['size_mb'], marker='o')
        ax2.set_title('Backup Size Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Size (MB)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Backup type distribution
        type_counts = df['type'].value_counts()
        ax3.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        ax3.set_title('Backup Type Distribution')
        
        # 4. Cumulative storage usage
        df_sorted = df.sort_values('timestamp')
        df_sorted['cumulative_gb'] = df_sorted['size'].cumsum() / 1024 / 1024 / 1024
        ax4.plot(df_sorted['timestamp'], df_sorted['cumulative_gb'])
        ax4.set_title('Cumulative Storage Usage')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Storage (GB)')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'backup_report_{datetime.now().strftime("%Y%m%d")}.png')
        plt.close()
        
        print("Charts saved to: backup_report_*.png")

if __name__ == '__main__':
    reporter = BackupReporter()
    reporter.generate_report()
```

## Recovery Time Objectives / 복구 시간 목표

### RTO/RPO Matrix / RTO/RPO 매트릭스
```yaml
Service Levels:
  Critical:
    RTO: 1 hour      # Recovery Time Objective
    RPO: 1 hour      # Recovery Point Objective
    Components:
      - API endpoints
      - Authentication
      - Core scraping
  
  Important:
    RTO: 4 hours
    RPO: 6 hours
    Components:
      - Dashboard
      - WhatsApp delivery
      - Historical data
  
  Standard:
    RTO: 24 hours
    RPO: 24 hours
    Components:
      - Analytics
      - Reports
      - Archives

Recovery Scenarios:
  Component Failure:
    - Detection: < 5 minutes
    - Diagnosis: < 15 minutes
    - Recovery: < 30 minutes
  
  Data Corruption:
    - Detection: < 30 minutes
    - Diagnosis: < 1 hour
    - Recovery: < 2 hours
  
  Complete Disaster:
    - Detection: < 15 minutes
    - Diagnosis: < 1 hour
    - Recovery: < 4 hours
```

## Best Practices / 모범 사례

### 1. Backup Best Practices / 백업 모범 사례
```yaml
Do:
  - Test backups regularly
  - Automate everything possible
  - Document procedures clearly
  - Monitor backup health
  - Encrypt sensitive data
  - Use multiple storage locations
  - Version control configurations
  - Keep retention policies updated

Don't:
  - Assume backups are working
  - Store all backups in one place
  - Forget to test recovery
  - Ignore backup alerts
  - Use weak encryption
  - Skip verification steps
  - Delay fixing failures
  - Overcomplicate procedures
```

### 2. Recovery Best Practices / 복구 모범 사례
```yaml
Before Recovery:
  - Assess the situation fully
  - Notify stakeholders
  - Document current state
  - Prepare recovery environment
  - Review recovery procedures
  - Gather necessary credentials

During Recovery:
  - Follow documented procedures
  - Log all actions taken
  - Verify each step
  - Communicate progress
  - Be prepared to rollback
  - Test functionality incrementally

After Recovery:
  - Verify full functionality
  - Document lessons learned
  - Update procedures if needed
  - Schedule post-mortem
  - Implement improvements
  - Test backup of recovered system
```

### 3. Continuous Improvement / 지속적 개선
```yaml
Monthly Reviews:
  - Backup success rates
  - Recovery test results
  - Storage utilization
  - Procedure updates
  - Tool improvements

Quarterly Assessments:
  - Full disaster recovery drill
  - RTO/RPO validation
  - Backup strategy review
  - Cost optimization
  - Technology updates

Annual Planning:
  - Strategic backup roadmap
  - Capacity planning
  - Budget allocation
  - Risk assessment
  - Compliance review
```

---
*Remember: Untested backups are not backups. Test your recovery procedures regularly.*

*기억하세요: 테스트하지 않은 백업은 백업이 아닙니다. 복구 절차를 정기적으로 테스트하세요.*

*Last Updated: January 25, 2025*