"""
FastAPI Application for Cloud Run Deployment
Multi-Agent Content Generation System
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.orchestration import ContentGenerationWorkflow
from src.monitoring import StructuredLogger
from src.infrastructure.budget_controller import BudgetController

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Content Generation API",
    description="AI-powered content generation with media creation and publishing",
    version="1.0.0"
)

# Initialize logger
logger = StructuredLogger(name='api')

# Request/Response Models
class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    topic: str = Field(..., description="Topic for the content", min_length=3)
    content_type: str = Field(
        default="blog_post",
        description="Type of content (blog_post, article, social_media_post)"
    )
    platform: str = Field(
        default="wordpress",
        description="Platform (twitter, facebook, instagram, wordpress, medium)"
    )
    media_types: list = Field(
        default=[],
        description="List of media types to generate (image, video, audio)"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata (tone, length, hashtags, etc.)"
    )


class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""
    status: str
    message: str
    project_id: Optional[str] = None
    content_url: Optional[str] = None
    media_urls: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    budget_status: Optional[dict] = None


class BudgetStatusResponse(BaseModel):
    """Budget status response"""
    total_spent: float
    total_budget: float
    percentage_used: float
    categories: dict
    is_throttled: bool


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "name": "Multi-Agent Content Generation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "budget": "/budget",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Check budget status
        budget_controller = BudgetController()
        budget_status = budget_controller.get_budget_status()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            budget_status=budget_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/budget", response_model=BudgetStatusResponse)
async def get_budget_status():
    """Get current budget status"""
    try:
        budget_controller = BudgetController()
        status = budget_controller.get_budget_status()
        
        return BudgetStatusResponse(
            total_spent=status['total_spent'],
            total_budget=status['total_budget'],
            percentage_used=status['percentage_used'],
            categories=status['categories'],
            is_throttled=status.get('is_throttled', False)
        )
    except Exception as e:
        logger.error(f"Failed to get budget status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve budget status")


@app.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate content using multi-agent workflow
    
    This endpoint triggers the content generation process and returns immediately.
    The actual generation happens in the background.
    """
    try:
        logger.info(f"Content generation request received for topic: {request.topic}")
        
        # Check budget before processing
        budget_controller = BudgetController()
        budget_status = budget_controller.get_budget_status()
        
        if budget_status.get('is_throttled', False):
            raise HTTPException(
                status_code=429,
                detail=f"Budget exceeded. Used {budget_status['percentage_used']:.1f}% of monthly budget."
            )
        
        # Initialize workflow
        workflow = ContentGenerationWorkflow()
        
        # Generate content in background
        def run_workflow():
            try:
                # Extract tone and word count from metadata, use defaults if not provided
                metadata = request.metadata or {}
                tone = metadata.get('tone', 'professional and conversational')
                word_count = metadata.get('word_count', 1200)
                
                # Check if images should be generated
                generate_images = 'image' in request.media_types if request.media_types else False
                
                result = workflow.generate_content(
                    topic=request.topic,
                    tone=tone,
                    target_word_count=word_count,
                    generate_images=generate_images
                )
                logger.info(f"Content generation completed: {result.get('project_id')}")
            except Exception as e:
                logger.error(f"Workflow execution failed: {str(e)}")
        
        # Add to background tasks
        background_tasks.add_task(run_workflow)
        
        return ContentGenerationResponse(
            status="processing",
            message="Content generation started. Check logs for progress.",
            project_id=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/generate/sync", response_model=ContentGenerationResponse)
async def generate_content_sync(request: ContentGenerationRequest):
    """
    Generate content synchronously (waits for completion)
    
    Use this endpoint if you need the result immediately.
    Note: This may timeout for long-running operations.
    """
    try:
        logger.info(f"Synchronous content generation request for topic: {request.topic}")
        
        # Check budget
        budget_controller = BudgetController()
        budget_status = budget_controller.get_budget_status()
        
        if budget_status.get('is_throttled', False):
            raise HTTPException(
                status_code=429,
                detail=f"Budget exceeded. Used {budget_status['percentage_used']:.1f}% of monthly budget."
            )
        
        # Initialize and run workflow
        workflow = ContentGenerationWorkflow()
        
        # Extract tone and word count from metadata, use defaults if not provided
        metadata = request.metadata or {}
        tone = metadata.get('tone', 'professional and conversational')
        word_count = metadata.get('word_count', 1200)
        
        # Check if images should be generated
        generate_images = 'image' in request.media_types if request.media_types else False
        
        logger.info(f"Media types requested: {request.media_types}, generate_images: {generate_images}")
        
        result = workflow.generate_content(
            topic=request.topic,
            tone=tone,
            target_word_count=word_count,
            generate_images=generate_images
        )
        
        logger.info(f"Workflow result: success={result.get('success')}, project_id={result.get('project_id')}, has_content={bool(result.get('content'))}, has_project={bool(result.get('project'))}")
        logger.info(f"Content generation completed: {result.get('project_id')}")
        
        # Check if generation was successful
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract content and project data
        project = result.get('project', {})
        content_data = result.get('content', {})
        
        # Get the actual content text from project or content data
        # Priority: project.content.body > content.body > content.content
        if 'content' in project and 'body' in project['content']:
            content_text = project['content']['body']
        elif 'body' in content_data:
            content_text = content_data['body']
        elif 'content' in content_data:
            content_text = content_data['content']
        else:
            content_text = 'No content generated'
        
        # Get title
        if 'content' in project and 'title' in project['content']:
            title = project['content']['title']
        elif 'title' in content_data:
            title = content_data['title']
        else:
            title = None
        
        # Get media URLs from result
        media_urls = result.get('media_urls', {'image': [], 'video': []})
        image_urls = media_urls.get('image', [])
        video_urls = media_urls.get('video', [])
        
        # If not in result, check project.media
        if not image_urls and not video_urls and 'media' in project:
            media = project.get('media', {})
            if 'main_image' in media:
                image_urls = [media['main_image']]
            elif 'all_images' in media:
                image_urls = media['all_images']
        
        # Get word count
        word_count = None
        if 'content' in project and 'word_count' in project['content']:
            word_count = project['content']['word_count']
        elif 'word_count' in content_data:
            word_count = content_data['word_count']
        
        return ContentGenerationResponse(
            status="completed",
            message=f"Content generated successfully{f' ({word_count} words)' if word_count else ''}",
            project_id=result.get('project_id'),
            content_url=content_text[:500] + '...' if len(content_text) > 500 else content_text,  # Truncate for API response
            media_urls={
                'image': image_urls if isinstance(image_urls, list) else [],
                'video': video_urls if isinstance(video_urls, list) else []
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": f"The requested path {request.url.path} was not found",
        "available_endpoints": ["/", "/health", "/generate", "/budget", "/docs"]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
