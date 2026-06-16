"""Per-plan rate limiting via slowapi."""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by IP; swap to user-id key func in production for per-user limits
limiter = Limiter(key_func=get_remote_address)

# Plan limits — used in route decorators as strings
PLAN_LIMITS = {
    "free":       "50/day",
    "starter":    "500/day",
    "pro":        "5000/day",
    "enterprise": "100000/day",
}
