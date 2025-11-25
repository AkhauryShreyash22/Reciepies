from django.http import JsonResponse
from django.core.cache import cache
import time

class RateLimitAndThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.daily_limit = 100
        self.window_seconds = 86400
        self.throttle_rules = {
            'default': {'limit': 60, 'window': 60},
            'sensitive': {'limit': 10, 'window': 60},
            'burst': {'limit': 30, 'window': 10},
        }

    def __call__(self, request):
        if self.should_skip(request):
            return self.get_response(request)

        user_id = self.get_user_identifier(request)
        
        throttle_response = self.check_throttling(request, user_id)
        if throttle_response:
            return throttle_response
        
        rate_limit_response = self.check_rate_limiting(user_id)
        if rate_limit_response:
            return rate_limit_response
        
        return self.get_response(request)

    def check_throttling(self, request, user_id):
        throttle_rule_name = self.get_throttle_rule_name(request)
        throttle_rule = self.throttle_rules[throttle_rule_name]
        cache_key = f"throttle{throttle_rule_name}{user_id}"
        
        current_count = self.get_throttle_count(cache_key, throttle_rule['window'])
        
        if current_count >= throttle_rule['limit']:
            return self.throttle_response(throttle_rule)
        
        self.increment_throttle_count(cache_key, throttle_rule['window'])
        return None

    def check_rate_limiting(self, user_id):
        cache_key = f"ratelimit{user_id}"
        current_count = self.get_request_count(cache_key)
        
        if current_count >= self.daily_limit:
            return self.rate_limit_response()
        
        self.increment_request_count(cache_key)
        return None

    def get_throttle_rule_name(self, request):
        path = request.path
        
        if any(path.endswith(endpoint) for endpoint in ['/login/', '/register/', '/password-reset/']):
            return 'sensitive'
        
        burst_key = f"burst{self.get_user_identifier(request)}"
        burst_count = self.get_throttle_count(burst_key, 10)
        
        if burst_count >= 30:
            return 'burst'
        
        self.increment_throttle_count(burst_key, 10)
        return 'default'

    def get_throttle_count(self, cache_key, window):
        data = cache.get(cache_key)
        if data:
            count, timestamp = data
            if time.time() - timestamp > window:
                return 0
            return count
        return 0

    def increment_throttle_count(self, cache_key, window):
        data = cache.get(cache_key)
        current_time = time.time()
        
        if data:
            count, timestamp = data
            if current_time - timestamp > window:
                count = 1
            else:
                count += 1
        else:
            count = 1
        
        cache.set(cache_key, (count, current_time), window)

    def throttle_response(self, throttle_rule):
        window_readable = self.get_window_readable(throttle_rule['window'])
        return JsonResponse({
            "error": "throttled",
            "message": "Request rate too high",
            "detail": f"Too many requests. Maximum {throttle_rule['limit']} requests per {window_readable}",
            "limit": throttle_rule['limit'],
            "window": window_readable
        }, status=429)

    def get_window_readable(self, seconds):
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        else:
            return f"{seconds // 3600} hours"

    def should_skip(self, request):
        skip_paths = [
            '/admin/', '/static/', '/media/',
            '/swagger/', '/redoc/', '/api/schema/',
            '/health/', '/favicon.ico'
        ]
        path = request.path
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def get_user_identifier(self, request):
        if request.user.is_authenticated:
            return f"user{request.user.id}"
        else:
            return f"ip{self.get_client_ip(request)}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def get_request_count(self, cache_key):
        data = cache.get(cache_key)
        if data:
            count, timestamp = data
            if time.time() - timestamp > self.window_seconds:
                return 0
            return count
        return 0

    def increment_request_count(self, cache_key):
        data = cache.get(cache_key)
        current_time = time.time()
        
        if data:
            count, timestamp = data
            if current_time - timestamp > self.window_seconds:
                count = 1
            else:
                count += 1
        else:
            count = 1
        
        cache.set(cache_key, (count, current_time), self.window_seconds)

    def rate_limit_response(self):
        return JsonResponse({
            "error": "rate_limit_exceeded",
            "message": "Daily request limit exceeded",
            "detail": f"You have exceeded the daily limit of {self.daily_limit} requests.",
            "limit": self.daily_limit,
            "window": "24 hours"
        }, status=429)