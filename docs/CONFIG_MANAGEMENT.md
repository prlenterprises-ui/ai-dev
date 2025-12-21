# Configuration Management

## Overview

The application now uses a **database-first configuration system** with automatic fallback to `config.json`.

## Configuration Priority

1. **Primary Source: Database** (`configs` table)
   - Configurations are stored in SQLite database
   - Editable via `/api/configs` endpoints
   - Managed through admin UI (coming soon)
   - Persistent across deployments

2. **Fallback Source: config.json**
   - Used when database is unavailable
   - Used for initial seeding
   - Read-only reference

## Configuration Names

| Config Name | Purpose | JSON Keys |
|------------|---------|-----------|
| `auto-apply` | Job search & matching | `jsearch`, `score_matching` |
| `matching_service` | Job scoring weights | `score_matching` |
| `jobbernaut` | Resume generation | jobbernaut settings |

## Usage Examples

### Python (Async)

```python
from python.config_loader import get_config

# Load config from DB with fallback to config.json
config = await get_config("auto-apply")
jsearch_settings = config.get("jsearch", {})
api_key = jsearch_settings.get("X-RapidAPI-Key")

# Load without fallback (DB only)
config = await get_config("auto-apply", fallback_to_json=False)

# Update config in database
from python.config_loader import update_config_in_db

await update_config_in_db(
    "auto-apply",
    {"jsearch": {...}, "score_matching": {...}},
    title="Auto Apply Configuration",
    description="Updated via API"
)
```

### API Endpoints

```bash
# List all configs
GET /api/configs/

# Get specific config
GET /api/configs/auto-apply

# Create new config
POST /api/configs/
{
  "name": "my-config",
  "title": "My Configuration",
  "config_json": {"key": "value"}
}

# Update config
PUT /api/configs/auto-apply
{
  "config_json": {
    "jsearch": {...},
    "score_matching": {...}
  }
}

# Delete config
DELETE /api/configs/auto-apply
```

## Initial Setup

### 1. Seed Database from config.json

```bash
cd apps/portal-python
python seed_configs.py
```

This will:
- Load settings from `apps/config.json`
- Create/update `auto-apply` config in database
- Create/update `matching_service` config in database
- Database becomes the source of truth

### 2. Verify Seeding

```bash
# Check what's in the database
sqlite3 portal.db "SELECT name, title FROM configs;"
```

## Updating Configuration

### Option 1: Via API (Recommended)

```bash
# Update jsearch queries
curl -X PUT http://localhost:8000/api/configs/auto-apply \
  -H "Content-Type: application/json" \
  -d '{
    "config_json": {
      "jsearch": {
        "queries": ["Senior Engineer", "Staff Engineer"],
        "X-RapidAPI-Key": "your-key",
        "remote_jobs_only": true
      }
    }
  }'
```

### Option 2: Edit config.json + Re-seed

```bash
# 1. Edit apps/config.json
vim apps/config.json

# 2. Re-run seed to update database
python seed_configs.py
```

### Option 3: Direct Database Edit

```bash
sqlite3 portal.db
UPDATE configs 
SET config_json = '{"jsearch": {...}}' 
WHERE name = 'auto-apply';
```

## Files Using Database Config

### Updated Files (Database-First)

- ✅ `apis/jobs_routes.py` - Job search endpoint
- ✅ `apis/config_routes.py` - Config management API
- ✅ `download_jobs_autopaging.py` - Standalone job downloader
- ✅ `ai/jobbernaut_service.py` - Resume generation service
- ✅ `seed_configs.py` - Database seeder

### Files Still Using config.json

- ⚠️ `jobbernaut/src/main.py` - Jobbernaut core (standalone)
- ⚠️ `jobbernaut/src/utils.py` - Utility functions (file-based)

Note: Jobbernaut is a standalone module that loads from its own `config.json` for independence.

## Migration Notes

### Before (config.json only)
```python
with open("config.json") as f:
    config = json.load(f)
    api_key = config["jsearch"]["X-RapidAPI-Key"]
```

### After (Database-first with fallback)
```python
from python.config_loader import get_config

config = await get_config("auto-apply")
api_key = config.get("jsearch", {}).get("X-RapidAPI-Key")
```

## Benefits

### Database-First Approach

1. **Dynamic Updates**: Change config without restarting server
2. **API Management**: Update via REST endpoints
3. **UI Integration**: Can build admin UI for config management
4. **Audit Trail**: Track when configs were updated
5. **Multi-Environment**: Different configs per environment

### config.json Fallback

1. **Reliability**: System works even if DB is unavailable
2. **Easy Setup**: Initial configuration via JSON file
3. **Portability**: Share configs as files
4. **Version Control**: Track config changes in git

## Troubleshooting

### Config not loading from database

```bash
# Check if database is initialized
ls -la portal.db

# Check if configs exist
sqlite3 portal.db "SELECT * FROM configs;"

# Re-seed from config.json
python seed_configs.py
```

### Want to reset to config.json

```bash
# Delete database
rm portal.db

# Re-seed
python seed_configs.py
```

### config.json not found

The system looks in these locations (in order):
1. `/workspaces/ai-dev/apps/config.json`
2. `/workspaces/ai-dev/apps/portal-python/config.json`
3. Current working directory

## Best Practices

1. **Initial Setup**: Use `seed_configs.py` to populate database from config.json
2. **Production**: Update configs via API endpoints, not by editing files
3. **Development**: Edit config.json and re-seed for major changes
4. **Backup**: Keep config.json in version control as reference
5. **Secrets**: Store API keys in environment variables, not in config

## Future Enhancements

- [ ] Admin UI for config management
- [ ] Config versioning and rollback
- [ ] Environment-specific configs (dev/staging/prod)
- [ ] Config validation and schema enforcement
- [ ] Export/import configs as JSON
- [ ] Audit logs for config changes
