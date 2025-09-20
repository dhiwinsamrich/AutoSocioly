"""
Ngrok Manager - Handles making local files publicly accessible via ngrok
"""

import subprocess
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NgrokManager:
    """Manages ngrok tunnels for making images publicly accessible"""
    
    def __init__(self):
        """Initialize ngrok manager"""
        self.active_tunnels = {}  # Store active tunnels by file path
        self.ngrok_process = None
        logger.info("Ngrok manager initialized")
    
    def _check_ngrok_installed(self) -> bool:
        """Check if ngrok is installed and available"""
        try:
            result = subprocess.run(['ngrok', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Ngrok found: {result.stdout.strip()}")
                return True
            else:
                logger.warning("Ngrok not found or not working")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Ngrok check failed: {e}")
            return False
    
    def _start_ngrok_if_needed(self) -> bool:
        """Start ngrok if not already running"""
        try:
            # Check if ngrok is already running by checking its API
            result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.info("Ngrok is already running")
                return True
            else:
                logger.info("Starting ngrok...")
                # Start ngrok in background
                self.ngrok_process = subprocess.Popen(
                    ['ngrok', 'http', '8000', '--log=stdout'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(3)  # Give ngrok time to start
                return True
                
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            return False
    
    def create_public_url(self, file_path: str, custom_port: Optional[int] = None) -> Optional[str]:
        """
        Create a public URL for a local file using ngrok
        
        Args:
            file_path: Path to the local file
            custom_port: Optional custom port to use
            
        Returns:
            Public URL or None if failed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Check if we already have a tunnel for this file
            if str(file_path) in self.active_tunnels:
                existing_url = self.active_tunnels[str(file_path)]
                logger.info(f"Using existing tunnel for {file_path}: {existing_url}")
                return existing_url
            
            # Check if ngrok is available
            if not self._check_ngrok_installed():
                logger.warning("Ngrok not available, using local path fallback")
                return self._create_local_fallback_url(file_path)
            
            # Start ngrok if needed
            if not self._start_ngrok_if_needed():
                logger.warning("Failed to start ngrok, using local path fallback")
                return self._create_local_fallback_url(file_path)
            
            # Get ngrok tunnels
            try:
                result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], 
                                        capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    tunnels_data = json.loads(result.stdout)
                    
                    if tunnels_data.get('tunnels'):
                        # Use the first active tunnel
                        tunnel_url = tunnels_data['tunnels'][0]['public_url']
                        
                        # Create public URL for the specific file
                        file_name = file_path.name
                        public_url = f"{tunnel_url}/static/uploads/{file_name}"
                        
                        # Store the tunnel mapping
                        self.active_tunnels[str(file_path)] = public_url
                        
                        logger.info(f"Created public URL for {file_path}: {public_url}")
                        return public_url
                    else:
                        logger.warning("No active ngrok tunnels found")
                        return self._create_local_fallback_url(file_path)
                else:
                    logger.warning("Failed to get ngrok tunnels")
                    return self._create_local_fallback_url(file_path)
                    
            except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
                logger.error(f"Failed to get ngrok tunnels: {e}")
                return self._create_local_fallback_url(file_path)
                
        except Exception as e:
            logger.error(f"Failed to create public URL for {file_path}: {e}")
            return self._create_local_fallback_url(file_path)
    
    def _create_local_fallback_url(self, file_path: Path) -> str:
        """Create a fallback local URL for development"""
        try:
            # For development, create a local URL
            # This assumes the file is in a static directory
            file_name = file_path.name
            
            # Check if file is in static directory
            static_path = Path("static/images")
            if static_path.exists():
                target_path = static_path / file_name
                if not target_path.exists():
                    # Copy file to static directory if needed
                    import shutil
                    shutil.copy2(file_path, target_path)
                    logger.info(f"Copied {file_path} to static directory")
            
            local_url = f"http://localhost:8000/static/uploads/{file_name}"
            logger.info(f"Using local fallback URL: {local_url}")
            
            return local_url
            
        except Exception as e:
            logger.error(f"Failed to create local fallback URL: {e}")
            return str(file_path)  # Return original path as last resort
    
    def get_tunnel_info(self) -> Dict[str, Any]:
        """Get information about active tunnels"""
        try:
            result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                tunnels_data = json.loads(result.stdout)
                return {
                    "ngrok_running": True,
                    "tunnels_count": len(tunnels_data.get('tunnels', [])),
                    "tunnels": tunnels_data.get('tunnels', []),
                    "active_mappings": self.active_tunnels
                }
            else:
                return {
                    "ngrok_running": False,
                    "error": "Failed to connect to ngrok API",
                    "active_mappings": self.active_tunnels
                }
                
        except Exception as e:
            logger.error(f"Failed to get tunnel info: {e}")
            return {
                "ngrok_running": False,
                "error": str(e),
                "active_mappings": self.active_tunnels
            }
    
    def cleanup_tunnel(self, file_path: str) -> bool:
        """Clean up tunnel for a specific file"""
        try:
            if str(file_path) in self.active_tunnels:
                del self.active_tunnels[str(file_path)]
                logger.info(f"Cleaned up tunnel for {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup tunnel for {file_path}: {e}")
            return False
    
    def cleanup_all_tunnels(self):
        """Clean up all active tunnels"""
        try:
            self.active_tunnels.clear()
            logger.info("Cleaned up all tunnels")
            
            # Optionally stop ngrok process
            if self.ngrok_process:
                self.ngrok_process.terminate()
                self.ngrok_process = None
                logger.info("Stopped ngrok process")
                
        except Exception as e:
            logger.error(f"Failed to cleanup all tunnels: {e}")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.cleanup_all_tunnels()
        except:
            pass

# Global ngrok manager instance
ngrok_manager = NgrokManager()

def get_ngrok_manager() -> NgrokManager:
    """Get the global ngrok manager instance"""
    return ngrok_manager