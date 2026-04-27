import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from app.core.logger import request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details."""
        request_id = self.generate_request_id()
        request.state.request_id = request_id
        
        start_time = time.time()
        
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_string = request.url.query
        
        request_logger.info(
            f"[{request_id}] {method} {path} "
            f"from {client_host}:{client_port} "
            f"{'?' + query_string if query_string else ''}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            status_code = response.status_code
            
            log_level = "info"
            if status_code >= 500:
                log_level = "error"
            elif status_code >= 400:
                log_level = "warning"
            
            log_message = (
                f"[{request_id}] {method} {path} "
                f"completed with status {status_code} "
                f"in {process_time:.3f}s"
            )
            
            if log_level == "error":
                request_logger.error(log_message)
            elif log_level == "warning":
                request_logger.warning(log_message)
            else:
                request_logger.info(log_message)
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        except Exception as e:
            import traceback
            process_time = time.time() - start_time

            request_logger.error(
                f"[{request_id}] {method} {path} "
                f"failed with exception after {process_time:.3f}s: {str(e)}\n"
                f"{traceback.format_exc()}"
            )

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
                headers={"X-Request-ID": request_id},
            )
    
    @staticmethod
    def generate_request_id():
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]
