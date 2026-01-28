"""
Opus API client for workflow execution.
Handles all interactions with the Opus platform API.
"""

import time
from typing import Dict, Any, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.logger import logger


class OpusAPIError(Exception):
    """Custom exception for Opus API errors."""
    pass


class OpusClient:
    """Client for interacting with Opus API."""
    
    def __init__(self):
        """Initialize Opus API client."""
        self.base_url = settings.opus_base_url
        self.api_key = settings.opus_api_key
        self.workflow_id = settings.opus_workflow_id
        self.headers = {
            "x-service-key": self.api_key,
            "Content-Type": "application/json"
        }
        self._workflow_schema: Optional[Dict[str, Any]] = None
        logger.info("Opus client initialized", base_url=self.base_url, workflow_id=self.workflow_id)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Opus API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            OpusAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            
            # Handle empty responses
            if not response.content:
                return {}
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Try to get detailed error from response body
            error_detail = str(e)
            try:
                error_body = e.response.json()
                error_detail = error_body.get("message", error_body.get("error", str(e)))
                logger.error("Opus API HTTP error with details", 
                            method=method, 
                            endpoint=endpoint, 
                            status_code=e.response.status_code,
                            error=str(e),
                            error_body=error_body)
            except:
                logger.error("Opus API HTTP error", 
                            method=method, 
                            endpoint=endpoint, 
                            status_code=e.response.status_code,
                            error=str(e),
                            response_text=e.response.text[:500])
            raise OpusAPIError(f"HTTP {e.response.status_code}: {error_detail}")
        except requests.exceptions.RequestException as e:
            logger.error("Opus API request failed", method=method, endpoint=endpoint, error=str(e))
            raise OpusAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            logger.error("Failed to parse Opus API response", error=str(e))
            raise OpusAPIError(f"Invalid JSON response: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def get_workflow_schema(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get workflow details and input schema.
        Caches the schema for subsequent calls unless force_refresh is True.
        
        Args:
            force_refresh: Force refresh the cached schema
            
        Returns:
            Workflow schema including jobPayloadSchema
        """
        if self._workflow_schema is not None and not force_refresh:
            logger.debug("Using cached workflow schema")
            return self._workflow_schema
        
        logger.info("Fetching workflow schema", workflow_id=self.workflow_id)
        endpoint = f"/workflow/{self.workflow_id}"
        schema = self._make_request("GET", endpoint)
        
        self._workflow_schema = schema
        logger.info("Workflow schema retrieved and cached", 
                   workflow_name=schema.get("name", "Unknown"))
        return schema
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def initiate_job(self, title: str, description: str) -> str:
        """
        Initiate a new job execution.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            Job execution ID
        """
        logger.info("Initiating Opus job", title=title)
        endpoint = "/job/initiate"
        
        payload = {
            "workflowId": self.workflow_id,
            "title": title,
            "description": description
        }
        
        logger.debug("Initiate request payload", 
                    workflowId=self.workflow_id,
                    title=title,
                    description=description,
                    payload=payload)
        
        response = self._make_request("POST", endpoint, json=payload)
        job_execution_id = response.get("jobExecutionId")
        
        if not job_execution_id:
            raise OpusAPIError("No jobExecutionId in response")
        
        logger.info("Job initiated successfully", job_execution_id=job_execution_id)
        return job_execution_id
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def execute_job(self, job_execution_id: str, job_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a job with the provided payload.
        
        Args:
            job_execution_id: Job execution ID from initiate_job
            job_payload: Job payload schema instance with input values
            
        Returns:
            Execution response
        """
        logger.info("Executing Opus job", job_execution_id=job_execution_id)
        endpoint = "/job/execute"
        
        payload = {
            "jobExecutionId": job_execution_id,
            "jobPayloadSchemaInstance": job_payload
        }
        
        response = self._make_request("POST", endpoint, json=payload)
        
        if response.get("success"):
            logger.info("Job execution started", job_execution_id=job_execution_id)
        else:
            logger.warning("Job execution response unclear", 
                         job_execution_id=job_execution_id,
                         response=response)
        
        return response
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def get_job_status(self, job_execution_id: str) -> str:
        """
        Get current status of a job.
        
        Args:
            job_execution_id: Job execution ID
            
        Returns:
            Job status (IN PROGRESS, COMPLETED, FAILED)
        """
        endpoint = f"/job/{job_execution_id}/status"
        response = self._make_request("GET", endpoint)
        
        status = response.get("status", "UNKNOWN")
        logger.debug("Job status retrieved", job_execution_id=job_execution_id, status=status)
        return status
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def get_job_results(self, job_execution_id: str) -> Dict[str, Any]:
        """
        Get results of a completed job.
        
        Args:
            job_execution_id: Job execution ID
            
        Returns:
            Job results
        """
        logger.info("Fetching job results", job_execution_id=job_execution_id)
        endpoint = f"/job/{job_execution_id}/results"
        response = self._make_request("GET", endpoint)
        
        logger.info("Job results retrieved", job_execution_id=job_execution_id)
        return response
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpusAPIError)
    )
    def get_job_audit_log(self, job_execution_id: str) -> Dict[str, Any]:
        """
        Get audit log for a job execution.
        
        Args:
            job_execution_id: Job execution ID
            
        Returns:
            Audit trail data
        """
        logger.info("Fetching job audit log", job_execution_id=job_execution_id)
        endpoint = f"/job/{job_execution_id}/audit"
        response = self._make_request("GET", endpoint)
        
        logger.debug("Audit log retrieved", 
                    job_execution_id=job_execution_id,
                    entries_count=len(response.get("auditTrail", [])))
        return response
    
    def poll_job_until_complete(self, job_execution_id: str, 
                               max_wait_seconds: int = 300,
                               poll_interval_seconds: int = 5) -> str:
        """
        Poll job status until it's completed or failed.
        
        Args:
            job_execution_id: Job execution ID
            max_wait_seconds: Maximum time to wait in seconds
            poll_interval_seconds: Time between status checks in seconds
            
        Returns:
            Final job status
            
        Raises:
            OpusAPIError: If job fails or timeout occurs
        """
        logger.info("Polling job until complete", 
                   job_execution_id=job_execution_id,
                   max_wait_seconds=max_wait_seconds)
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_seconds:
                logger.error("Job polling timeout", 
                           job_execution_id=job_execution_id,
                           elapsed_seconds=elapsed)
                raise OpusAPIError(f"Job polling timeout after {elapsed:.0f} seconds")
            
            status = self.get_job_status(job_execution_id)
            
            if status == "COMPLETED":
                logger.info("Job completed successfully", 
                          job_execution_id=job_execution_id,
                          elapsed_seconds=elapsed)
                return status
            elif status == "FAILED":
                logger.error("Job failed", job_execution_id=job_execution_id)
                # Try to get audit log for debugging
                try:
                    audit_log = self.get_job_audit_log(job_execution_id)
                    logger.error("Job failure audit log", audit_trail=audit_log.get("auditTrail", []))
                except Exception as e:
                    logger.warning("Could not retrieve audit log", error=str(e))
                raise OpusAPIError(f"Job failed: {job_execution_id}")
            elif status == "IN PROGRESS":
                logger.debug("Job in progress, waiting...", 
                           job_execution_id=job_execution_id,
                           elapsed_seconds=elapsed)
                time.sleep(poll_interval_seconds)
            else:
                logger.warning("Unexpected job status", 
                             job_execution_id=job_execution_id,
                             status=status)
                time.sleep(poll_interval_seconds)
    
    def build_job_payload(self, scraped_data: Dict[str, Any], 
                         content_type: str,
                         target_audience: str) -> Dict[str, Any]:
        """
        Build job payload from scraped data according to workflow schema.
        Maps all available data to workflow input variables.
        
        Args:
            scraped_data: Scraped content data (should be a dict with 'content', 'title', 'url', etc.)
            content_type: Type of content to generate
            target_audience: Target audience for the content
            
        Returns:
            Job payload schema instance ready for execution
        """
        # Extract data from scraped_data
        content_text = scraped_data.get("content", "")
        article_title = scraped_data.get("title", "")
        article_url = scraped_data.get("url", "")
        keywords = scraped_data.get("keywords", [])
        content_source = scraped_data.get("source", "")
        published_at = scraped_data.get("published_at")
        
        # Handle null/empty published_at - convert to "N/A" or empty string
        # This prevents workflow input node failures when date is null
        if published_at is None or published_at == "":
            published_at = "N/A"  # Or use "" if workflow accepts empty string
        
        # Convert keywords list to comma-separated string
        keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
        
        if not content_text:
            logger.error("No content text found in scraped_data", 
                        scraped_data_keys=list(scraped_data.keys()) if isinstance(scraped_data, dict) else "not_dict")
            raise ValueError("No content text found in scraped_data")
        
        logger.info("Building payload with rich metadata", 
                   content_length=len(content_text),
                   title=article_title[:50],
                   source=content_source,
                   keywords_count=len(keywords) if isinstance(keywords, list) else 0)
        
        # Get workflow schema to find all variable names
        schema = self.get_workflow_schema()
        job_payload_schema = schema.get("jobPayloadSchema", {})
        
        logger.debug("Workflow schema variables", 
                    variable_count=len(job_payload_schema),
                    variables=list(job_payload_schema.keys()))
        
        # Build payload instance by matching variables
        payload_instance = {}
        
        # Mapping of data to potential variable name patterns
        # Order matters: more specific patterns first
        field_mappings = {
            'raw_ai_text': {
                'value': content_text,
                'patterns': ['raw_ai_text', 'raw ai text', 'raw_ai_industry', 'raw ai industry'],
                'exact_match': True  # Must match exactly
            },
            'article_title': {
                'value': article_title,
                'patterns': ['article_title', 'article title', 'article-title'],
                'exact_match': False
            },
            'article_url': {
                'value': article_url,
                'patterns': ['article_url', 'article url', 'article-url'],
                'exact_match': False
            },
            'keywords': {
                'value': keywords_str,
                'patterns': ['keywords', 'keyword'],
                'exact_match': False
            },
            'content_source': {
                'value': content_source,
                'patterns': ['content_source', 'content source', 'content-source'],
                'exact_match': False  # More specific pattern
            },
            'published_date': {
                'value': published_at,
                'patterns': ['published_date', 'published date', 'published-date', 'publish date'],
                'exact_match': False
            }
        }
        
        # Match each workflow variable to our data
        # Process in priority order to avoid conflicts
        for var_name, var_config in job_payload_schema.items():
            variable_name = var_config.get("variable_name", "")
            display_name = var_config.get("display_name", "").lower()
            var_type = var_config.get("type", "str")
            
            # Try to match this variable to one of our fields
            matched = False
            
            for field_key, field_data in field_mappings.items():
                # Skip if already matched (prevent double-mapping)
                if matched:
                    break
                
                for pattern in field_data['patterns']:
                    # Use more precise matching to avoid conflicts
                    # Check display_name first (most reliable)
                    display_match = pattern.lower() in display_name
                    
                    # For exact_match fields, be more strict
                    if field_data.get('exact_match', False):
                        # Must be exact match in display name or variable name
                        if (display_name == pattern or 
                            pattern in display_name and 'raw' in display_name):
                            payload_instance[var_name] = {
                                "value": field_data['value'],
                                "type": var_type
                            }
                            logger.info(f"Mapped {field_key} to workflow variable",
                                       var_name=var_name,
                                       display_name=var_config.get("display_name"),
                                       value_preview=str(field_data['value'])[:50])
                            matched = True
                            break
                    else:
                        # Regular matching for other fields
                        if display_match:
                            payload_instance[var_name] = {
                                "value": field_data['value'],
                                "type": var_type
                            }
                            logger.info(f"Mapped {field_key} to workflow variable",
                                       var_name=var_name,
                                       display_name=var_config.get("display_name"),
                                       value_preview=str(field_data['value'])[:50])
                            matched = True
                            break
            
            if not matched:
                logger.warning("Could not match workflow variable to data",
                             var_name=var_name,
                             display_name=display_name,
                             available_fields=list(field_mappings.keys()))
        
        # Verify we at least have the main content mapped
        if not any('raw_ai_text' in str(payload_instance.get(k, {})) or 
                   content_text in str(payload_instance.get(k, {}).get('value', '')) 
                   for k in payload_instance.keys()):
            logger.error("Main content (raw_ai_text) not mapped!",
                        mapped_variables=list(payload_instance.keys()))
            raise ValueError("Failed to map main content to workflow")
        
        logger.info("Final payload built", 
                   payload_keys=list(payload_instance.keys()),
                   total_variables=len(payload_instance))
        
        return payload_instance
    
    def run_complete_job_async(self, scraped_data: Dict[str, Any],
                              content_type: str,
                              title: str,
                              description: str) -> Dict[str, Any]:
        """
        Submit a job to Opus without waiting for completion (async mode).
        
        This method:
        1. Initiates a job
        2. Builds the payload from scraped data
        3. Executes the job
        4. Returns immediately (does NOT wait for completion)
        
        The job will remain in Opus for manual approval/completion.
        No timeout - jobs can be approved minutes, hours, or days later.
        
        Args:
            scraped_data: Processed content data dictionary
            content_type: Type of content (e.g., 'industry_news')
            title: Job title
            description: Job description
            
        Returns:
            Dictionary containing job execution ID and submission status
            
        Raises:
            OpusAPIError: If initiation or execution fails
        """
        logger.info("Starting async Opus job (no timeout)",
                   title=title,
                   content_type=content_type)
        
        try:
            # 1. Initiate job
            job_execution_id = self.initiate_job(title, description)
            
            # 2. Build payload
            job_payload = self.build_job_payload(
                scraped_data,
                content_type,
                target_audience="twitter"
            )
            
            # 3. Execute job
            self.execute_job(job_execution_id, job_payload)
            
            # Return immediately - don't wait for completion!
            logger.info("Job submitted successfully (async mode)",
                       job_execution_id=job_execution_id,
                       title=title,
                       message="Job queued in Opus for manual approval")
            
            return {
                "job_execution_id": job_execution_id,
                "status": "SUBMITTED",
                "message": "Job submitted to Opus. Will complete when manually approved.",
                "note": "No timeout - job can be approved anytime"
            }
            
        except Exception as e:
            logger.error("Failed to submit async job",
                       title=title,
                       error=str(e))
            raise OpusAPIError(f"Failed to submit async job: {e}")
    
    def run_complete_job(self, scraped_data: Dict[str, Any],
                        content_type: str,
                        title: str,
                        description: str) -> Dict[str, Any]:
        """
        Run a complete job from initiation to results retrieval.
        
        Args:
            scraped_data: Scraped content data
            content_type: Type of content to generate
            title: Job title
            description: Job description
            
        Returns:
            Job results
        """
        logger.info("Running complete Opus job", title=title, content_type=content_type)
        
        try:
            # 1. Initiate job
            job_execution_id = self.initiate_job(title, description)
            
            # 2. Build payload
            job_payload = self.build_job_payload(
                scraped_data,
                content_type,
                settings.target_audience
            )
            
            # 3. Execute job
            self.execute_job(job_execution_id, job_payload)
            
            # 4. Poll until complete
            final_status = self.poll_job_until_complete(job_execution_id)
            
            # 5. Get results
            if final_status == "COMPLETED":
                results = self.get_job_results(job_execution_id)
                logger.info("Complete job finished successfully", job_execution_id=job_execution_id)
                return {
                    "job_execution_id": job_execution_id,
                    "status": final_status,
                    "results": results
                }
            else:
                raise OpusAPIError(f"Job ended with status: {final_status}")
                
        except Exception as e:
            logger.error("Complete job failed", title=title, error=str(e))
            raise


# Global Opus client instance
opus_client = OpusClient()
