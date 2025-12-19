# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Domain name with DNS configured
- SSL certificates (via Let's Encrypt recommended)
- PostgreSQL database (RDS, Cloud SQL, or self-hosted)
- API keys for:
  - OpenRouter
  - OpenAI (optional)
  - Anthropic (optional)

## Quick Deployment

### 1. Clone and Configure

```bash
git clone https://github.com/prlenterprises-ui/ai-dev.git
cd ai-dev

# Copy and configure environment files
cp apps/portal-python/.env.production apps/portal-python/.env
# Edit .env with your production values

cp apps/portal-ui/.env.example apps/portal-ui/.env
# Edit with your production API URL
```

### 2. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check health
curl http://localhost:8000/api/health
```

### 3. Set up Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/ai-portal
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /graphql {
        proxy_pass http://localhost:8000/graphql;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        root /var/www/ai-portal;
        try_files $uri $uri/ /index.html;
    }
}
```

### 4. SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Environment Variables

### Backend (.env)

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

HOST=0.0.0.0
PORT=8000

CORS_ORIGINS=https://yourdomain.com

# CRITICAL: Set these
OPENROUTER_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/portal

UPLOAD_DIR=/var/lib/portal/uploads
OUTPUT_DIR=/var/lib/portal/outputs

API_KEY=your_secure_key
```

### Frontend (.env)

```env
VITE_API_URL=https://yourdomain.com
VITE_GRAPHQL_URL=https://yourdomain.com/graphql
VITE_ENV=production
```

## Database Setup

### PostgreSQL (Recommended for Production)

```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_DB=portal \
  -e POSTGRES_USER=portal \
  -e POSTGRES_PASSWORD=secure_password \
  -v portal_db:/var/lib/postgresql/data \
  postgres:15

# Or use managed service (AWS RDS, Google Cloud SQL, etc.)
```

### Run Migrations

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
from python.database import init_db
asyncio.run(init_db())
"
```

## Monitoring

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-12-19T...",
  "version": "0.1.0"
}
```

### Logs

```bash
# View backend logs
docker-compose -f docker-compose.prod.yml logs -f backend

# View frontend logs (if using Docker)
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Metrics (Optional)

Add Prometheus + Grafana for advanced monitoring:

```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## Backups

### Database Backups

```bash
# Automated daily backups
docker exec postgres pg_dump -U portal portal > backup_$(date +%Y%m%d).sql

# Add to crontab:
0 2 * * * /path/to/backup_script.sh
```

### File Storage Backups

```bash
# Backup uploads and outputs
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /var/lib/portal/uploads
tar -czf outputs_backup_$(date +%Y%m%d).tar.gz /var/lib/portal/outputs
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

### Load Balancing

Use nginx or a cloud load balancer to distribute traffic:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] API keys stored securely (not in code)
- [ ] CORS configured with specific domains
- [ ] Database credentials rotated regularly
- [ ] File upload size limits enforced
- [ ] Rate limiting enabled (via nginx or middleware)
- [ ] Logs monitored for suspicious activity
- [ ] Regular security updates applied
- [ ] Backups tested and verified
- [ ] Firewall configured (only necessary ports open)

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

### Database connection errors

```bash
# Verify database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec backend python -c "
from python.database import engine
import asyncio
asyncio.run(engine.connect())
print('Connection successful')
"
```

### API returns 502/504

```bash
# Check backend is responding
curl http://localhost:8000/api/health

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Database Maintenance

```bash
# Vacuum database
docker-compose -f docker-compose.prod.yml exec postgres vacuumdb -U portal portal

# Check database size
docker-compose -f docker-compose.prod.yml exec postgres psql -U portal -c "
SELECT pg_size_pretty(pg_database_size('portal'));
"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/prlenterprises-ui/ai-dev/issues
- Documentation: See README.md

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
