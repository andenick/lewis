#!/usr/bin/env python3
"""
Enhanced API Pipeline for Lewis International Economics Platform.
Provides robust error handling, retry mechanisms, parallel processing, and comprehensive logging.
"""

import asyncio
import aiohttp
import requests
import logging
from typing import Dict, List, Optional, Any, Callable, Union, AsyncGenerator
from datetime import datetime, timedelta
import json
import time
import hashlib
import pickle
from pathlib import Path
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import threading
from functools import wraps
# Optional dependencies - these will be imported with try/except
backoff = None
tenacity = None
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API pipeline."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    timeout: int = 30
    max_concurrent_requests: int = 10
    max_workers: int = 4
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    rate_limit_delay: float = 0.1
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    enable_compression: bool = True

@dataclass
class APIResponse:
    """Container for API response data."""
    success: bool
    data: Any
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    cached: bool = False
    retry_count: int = 0

@dataclass
class APIRequest:
    """Container for API request data."""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Union[Dict, str, bytes]] = None
    json_data: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    callback: Optional[Callable] = None
    retry_on_failure: bool = True
    cache_key: Optional[str] = None

class CircuitBreaker:
    """Circuit breaker for API endpoints."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == 'OPEN':
                if (datetime.now() - self.last_failure_time).total_seconds() > self.timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            self.failure_count = 0
            self.state = 'CLOSED'

    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'

class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.last_call = 0
        self._lock = threading.Lock()

    def wait(self):
        """Wait if necessary to respect rate limit."""
        with self._lock:
            elapsed = time.time() - self.last_call
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
            self.last_call = time.time()

class MemoryCache:
    """In-memory cache for API responses."""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached item."""
        with self._lock:
            if key in self.cache:
                item, timestamp = self.cache[key]
                if (datetime.now() - timestamp).total_seconds() < self.ttl:
                    return item
                else:
                    del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set cached item."""
        with self._lock:
            self.cache[key] = (value, datetime.now())

    def clear(self):
        """Clear cache."""
        with self._lock:
            self.cache.clear()

class EnhancedAPIPipeline:
    """
    Enhanced API pipeline with error handling, retry mechanisms, and parallel processing.
    Supports both synchronous and asynchronous operations.
    """

    def __init__(self, config: APIConfig):
        """Initialize the enhanced API pipeline."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Lewis-Platform/1.0',
            'Accept-Encoding': 'gzip, deflate' if config.enable_compression else 'identity'
        })

        # Initialize components
        self.circuit_breakers = {}
        self.rate_limiter = RateLimiter(config.rate_limit_delay)
        self.cache = MemoryCache(config.cache_ttl) if config.enable_caching else None
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max(2, config.max_workers // 2))

        # Performance tracking
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'total_time': 0.0,
            'retries': 0
        }
        self._stats_lock = threading.Lock()

        logger.info(f"Enhanced API Pipeline initialized with {config.max_workers} workers")

    def _get_circuit_breaker(self, url: str) -> CircuitBreaker:
        """Get or create circuit breaker for URL."""
        key = hashlib.md5(url.encode()).hexdigest()
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker(
                self.config.circuit_breaker_threshold,
                self.config.circuit_breaker_timeout
            )
        return self.circuit_breakers[key]

    def _update_stats(self, success: bool, execution_time: float, cached: bool = False, retries: int = 0):
        """Update performance statistics."""
        with self._stats_lock:
            self.request_stats['total_requests'] += 1
            self.request_stats['total_time'] += execution_time
            self.request_stats['retries'] += retries

            if success:
                self.request_stats['successful_requests'] += 1
                if cached:
                    self.request_stats['cache_hits'] += 1
            else:
                self.request_stats['failed_requests'] += 1

    def _make_request_sync(self, request: APIRequest) -> APIResponse:
        """Make synchronous API request with error handling and retries."""
        start_time = time.time()
        retry_count = 0
        last_exception = None

        # Check cache first
        if self.cache and request.cache_key:
            cached_result = self.cache.get(request.cache_key)
            if cached_result:
                execution_time = time.time() - start_time
                self._update_stats(True, execution_time, cached=True)
                return APIResponse(
                    success=True,
                    data=cached_result,
                    cached=True,
                    execution_time=execution_time
                )

        # Define retry logic manually
        def _execute_request():
            """Execute the actual request."""
            self.rate_limiter.wait()

            kwargs = {
                'method': request.method,
                'url': request.url,
                'headers': request.headers,
                'params': request.params,
                'timeout': request.timeout or self.config.timeout
            }

            if request.json_data:
                kwargs['json'] = request.json_data
            elif request.data:
                kwargs['data'] = request.data

            response = self.session.request(**kwargs)

            if response.status_code >= 400:
                raise requests.HTTPError(f"HTTP {response.status_code}: {response.reason}")

            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text

            return data

        # Execute request with retry logic and circuit breaker
        circuit_breaker = self._get_circuit_breaker(request.url)
        last_exception = None

        try:
            if request.retry_on_failure:
                # Manual retry with exponential backoff
                for attempt in range(self.config.max_retries + 1):
                    try:
                        result = circuit_breaker.call(_execute_request)
                        break  # Success
                    except Exception as e:
                        last_exception = e
                        if attempt < self.config.max_retries:
                            delay = min(self.config.base_delay * (2 ** attempt), self.config.max_delay)
                            time.sleep(delay)
                            logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}")
                            retry_count += 1
                        else:
                            raise e
            else:
                result = _execute_request()

            # Cache result if successful and caching enabled
            if self.cache and request.cache_key and request.method.upper() == 'GET':
                self.cache.set(request.cache_key, result)

            execution_time = time.time() - start_time
            self._update_stats(True, execution_time, retries=retry_count)

            return APIResponse(
                success=True,
                data=result,
                status_code=200,
                execution_time=execution_time,
                retry_count=retry_count
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self._update_stats(False, execution_time, retries=retry_count)

            return APIResponse(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                retry_count=retry_count
            )

    async def _make_request_async(self, session: aiohttp.ClientSession, request: APIRequest) -> APIResponse:
        """Make asynchronous API request with error handling and retries."""
        start_time = time.time()
        retry_count = 0

        # Check cache first
        if self.cache and request.cache_key:
            cached_result = self.cache.get(request.cache_key)
            if cached_result:
                execution_time = time.time() - start_time
                self._update_stats(True, execution_time, cached=True)
                return APIResponse(
                    success=True,
                    data=cached_result,
                    cached=True,
                    execution_time=execution_time
                )

        # Prepare request parameters
        kwargs = {
            'method': request.method.upper(),
            'url': request.url,
            'headers': request.headers,
            'params': request.params,
            'timeout': aiohttp.ClientTimeout(total=request.timeout or self.config.timeout)
        }

        if request.json_data:
            kwargs['json'] = request.json_data
        elif request.data:
            kwargs['data'] = request.data

        # Implement retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                self.rate_limiter.wait()

                async with session.request(**kwargs) as response:
                    if response.status >= 400:
                        raise aiohttp.ClientResponseError(f"HTTP {response.status}: {response.reason}")

                    try:
                        data = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        data = await response.text()

                    # Cache result if successful
                    if self.cache and request.cache_key and request.method.upper() == 'GET':
                        self.cache.set(request.cache_key, data)

                    execution_time = time.time() - start_time
                    self._update_stats(True, execution_time, retries=retry_count)

                    return APIResponse(
                        success=True,
                        data=data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        execution_time=execution_time,
                        retry_count=retry_count
                    )

            except Exception as e:
                retry_count += 1
                if attempt < self.config.max_retries:
                    delay = min(self.config.base_delay * (2 ** attempt), self.config.max_delay)
                    await asyncio.sleep(delay)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}")
                else:
                    execution_time = time.time() - start_time
                    self._update_stats(False, execution_time, retries=retry_count)

                    return APIResponse(
                        success=False,
                        data=None,
                        error_message=str(e),
                        execution_time=execution_time,
                        retry_count=retry_count
                    )

    def make_request(self, request: APIRequest) -> APIResponse:
        """Make synchronous API request."""
        return self._make_request_sync(request)

    async def make_request_async(self, request: APIRequest) -> APIResponse:
        """Make asynchronous API request."""
        async with aiohttp.ClientSession() as session:
            return await self._make_request_async(session, request)

    def make_batch_requests(self, requests: List[APIRequest]) -> List[APIResponse]:
        """Make multiple API requests in parallel (synchronous)."""
        if len(requests) > self.config.max_concurrent_requests:
            logger.warning(f"Batch size ({len(requests)}) exceeds max concurrent requests ({self.config.max_concurrent_requests})")

        futures = []
        for request in requests[:self.config.max_concurrent_requests]:
            future = self.executor.submit(self._make_request_sync, request)
            futures.append(future)

        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)

                # Execute callback if provided
                if result.success and request.callback:
                    try:
                        request.callback(result.data)
                    except Exception as e:
                        logger.error(f"Callback execution failed: {e}")

            except Exception as e:
                logger.error(f"Batch request failed: {e}")
                results.append(APIResponse(
                    success=False,
                    data=None,
                    error_message=str(e)
                ))

        return results

    async def make_batch_requests_async(self, requests: List[APIRequest]) -> List[APIResponse]:
        """Make multiple API requests in parallel (asynchronous)."""
        if len(requests) > self.config.max_concurrent_requests:
            logger.warning(f"Batch size ({len(requests)}) exceeds max concurrent requests ({self.config.max_concurrent_requests})")

        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_requests)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for request in requests[:self.config.max_concurrent_requests]:
                task = asyncio.create_task(self._make_request_async(session, request))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(APIResponse(
                        success=False,
                        data=None,
                        error_message=str(result)
                    ))
                else:
                    processed_results.append(result)

            return processed_results

    def process_data_parallel(self, data_items: List[Any],
                            processor_func: Callable[[Any], Any],
                            use_processes: bool = False) -> List[Any]:
        """Process data items in parallel using threads or processes."""
        if not data_items:
            return []

        executor = self.process_executor if use_processes else self.executor

        futures = []
        for item in data_items:
            future = executor.submit(processor_func, item)
            futures.append(future)

        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Data processing failed: {e}")
                results.append(None)

        return results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._stats_lock:
            stats = self.request_stats.copy()

        if stats['total_requests'] > 0:
            stats.update({
                'success_rate': stats['successful_requests'] / stats['total_requests'],
                'failure_rate': stats['failed_requests'] / stats['total_requests'],
                'cache_hit_rate': stats['cache_hits'] / stats['total_requests'],
                'average_response_time': stats['total_time'] / stats['total_requests'],
                'average_retries': stats['retries'] / stats['total_requests']
            })
        else:
            stats.update({
                'success_rate': 0.0,
                'failure_rate': 0.0,
                'cache_hit_rate': 0.0,
                'average_response_time': 0.0,
                'average_retries': 0.0
            })

        # Add circuit breaker status
        stats['circuit_breakers'] = {
            'total': len(self.circuit_breakers),
            'open': sum(1 for cb in self.circuit_breakers.values() if cb.state == 'OPEN'),
            'closed': sum(1 for cb in self.circuit_breakers.values() if cb.state == 'CLOSED'),
            'half_open': sum(1 for cb in self.circuit_breakers.values() if cb.state == 'HALF_OPEN')
        }

        # Add cache status
        if self.cache:
            stats['cache'] = {
                'size': len(self.cache.cache),
                'ttl': self.cache.ttl
            }

        return stats

    def clear_cache(self):
        """Clear the response cache."""
        if self.cache:
            self.cache.clear()
            logger.info("API response cache cleared")

    def reset_stats(self):
        """Reset performance statistics."""
        with self._stats_lock:
            self.request_stats = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'cache_hits': 0,
                'total_time': 0.0,
                'retries': 0
            }
        logger.info("Performance statistics reset")

    def close(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        self.session.close()
        logger.info("Enhanced API Pipeline closed")

# Convenience functions for common API operations
def create_get_request(url: str, params: Dict[str, Any] = None,
                       cache_key: str = None, **kwargs) -> APIRequest:
    """Create GET request."""
    return APIRequest(
        method='GET',
        url=url,
        params=params,
        cache_key=cache_key,
        **kwargs
    )

def create_post_request(url: str, data: Dict[str, Any] = None,
                        json_data: Dict[str, Any] = None, **kwargs) -> APIRequest:
    """Create POST request."""
    return APIRequest(
        method='POST',
        url=url,
        data=data,
        json_data=json_data,
        **kwargs
    )

def create_put_request(url: str, data: Dict[str, Any] = None,
                      json_data: Dict[str, Any] = None, **kwargs) -> APIRequest:
    """Create PUT request."""
    return APIRequest(
        method='PUT',
        url=url,
        data=data,
        json_data=json_data,
        **kwargs
    )

def create_delete_request(url: str, **kwargs) -> APIRequest:
    """Create DELETE request."""
    return APIRequest(
        method='DELETE',
        url=url,
        **kwargs
    )

# Decorator for API endpoint functions
def api_endpoint(max_retries: int = 3, cache_ttl: int = 3600):
    """Decorator for API endpoint functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Implementation would depend on how the decorator is used
            # This is a placeholder for the decorator pattern
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def main():
    """Main function for testing the enhanced API pipeline."""
    print("=== Enhanced API Pipeline Test ===")
    print()

    # Initialize API pipeline
    config = APIConfig(
        max_retries=3,
        max_concurrent_requests=5,
        max_workers=3,
        enable_caching=True,
        cache_ttl=300  # 5 minutes
    )

    api = EnhancedAPIPipeline(config)

    try:
        # Test single request
        print("1. Testing single request...")
        request = create_get_request(
            "https://httpbin.org/get",
            params={"test": "single_request"},
            cache_key="test_single"
        )

        response = api.make_request(request)
        if response.success:
            print(f"SUCCESS: Single request completed in {response.execution_time:.3f}s")
            print(f"  Status code: {response.status_code}")
            print(f"  Cached: {response.cached}")
        else:
            print(f"ERROR: Single request failed: {response.error_message}")

        # Test batch requests
        print("\n2. Testing batch requests...")
        requests = []
        for i in range(5):
            request = create_get_request(
                f"https://httpbin.org/get",
                params={"test": f"batch_request_{i}", "id": i},
                cache_key=f"test_batch_{i}"
            )
            requests.append(request)

        batch_responses = api.make_batch_requests(requests)
        successful = sum(1 for r in batch_responses if r.success)
        print(f"SUCCESS: Batch requests completed - {successful}/{len(requests)} successful")
        if batch_responses:
            avg_time = sum(r.execution_time for r in batch_responses) / len(batch_responses)
            print(f"  Average response time: {avg_time:.3f}s")

        # Test caching
        print("\n3. Testing caching system...")
        cached_request = create_get_request(
            "https://httpbin.org/get",
            params={"test": "cache_test"},
            cache_key="test_cache"
        )

        # First request (not cached)
        start_time = time.time()
        response1 = api.make_request(cached_request)
        first_time = time.time() - start_time

        # Second request (should be cached)
        start_time = time.time()
        response2 = api.make_request(cached_request)
        second_time = time.time() - start_time

        if response1.success and response2.success and response2.cached:
            print(f"SUCCESS: Caching system working")
            print(f"  First request: {first_time:.3f}s")
            print(f"  Second request: {second_time:.3f}s (cached)")
            print(f"  Speedup: {first_time/second_time:.1f}x")
        else:
            print("ERROR: Caching system not working properly")

        # Test performance stats
        print("\n4. Testing performance statistics...")
        stats = api.get_performance_stats()
        print("SUCCESS: Performance statistics available")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Success rate: {stats['success_rate']:.2%}")
        print(f"  Cache hit rate: {stats['cache_hit_rate']:.2%}")
        print(f"  Average response time: {stats['average_response_time']:.3f}s")
        print(f"  Circuit breakers: {stats['circuit_breakers']['total']} total")

        print(f"\n*** ENHANCED API PIPELINE TEST COMPLETED SUCCESSFULLY! ***")

    except Exception as e:
        print(f"API pipeline test failed: {e}")
        raise

    finally:
        api.close()

if __name__ == "__main__":
    main()