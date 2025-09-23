import time
import functools
import inspect
from prometheus_client import Counter, Histogram

REQUEST_LATENCY = Histogram('request_latency_seconds','Latency of HTTP requests in seconds',['method','endpoint'],buckets=(0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2,5))

PREDICTIONS_TOTAL = Counter('predictions_total','Total predictions served',['status'])

PREDICTION_ERRORS_TOTAL = Counter('prediction_errors_total','Total prediction errors')

def timed(method, endpoint):
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return await func(*args, **kwargs)
                finally:
                    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.perf_counter()-start)
            async_wrapper.__signature__ = inspect.signature(func)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.perf_counter()-start)
            sync_wrapper.__signature__ = inspect.signature(func)
            return sync_wrapper
    return decorator
