from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, List
import logging
from contextlib import asynccontextmanager

from src.config import settings
from src.utils.logger_config import setup_logging
from src.routes.main_routes import router as main_router
from src.routes.user_workflow_routes import router as user_workflow_router
from src.services.getlate_service import GetLateService
from src.services.workflow_service import SocialMediaWorkflow

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
getlate_service = None
workflow_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global getlate_service, workflow_service
    
    # Startup
    logger.info("Starting GetLate Social Media Automation...")
    
    try:
        # Initialize GetLate service
        getlate_service = GetLateService(
            api_key=settings.GETLATE_API_KEY,
            base_url=settings.GETLATE_BASE_URL
        )
        
        # Initialize workflow service
        workflow_service = SocialMediaWorkflow()
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GetLate Social Media Automation...")

# Create FastAPI app
app = FastAPI(
    title="GetLate Social Media Automation",
    description="AI-powered social media content generation and posting platform",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(main_router, prefix="", tags=["main"])
app.include_router(user_workflow_router, prefix="/api", tags=["user-workflow"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GetLate Social Media Automation",
        "version": "1.0.0"
    }

# Root endpoint - redirect to main page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - main page"""
    return templates.TemplateResponse("index.html", {"request": request})

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "error_code": 404, "error_message": "Page not found"},
        status_code=404
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "error_code": 500, "error_message": "Internal server error"},
        status_code=500
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    # Suppress watchfiles logging before starting uvicorn
    import logging
    logging.getLogger('watchfiles').setLevel(logging.WARNING)
    logging.getLogger('watchfiles.main').setLevel(logging.WARNING)
    
    # Run the application
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )