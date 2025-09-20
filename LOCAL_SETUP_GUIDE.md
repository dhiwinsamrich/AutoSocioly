# AutoSocioly Local Development Setup Guide

## 🚀 Quick Start (Development Mode)

### Step 1: Create Environment File
```bash
copy .env.example .env
```

### Step 2: Configure Your API Keys
Edit `.env` file and add your API keys:
```
GETLATE_API_KEY=your_getlate_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
```

### Step 3: Start Development Environment
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Or start with full services (including PostgreSQL)
docker-compose -f docker-compose.dev.yml --profile db up -d
```

### Step 4: Access Your Application
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis Commander**: http://localhost:8081

## 📋 Complete Setup Instructions

### Prerequisites Check
```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose version
```

### Option 1: Development Mode (Recommended for Development)
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Option 2: Production Mode (For Testing Production Setup)
```bash
# Generate SSL certificates first
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/autosocioly.key \
  -out ssl/autosocioly.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Start production environment
docker-compose --profile production up -d

# Access with HTTPS
https://localhost
```

### Option 3: Simple Mode (Minimal Setup)
```bash
# Start just the app and Redis
docker-compose up -d

# Access application
http://localhost:8000
```

## 🔧 Environment Configuration

### Required API Keys
You need to obtain these API keys:

1. **GetLate API Key**: Sign up at https://getlate.dev
2. **Google Gemini API Key**: Get from Google AI Studio

### Sample .env Configuration
```env
# Application
SECRET_KEY=your-very-secure-secret-key-change-this
DEBUG=true
HOST=0.0.0.0
PORT=8000

# API Keys (Required)
GETLATE_API_KEY=your_actual_getlate_api_key
GOOGLE_API_KEY=your_actual_google_api_key

# Redis (Auto-configured in Docker)
REDIS_URL=redis://redis:6379/0

# File Uploads
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

## 🐳 Docker Commands Reference

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
docker-compose logs -f redis

# Stop services
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# View running containers
docker ps

# Access container shell
docker-compose exec app bash

# Check Redis connection
docker-compose exec redis redis-cli ping
```

## 🔄 Development Workflow

### Making Code Changes
```bash
# The development setup supports hot reload
# Just edit your code and changes will be reflected automatically

# If you need to restart:
docker-compose -f docker-compose.dev.yml restart app
```

### Database/Cache Management
```bash
# Access Redis Commander
http://localhost:8081

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# View Redis info
docker-compose exec redis redis-cli INFO
```

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Or use different ports in docker-compose.dev.yml
```

2. **Container Won't Start**
```bash
# Check logs
docker-compose logs app

# Rebuild containers
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

3. **Redis Connection Issues**
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Should return: PONG
```

4. **Permission Issues**
```bash
# Fix permissions on Windows
icacls static/uploads /grant Everyone:F /T
icacls logs /grant Everyone:F /T
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove all images and rebuild
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Verification Steps

After starting the services, verify everything is working:

1. **Health Check**: http://localhost:8000/health
2. **API Docs**: http://localhost:8000/docs
3. **Main App**: http://localhost:8000
4. **Redis**: Should show "PONG" when you run `docker-compose exec redis redis-cli ping`

## 🎯 Next Steps

1. **Get API Keys**: Obtain GetLate and Google Gemini API keys
2. **Test Features**: Try the content generation and posting features
3. **Customize**: Modify the code for your specific needs
4. **Deploy**: Use the production setup for live deployment

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your `.env` configuration
3. Ensure all required API keys are valid
4. Check the troubleshooting section above