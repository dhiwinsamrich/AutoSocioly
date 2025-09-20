# AutoSocioly Docker Deployment Guide

## Overview

AutoSocioly is containerized using Docker for easy deployment and scaling. This guide covers all aspects of deploying the application with Redis caching, load balancing, and production-ready configurations.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM recommended
- 10GB+ available disk space

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/AutoSocioly.git
cd AutoSocioly

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start development environment
docker-compose up -d

# Access the application
open http://localhost:8000
```

### Production Environment

```bash
# Start production environment with SSL and load balancing
docker-compose --profile production up -d

# Access the application (with SSL)
open https://localhost
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=false
HOST=0.0.0.0
PORT=8000
BASE_URL=https://your-domain.com

# API Keys
GETLATE_API_KEY=your-getlate-api-key
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL_ID=gemini-2.0-flash-001
GEMINI_IMAGE_MODEL_ID=gemini-2.5-flash-image-preview

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# File Upload Settings
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

# Security Settings
RATE_LIMIT_PER_MINUTE=60
SESSION_COOKIE_SECURE=true

# Optional Services
NGROK_AUTHTOKEN=your-ngrok-token
USE_NGROK=false
```

### Redis Configuration

The Redis server is configured with:
- **Memory limit**: 256MB with LRU eviction
- **Persistence**: RDB snapshots + AOF for data durability
- **Security**: Dangerous commands disabled
- **Performance**: Optimized for caching and session storage

### SSL Configuration (Production)

For production deployment with SSL:

1. Generate SSL certificates:
```bash
# Using Let's Encrypt (recommended)
certbot certonly --standalone -d your-domain.com

# Or generate self-signed certificates for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/autosocioly.key \
  -out ssl/autosocioly.crt
```

2. Mount certificates in docker-compose.yml:
```yaml
volumes:
  - ./ssl/autosocioly.crt:/etc/ssl/certs/autosocioly.crt:ro
  - ./ssl/autosocioly.key:/etc/ssl/private/autosocioly.key:ro
```

## Deployment Options

### Single Server Deployment

```bash
# Development
docker-compose up -d

# Production with SSL
docker-compose --profile production up -d
```

### Multi-Server Deployment

For high availability, deploy across multiple servers:

```bash
# On load balancer server
docker-compose --profile loadbalancer up -d

# On application servers
docker-compose up -d app redis

# On database/cache servers
docker-compose up -d redis
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=autosocioly
```

## Monitoring and Logging

### Application Logs

```bash
# View application logs
docker-compose logs -f app

# View Redis logs
docker-compose logs -f redis

# View all logs
docker-compose logs -f
```

### Redis Monitoring

Access Redis Commander for database monitoring:
```bash
# Start with Redis Commander
docker-compose --profile dev up -d

# Access Redis Commander
open http://localhost:8081
```

### Health Checks

The application provides health check endpoints:
- Application: `http://localhost:8000/health`
- Redis: `redis-cli ping`

## Scaling

### Horizontal Scaling

```bash
# Scale application instances
docker-compose up -d --scale app=3

# Scale with load balancer
docker-compose --profile production up -d --scale app=3
```

### Vertical Scaling

Adjust resource limits in docker-compose.yml:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Backup and Recovery

### Redis Data Backup

```bash
# Create backup
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup/

# Restore backup
docker cp ./backup/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose restart redis
```

### Application Data Backup

```bash
# Backup uploads
docker run --rm -v autosocioly_static_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz -C /data .

# Backup logs
docker run --rm -v autosocioly_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs_backup.tar.gz -C /data .
```

## Security

### Network Security

- Application runs on isolated Docker network
- Redis is not exposed to external network
- Rate limiting implemented via Nginx

### Container Security

- Non-root user execution
- Minimal base images
- Regular security updates
- Vulnerability scanning

### Data Security

- Environment variables for sensitive data
- SSL/TLS encryption in production
- Secure session management
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 6379, 8081 are available
2. **Memory issues**: Increase Docker memory limits
3. **Permission issues**: Check file permissions for uploads and logs
4. **Network issues**: Verify Docker network configuration

### Debug Mode

```bash
# Enable debug logging
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up -d
```

### Performance Tuning

1. **Redis optimization**: Adjust memory limits and eviction policies
2. **Application tuning**: Modify worker processes and connection pools
3. **Nginx tuning**: Adjust buffer sizes and connection limits

## Maintenance

### Updates

```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f
```

### Monitoring

Set up monitoring with:
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for notifications

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-username/AutoSocioly/issues
- Documentation: https://docs.autosocioly.com
- Email: support@autosocioly.com

## License

This Docker configuration is licensed under the MIT License. See LICENSE file for details.