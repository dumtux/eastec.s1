from .auth import check_token


def test_check_token():
    assert check_token('invalid-token-string') is False
