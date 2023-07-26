import os

from basewordle import decode, encode


def _bytes(_bytes):
    return " ".join([f"{b:0>8_b}" for b in _bytes])


def test_simple_roundtrip():
    assert decode(encode(b"012345678")) == b"012345678"


def test_properly_encoded_with_overflow_roundtrips():
    the_bytes = decode("AgentBreadCauseGuard")
    print(_bytes(the_bytes))
    assert encode(the_bytes) == "AgentBreadCauseGuard"


def test_improperly_encoded_with_overflow_decodes_to_correct_bytes(caplog):
    the_bytes = decode("AgentBreadCauseHandy")
    assert "Ignoring 4 bits of nonzero overflow: " in caplog.text
    print(_bytes(the_bytes))
    assert encode(the_bytes) == "AgentBreadCauseGuard"


def test_lots_of_random_bytes():
    for n in range(100):
        for i in range(10):
            the_bytes = os.urandom(n)
            assert len(the_bytes) == n
            assert isinstance(the_bytes, bytes)
            print("the_bytes", _bytes(the_bytes))

            encoded = encode(the_bytes)
            print("encoded", encoded)
            result_bytes = decode(encoded)
            print("result bytes", _bytes(result_bytes))
            assert result_bytes == the_bytes, (n, i, the_bytes)
