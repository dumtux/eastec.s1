from sone.auth import _verify_token


def test__verify_token():
    assert _verify_token('invalid-token-string') is False
