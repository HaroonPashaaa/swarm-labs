# Migration Guide

## Upgrading from v0.x to v1.0

### Breaking Changes

1. **Database Schema**
   - Run migrations: `python scripts/migrate.py`
   
2. **Configuration Format**
   - `.env` file structure changed
   - Copy `.env.example` and update values

3. **API Changes**
   - Signal format updated
   - Review agent implementations

### Migration Steps

```bash
# 1. Backup data
python scripts/backup.py

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run migrations
python scripts/migrate.py

# 5. Update configuration
cp .env.example .env
# Edit .env with your settings

# 6. Restart services
docker-compose restart
```

## Database Migrations

### Create New Migration

```bash
python scripts/create_migration.py --name "add_new_table"
```

### Rollback Migration

```bash
python scripts/rollback_migration.py --version 20240101
```
