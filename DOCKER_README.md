# AutoSocioly Docker Deployment

## 🚀 Quick Start

### Development Environment
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access application
http://localhost:8000

# Access Redis Commander
http://localhost:8081
```

### Production Environment
```bash
# Start production environment
docker-compose --profile production up -d

# Access application with SSL
https://localhost
```

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 10GB available disk space

## 🔧 Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your settings:**
   - Add your API keys (GetLate, Google Gemini)
   - Set your domain and security settings
   - Configure Redis connection

3. **SSL Certificates (Production):**
   ```bash
   # Generate self-signed certificates for testing
   mkdir ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/autosocioly.key \
     -out ssl/autosocioly.crt
   ```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   AutoSocioly   │    │     Redis       │
│  (Load Balancer)│────│   Application   │────│   (Cache/Store) │
│   Port: 80/443  │    │   Port: 8000    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Services

| Service | Port | Description |
|---------|------|-------------|
| Application | 8000 | Main FastAPI application |
| Redis | 6379 | Caching and session storage |
| Redis Commander | 8081 | Redis management UI (dev only) |
| Nginx | 80/443 | Load balancer and SSL termination |

## 🔄 Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Scale application
docker-compose up -d --scale app=3
```

## 📁 Volumes

- `static/uploads`: User uploaded files
- `logs`: Application logs
- `redis_data`: Redis persistent data

## 🔒 Security Features

- Non-root container execution
- SSL/TLS encryption
- Rate limiting
- Input validation
- Secure session management
- Redis security hardening

## 🚀 Deployment Options

### Single Server
```bash
docker-compose --profile production up -d
```

### Multi-Server (High Availability)
```bash
# Load balancer server
docker-compose --profile loadbalancer up -d

# Application servers
docker-compose up -d app redis
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 📊 Monitoring

### Health Checks
- Application: `http://localhost:8000/health`
- Redis: `redis-cli ping`

### Logs
```bash
# Application logs
docker-compose logs -f app

# All logs
docker-compose logs -f
```

## 🔧 Customization

### Environment Variables
See `.env.example` for all available configuration options.

### Redis Configuration
Edit `redis.conf` to customize:
- Memory limits
- Persistence settings
- Security policies

### Nginx Configuration
Edit `nginx.conf` to customize:
- Load balancing
- SSL settings
- Rate limiting

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 6379, 8081 are available
2. **Memory issues**: Increase Docker memory limits
3. **Permission issues**: Check file permissions for uploads

### Debug Mode
```bash
docker-compose -f docker-compose.dev.yml up -d
```

## 📚 Documentation

- [Full Deployment Guide](DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [Redis Commander](http://localhost:8081)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This Docker configuration is licensed under the MIT License.

## 🆘 Support

- GitHub Issues: [Report bugs](https://github.com/your-username/AutoSocioly/issues)
- Documentation: [Full guide](DEPLOYMENT.md)
- Email: support@autosocioly.com