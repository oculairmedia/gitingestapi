import os
from urllib import request, parse
import json
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gitingest(
    url: str,
    request_heartbeat: bool = False,
    max_file_size: int = 243,
    pattern_type: str = "exclude",
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> str:
    """Analyze and ingest a GitHub repository using the gitingest API.

    Args:
        url: The GitHub repository URL to analyze
        request_heartbeat: Request an immediate heartbeat after function execution (required for Letta)
        max_file_size: Maximum file size to process in KB
        pattern_type: Type of pattern matching to use (exclude or include)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds (will double each retry)

    Returns:
        str: Formatted analysis results or error message
    """
    # Get configuration from environment variables
    gitingest_url = os.getenv("GITINGEST_URL", "http://192.168.50.90:8082")
    
    # Construct API URL with parameters
    params = {
        "url": url,
        "max_file_size": max_file_size,
        "pattern_type": pattern_type
    }
    api_url = f"{gitingest_url}/api/v1/ingest?{parse.urlencode(params)}"
    
    headers = {
        "accept": "application/json"
    }
    
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            req = request.Request(api_url, headers=headers)
            with request.urlopen(req) as response:
                # Check response status
                if response.status != 200:
                    error_msg = f"Repository analysis failed: HTTP {response.status}"
                    logger.error(error_msg)
                    return error_msg
                
                # Read and decode response
                raw_data = response.read().decode('utf-8')
                
                # Verify response is not empty
                if not raw_data:
                    error_msg = "Repository analysis failed: Empty response from server"
                    logger.error(error_msg)
                    return error_msg
                
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError as e:
                    error_msg = f"Repository analysis failed: Invalid JSON response: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
                
                # Format the response
                output = []
                
                # Add summary section
                if "summary" in data:
                    output.append("# Repository Analysis Summary")
                    output.append(data["summary"])
                    output.append("")
                
                # Add directory tree section
                if "tree" in data:
                    output.append("# Repository Structure")
                    output.append("```")
                    output.append(data["tree"])
                    output.append("```")
                    output.append("")
                
                # Add content section if available
                if "content" in data:
                    output.append("# File Contents")
                    output.append("Key files analyzed from the repository:")
                    output.append("```")
                    output.append(data["content"])
                    output.append("```")
                
                return "\n".join(output)

        except Exception as e:
            logger.error(f"Analysis attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            return f"Repository analysis failed after multiple attempts: {str(e)}"
    
    return "Repository analysis failed after maximum retries"