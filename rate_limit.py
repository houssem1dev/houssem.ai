"""
Houssem AI - Redis-backed persistent rate limiter.
Falls back to in-memory if Redis unavailable (graceful degradation).
"""

import time
import logging
from typing import Tuple, Dict, List
from collections import defaultdict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
LIMITS = {
    "minute": (15, 60),      # 15 requests / 60 seconds
    "hour":   (200, 3600),   # 200 requests / 3600 seconds
    "day":    (1500, 86400), # 1500 requests / day
}


class RedisRateLimiter:
    """Sliding-window rate limiter backed by Redis sorted sets."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.client = None
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                self.client.ping()
                logger.info("✅ Redis rate limiter connected")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, falling back to memory: {e}")
                self.client = None

        # In-memory fallback
        self._memory: Dict[str, List[float]] = defaultdict(list)

    # ---------- Public API ----------
    def check(self, key: str) -> Tuple[bool, str]:
        """Return (allowed, reason). Records the request if allowed."""
        if self.client:
            return self._check_redis(key)
        return self._check_memory(key)

    def get_usage(self, key: str) -> Dict[str, int]:
        """Return current usage counts (for UI display)."""
        now = time.time()
        usage = {}
        for window_name, (_limit, seconds) in LIMITS.items():
            if self.client:
                rkey = f"rl:{key}:{window_name}"
                self.client.zremrangebyscore(rkey, 0, now - seconds)
                usage[window_name] = self.client.zcard(rkey)
            else:
                cutoff = now - seconds
                usage[window_name] = len(
                    [t for t in self._memory[key] if t > cutoff]
                )
        return usage

    # ---------- Redis backend ----------
    def _check_redis(self, key: str) -> Tuple[bool, str]:
        now = time.time()
        pipe = self.client.pipeline()

        for window_name, (limit, seconds) in LIMITS.items():
            rkey = f"rl:{key}:{window_name}"
            # Prune + count + add in a pipeline (atomic-ish)
            pipe.zremrangebyscore(rkey, 0, now - seconds)
            pipe.zcard(rkey)

        results = pipe.execute()

        # results = [prune_count, card_count, ...] pairs
        for i, (window_name, (limit, seconds)) in enumerate(LIMITS.items()):
            count = results[i * 2 + 1]
            if count >= limit:
                wait = seconds - int(now - now % seconds) if seconds < 60 else 60
                return False, (
                    f"⏳ تجاوزت الحد ({limit} طلب / {self._pretty(seconds)}). "
                    f"حاول لاحقاً."
                )

        # Allowed — record request
        pipe = self.client.pipeline()
        unique_id = f"{now}:{id(key)}"
        for window_name, (_limit, seconds) in LIMITS.items():
            rkey = f"rl:{key}:{window_name}"
            pipe.zadd(rkey, {unique_id: now})
            pipe.expire(rkey, seconds + 5)
        pipe.execute()

        return True, ""

    # ---------- Memory fallback ----------
    def _check_memory(self, key: str) -> Tuple[bool, str]:
        now = time.time()
        for window_name, (limit, seconds) in LIMITS.items():
            cutoff = now - seconds
            self._memory[key] = [t for t in self._memory[key] if t > cutoff]
            if len(self._memory[key]) >= limit:
                return False, (
                    f"⏳ تجاوزت الحد ({limit} طلب / {self._pretty(seconds)}). "
                    f"حاول لاحقاً."
                )
        self._memory[key].append(now)
        return True, ""

    @staticmethod
    def _pretty(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} ثانية"
        if seconds < 3600:
            return f"{seconds // 60} دقيقة"
        return f"{seconds // 3600} ساعة"
