import time
import pytest

from utils.rate_limiter import RateLimiter


def test_rate_limiter_allows_initial_requests():
    rate_limiter = RateLimiter(rate_limit_per_second=1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow the first request."


def test_rate_limiter_blocks_excessive_requests():
    rate_limiter = RateLimiter(rate_limit_per_second=1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow the first request."
    assert (
        rate_limiter.can_proceed() is False
    ), "Rate limiter should block the second request made too quickly."


def test_rate_limiter_allows_after_waiting():
    rate_limiter = RateLimiter(rate_limit_per_second=1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow the first request."
    time.sleep(1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow the second request after waiting."


def test_rate_limiter_wait_until_can_proceed():
    rate_limiter = RateLimiter(rate_limit_per_second=1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow the first request."
    assert (
        rate_limiter.can_proceed() is False
    ), "Rate limiter should block the second request processed too quickly."

    start_time = time.monotonic()
    rate_limiter.wait_until_can_proceed()
    end_time = time.monotonic()

    # The wait should be at least 1 second
    assert (
        end_time - start_time
    ) >= 1, "Rate limiter should wait for 1 second before allowing the next request."
    time.sleep(1)
    assert (
        rate_limiter.can_proceed() is True
    ), "Rate limiter should allow proceeding after waiting."
