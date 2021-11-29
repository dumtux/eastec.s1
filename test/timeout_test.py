import time

from pytest import raises

from sone.timeout import timeout, TimeoutError


def test_timeout():
    @timeout(1)
    def slow_func():
        time.sleep(2)

    with raises(TimeoutError):
        slow_func()
