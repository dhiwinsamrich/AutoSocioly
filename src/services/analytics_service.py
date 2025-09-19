from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

from ..config import settings
from ..utils.logger_config import get_logger

logger = get_logger('analytics_service')

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self):
        """Initialize analytics service"""
        self.analytics_data_dir = Path(settings.ANALYTICS_DATA_DIR)
        self.analytics_data_dir.mkdir(exist_ok=True)
        
        logger.info(f"Analytics service initialized with data directory: {self.analytics_data_dir}")
    
    def log_content_performance(
        self,
        workflow_id: str,
        platform: str,
        content_id: str,
        metrics: Dict[str, Any]
    ):
        """
        Log content performance metrics
        
        Args:
            workflow_id: Workflow ID
            platform: Platform name
            content_id: Content ID
            metrics: Performance metrics
        """
        try:
            timestamp = datetime.now()
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "workflow_id": workflow_id,
                "platform": platform,
                "content_id": content_id,
                "metrics": metrics,
                "date": timestamp.strftime("%Y-%m-%d")
            }
            
            # Save to daily analytics file
            date_str = timestamp.strftime("%Y-%m-%d")
            analytics_file = self.analytics_data_dir / f"analytics_{date_str}.jsonl"
            
            with open(analytics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.info(f"Logged performance metrics for {platform} content {content_id}")
            
        except Exception as e:
            logger.error(f"Failed to log performance metrics: {e}")
    
    def get_platform_analytics(
        self,
        platform: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get platform analytics data
        
        Args:
            platform: Optional platform filter
            date_from: Optional start date
            date_to: Optional end date
            limit: Maximum number of records
            
        Returns:
            Analytics data
        """
        try:
            analytics_data = []
            
            # Default date range: last 30 days
            if not date_from:
                date_from = datetime.now() - timedelta(days=30)
            if not date_to:
                date_to = datetime.now()
            
            # Collect analytics files in date range
            current_date = date_from
            while current_date <= date_to:
                date_str = current_date.strftime("%Y-%m-%d")
                analytics_file = self.analytics_data_dir / f"analytics_{date_str}.jsonl"
                
                if analytics_file.exists():
                    try:
                        with open(analytics_file, "r", encoding="utf-8") as f:
                            for line in f:
                                try:
                                    entry = json.loads(line.strip())
                                    
                                    # Apply filters
                                    if platform and entry.get("platform") != platform:
                                        continue
                                    
                                    analytics_data.append(entry)
                                    
                                    if len(analytics_data) >= limit:
                                        break
                                except json.JSONDecodeError:
                                    continue
                        
                        if len(analytics_data) >= limit:
                            break
                            
                    except Exception as e:
                        logger.error(f"Error reading analytics file {analytics_file}: {e}")
                
                current_date += timedelta(days=1)
            
            # Calculate summary statistics
            platform_stats = {}
            total_posts = len(analytics_data)
            
            for entry in analytics_data:
                platform_name = entry.get("platform", "unknown")
                metrics = entry.get("metrics", {})
                
                if platform_name not in platform_stats:
                    platform_stats[platform_name] = {
                        "total_posts": 0,
                        "total_engagement": 0,
                        "total_reach": 0,
                        "average_engagement_rate": 0,
                        "top_performing_content": []
                    }
                
                platform_stats[platform_name]["total_posts"] += 1
                platform_stats[platform_name]["total_engagement"] += metrics.get("engagement", 0)
                platform_stats[platform_name]["total_reach"] += metrics.get("reach", 0)
            
            # Calculate averages
            for platform_name, stats in platform_stats.items():
                if stats["total_posts"] > 0:
                    stats["average_engagement_rate"] = (
                        stats["total_engagement"] / stats["total_posts"]
                    )
            
            logger.info(f"Retrieved analytics data: {total_posts} records across {len(platform_stats)} platforms")
            
            return {
                "success": True,
                "data": {
                    "total_records": total_posts,
                    "date_range": {
                        "from": date_from.isoformat(),
                        "to": date_to.isoformat()
                    },
                    "platform_stats": platform_stats,
                    "raw_data": analytics_data[:limit]  # Return limited raw data
                },
                "message": "Analytics data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve analytics data"
            }
    
    def get_workflow_analytics(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get workflow performance analytics
        
        Args:
            workflow_id: Optional specific workflow ID
            
        Returns:
            Workflow analytics data
        """
        try:
            # This would integrate with workflow logs
            # For now, return mock data structure
            
            workflow_stats = {
                "total_workflows": 0,
                "successful_workflows": 0,
                "failed_workflows": 0,
                "average_completion_time": 0,
                "platform_success_rates": {},
                "recent_workflows": []
            }
            
            logger.info("Workflow analytics retrieved (mock data)")
            
            return {
                "success": True,
                "data": workflow_stats,
                "message": "Workflow analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve workflow analytics"
            }
    
    def generate_performance_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            date_from: Optional start date
            date_to: Optional end date
            
        Returns:
            Performance report
        """
        try:
            # Get platform analytics
            platform_analytics = self.get_platform_analytics(
                date_from=date_from,
                date_to=date_to
            )
            
            # Get workflow analytics
            workflow_analytics = self.get_workflow_analytics()
            
            if not platform_analytics["success"]:
                raise Exception("Failed to get platform analytics")
            
            platform_data = platform_analytics["data"]
            
            # Generate insights
            insights = []
            
            # Platform performance insights
            for platform, stats in platform_data.get("platform_stats", {}).items():
                if stats["total_posts"] > 0:
                    avg_engagement = stats["average_engagement_rate"]
                    if avg_engagement > 100:  # High engagement threshold
                        insights.append(f"{platform.title()} shows high engagement with {avg_engagement:.1f} average interactions per post")
                    elif avg_engagement < 10:  # Low engagement threshold
                        insights.append(f"{platform.title()} engagement could be improved (current: {avg_engagement:.1f} per post)")
            
            # Content performance insights
            total_posts = platform_data.get("total_records", 0)
            if total_posts > 0:
                insights.append(f"Generated {total_posts} posts in the specified period")
            
            # Recommendations
            recommendations = [
                "Focus on platforms with highest engagement rates",
                "Test different posting times for better reach",
                "Use A/B testing with content variants",
                "Monitor trending topics for relevant content",
                "Engage with audience comments and messages"
            ]
            
            report = {
                "report_date": datetime.now().isoformat(),
                "date_range": platform_data.get("date_range", {}),
                "summary": {
                    "total_posts": total_posts,
                    "platforms_used": len(platform_data.get("platform_stats", {})),
                    "total_engagement": sum(
                        stats["total_engagement"] 
                        for stats in platform_data.get("platform_stats", {}).values()
                    )
                },
                "platform_performance": platform_data.get("platform_stats", {}),
                "workflow_performance": workflow_analytics.get("data", {}),
                "insights": insights,
                "recommendations": recommendations
            }
            
            logger.info("Performance report generated successfully")
            
            return {
                "success": True,
                "data": report,
                "message": "Performance report generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate performance report"
            }
    
    def get_content_suggestions(self, platform: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Get content suggestions based on analytics
        
        Args:
            platform: Target platform
            topic: Optional topic filter
            
        Returns:
            Content suggestions
        """
        try:
            # Get recent analytics for the platform
            platform_analytics = self.get_platform_analytics(
                platform=platform,
                limit=50
            )
            
            if not platform_analytics["success"]:
                raise Exception("Failed to get platform analytics")
            
            # Analyze successful content patterns
            successful_content = []
            for entry in platform_analytics["data"]["raw_data"]:
                metrics = entry.get("metrics", {})
                engagement = metrics.get("engagement", 0)
                
                if engagement > 50:  # High engagement threshold
                    successful_content.append({
                        "content_id": entry.get("content_id"),
                        "engagement": engagement,
                        "timestamp": entry.get("timestamp")
                    })
            
            # Generate suggestions based on successful patterns
            suggestions = []
            
            if successful_content:
                avg_engagement = sum(c["engagement"] for c in successful_content) / len(successful_content)
                
                suggestions = [
                    f"Content similar to your top performers (avg {avg_engagement:.0f} engagement)",
                    "Use engaging questions to drive interaction",
                    "Include relevant hashtags for better discovery",
                    "Post during peak engagement hours",
                    "Use visual content when possible"
                ]
            else:
                suggestions = [
                    "Start with engaging questions to drive interaction",
                    "Use trending hashtags relevant to your topic",
                    "Post consistently to build audience engagement",
                    "Share valuable insights and tips",
                    "Use visual content to increase engagement"
                ]
            
            logger.info(f"Generated {len(suggestions)} content suggestions for {platform}")
            
            return {
                "success": True,
                "data": {
                    "platform": platform,
                    "topic": topic,
                    "suggestions": suggestions,
                    "successful_content_count": len(successful_content)
                },
                "message": "Content suggestions generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get content suggestions: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate content suggestions"
            }
    
    def cleanup_old_analytics(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Clean up old analytics data
        
        Args:
            days_to_keep: Number of days to keep data
            
        Returns:
            Cleanup results
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_files = 0
            
            for analytics_file in self.analytics_data_dir.glob("analytics_*.jsonl"):
                try:
                    # Extract date from filename
                    date_str = analytics_file.stem.replace("analytics_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    if file_date < cutoff_date:
                        analytics_file.unlink()
                        deleted_files += 1
                        
                except (ValueError, OSError) as e:
                    logger.warning(f"Could not process file {analytics_file}: {e}")
            
            logger.info(f"Cleaned up {deleted_files} old analytics files")
            
            return {
                "success": True,
                "data": {
                    "deleted_files": deleted_files,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_to_keep": days_to_keep
                },
                "message": "Analytics cleanup completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to cleanup old analytics data"
            }