# GetLate Social Media Automation

A comprehensive social media automation platform powered by GetLate API and AI content generation using Google Gemini.

## Features

- 🤖 **AI-Powered Content Generation**: Generate engaging social media content using Google Gemini AI
- 📱 **Multi-Platform Support**: Post to Twitter, LinkedIn, Facebook, Instagram, and Reddit
- 🎨 **AI Image Generation**: Create custom images for your social media posts
- 🎯 **Content Optimization**: Optimize content based on analytics and performance data
- 📊 **Comprehensive Analytics**: Track performance across all platforms
- 🗣️ **Voice Input**: Use voice commands to create content
- 🔧 **Advanced Configuration**: Flexible configuration system with environment variables
- 📋 **Workflow Management**: Track and manage content creation workflows
- 📝 **Content Variants**: Generate multiple content variants for A/B testing
- 🔍 **Performance Analytics**: Monitor content performance and engagement

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd GetLate_Social_Media_Automation
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Create necessary directories:**
   ```bash
   mkdir -p uploads/images logs
   ```

## Configuration

### Required Environment Variables

```env
# GetLate API Configuration
GETLATE_API_KEY=your_getlate_api_key_here
GETLATE_API_URL=https://api.getlate.dev/v1

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=false
PORT=8000
HOST=0.0.0.0

# File Upload Configuration
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads
```

### Optional Configuration

```env
# Ngrok Configuration (for webhooks)
NGROK_AUTH_TOKEN=your_ngrok_auth_token
NGROK_DOMAIN=your_custom_domain.ngrok.io

# Redis Configuration (for production)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Usage

### Start the Application

```bash
# Development mode
python app.py

# Production mode with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

#### Content Creation
- `POST /create-content` - Create AI-generated content
- `POST /publish-content` - Publish content to social media platforms
- `GET /workflow-status/{workflow_id}` - Get workflow status

#### Account Management
- `GET /accounts` - Get connected social media accounts

#### Analytics
- `GET /analytics` - Get system analytics
- `POST /optimize-content` - Optimize content based on analytics

#### System Management
- `DELETE /cleanup-workflows` - Clean up completed workflows
- `GET /health` - Health check endpoint

### Web Interface

Access the web interface at `http://localhost:8000` to:

1. **Create Content**: Enter a topic and select platforms
2. **Generate AI Content**: Get multiple content variants
3. **Review and Edit**: Preview generated content and images
4. **Publish**: Post to selected social media platforms
5. **Monitor**: Track performance and analytics

## GetLate API Integration

The application integrates with GetLate API for social media posting. Key features:

- **Account Management**: Connect and manage social media accounts
- **Content Publishing**: Post text and images to multiple platforms
- **Platform-Specific Features**: Optimize content for each platform
- **Analytics Integration**: Track post performance and engagement

### Supported Platforms

- **Twitter**: Text posts with hashtags
- **LinkedIn**: Professional content with rich formatting
- **Facebook**: Posts with images and links
- **Instagram**: Image posts with captions and hashtags
- **Reddit**: Subreddit-specific content with proper formatting

## AI Features

### Content Generation
- **Topic-Based Generation**: Create content based on any topic
- **Tone Customization**: Professional, casual, humorous, inspirational, educational
- **Platform Optimization**: Tailor content for each platform
- **Hashtag Generation**: AI-generated relevant hashtags
- **Content Variants**: Multiple versions for A/B testing

### Image Generation
- **AI Image Creation**: Generate custom images using Gemini AI
- **Image Enhancement**: Improve existing images
- **Style Customization**: Different artistic styles and themes
- **Size Optimization**: Platform-specific image dimensions

### Content Optimization
- **Performance Analysis**: Analyze content performance
- **Engagement Prediction**: Predict engagement rates
- **Content Suggestions**: AI-powered content recommendations
- **SEO Optimization**: Optimize content for search

## Logging and Monitoring

The application includes comprehensive logging:

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File and Console Output**: Dual logging to files and console
- **Platform-Specific Logs**: Separate logs for each social media platform
- **API Call Logging**: Track all API interactions
- **Error Tracking**: Detailed error logging with stack traces

### Log Files

- `logs/app.log` - Main application logs
- `logs/getlate_api.log` - GetLate API interactions
- `logs/ai_service.log` - AI service logs
- `logs/workflow.log` - Workflow execution logs

## Security Features

- **API Key Management**: Secure storage of API keys
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Prevent API abuse
- **Error Handling**: Secure error messages
- **CORS Configuration**: Proper CORS settings
- **File Upload Security**: Safe file handling

## Development

### Project Structure

```
GetLate_Social_Media_Automation/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── src/
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic services
│   ├── routes/              # API routes
│   └── utils/               # Utility functions
├── templates/               # HTML templates
├── static/                  # CSS and JavaScript files
├── uploads/                 # File uploads directory
└── logs/                    # Log files
```

### Adding New Features

1. **New Social Media Platform**:
   - Add platform configuration in `src/config.py`
   - Implement platform-specific logic in `src/services/getlate_service.py`
   - Add platform models in `src/models/__init__.py`
   - Update frontend templates

2. **New AI Features**:
   - Extend `src/services/ai_service.py`
   - Add new models if needed
   - Update API endpoints in `src/routes/main_routes.py`

3. **New Analytics**:
   - Extend `src/services/analytics_service.py`
   - Add new API endpoints
   - Update frontend analytics display

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Verify all API keys are correctly set in `.env`
   - Check API key permissions and quotas
   - Review API documentation for authentication requirements

2. **Content Generation Failures**:
   - Check Google Gemini API quota and limits
   - Verify prompt formatting and content policies
   - Review error logs for specific issues

3. **Publishing Issues**:
   - Verify social media account connections
   - Check platform-specific requirements and limits
   - Review GetLate API documentation for platform constraints

4. **Performance Issues**:
   - Monitor system resources and memory usage
   - Check log files for performance warnings
   - Consider implementing caching for frequently accessed data

### Debug Mode

Enable debug mode by setting `DEBUG=true` in your `.env` file:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

This will provide detailed logging and error information.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- 📧 Email: support@yourcompany.com
- 💬 Discord: [Join our Discord server]
- 📚 Documentation: [View full documentation]
- 🐛 Issues: [Report bugs and issues]

## Changelog

### Version 1.0.0
- Initial release with GetLate API integration
- AI-powered content generation using Google Gemini
- Multi-platform social media posting
- Comprehensive analytics and monitoring
- Voice input support
- Web interface with modern UI

---

**Built with ❤️ using FastAPI, Google Gemini AI, and GetLate API**